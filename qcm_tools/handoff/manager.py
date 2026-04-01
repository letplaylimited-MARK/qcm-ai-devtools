"""
交接包管理器

提供交接包的存储、检索、验证和追溯功能
"""

import os
import json
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
from qcm_tools.handoff.models import HandoffPackage, SkillID


class HandoffManager:
    """
    交接包管理器
    
    功能：
    - 存储交接包（内存 + 文件持久化）
    - 按 Skill ID 检索交接包
    - 验证交接包格式
    - 追溯完整链路历史
    
    Example:
        >>> from qcm_tools.handoff import HandoffManager
        >>> 
        >>> # 初始化管理器
        >>> manager = HandoffManager(storage_path="./handoff_history")
        >>> 
        >>> # 存储交接包
        >>> handoff = HandoffPackage(
        ...     from_skill="skill-00",
        ...     to_skill="skill-03",
        ...     payload={'intent_type': 'find_open_source'}
        ... )
        >>> manager.save(handoff)
        >>> 
        >>> # 检索交接包
        >>> previous = manager.load("skill-00")
        >>> 
        >>> # 获取完整链路
        >>> chain = manager.get_chain()
    """
    
    def __init__(self, storage_path: str = None):
        """
        初始化交接包管理器
        
        Args:
            storage_path: 持久化存储路径（可选）
        """
        self._memory_store: Dict[str, List[HandoffPackage]] = {}
        self._storage_path = Path(storage_path) if storage_path else None
        
        # 确保存储目录存在
        if self._storage_path:
            self._storage_path.mkdir(parents=True, exist_ok=True)
    
    def save(
        self,
        handoff: HandoffPackage,
        session_id: str = "default",
        persist: bool = True
    ) -> str:
        """
        存储交接包
        
        Args:
            handoff: 交接包对象
            session_id: 会话 ID（用于区分不同工作流）
            persist: 是否持久化到文件
            
        Returns:
            交接包 ID
            
        Example:
            >>> manager = HandoffManager()
            >>> handoff = HandoffPackage(from_skill="skill-00", to_skill="skill-03")
            >>> handoff_id = manager.save(handoff)
        """
        # 验证交接包
        issues = handoff.validate()
        if issues:
            raise ValueError(f"交接包验证失败: {', '.join(issues)}")
        
        # 生成唯一 ID
        handoff_id = self._generate_id(handoff)
        
        # 存储到内存
        if session_id not in self._memory_store:
            self._memory_store[session_id] = []
        self._memory_store[session_id].append(handoff)
        
        # 持久化到文件
        if persist and self._storage_path:
            self._persist(handoff, session_id, handoff_id)
        
        return handoff_id
    
    def load(
        self,
        from_skill: str,
        session_id: str = "default"
    ) -> Optional[HandoffPackage]:
        """
        加载最新的交接包
        
        Args:
            from_skill: 来源 Skill ID
            session_id: 会话 ID
            
        Returns:
            最新的交接包，如果不存在则返回 None
            
        Example:
            >>> manager = HandoffManager()
            >>> previous = manager.load("skill-00")
        """
        if session_id not in self._memory_store:
            return None
        
        # 从后往前查找
        for handoff in reversed(self._memory_store[session_id]):
            if handoff.from_skill == from_skill:
                return handoff
        
        return None
    
    def load_by_to_skill(
        self,
        to_skill: str,
        session_id: str = "default"
    ) -> Optional[HandoffPackage]:
        """
        加载目标 Skill 的最新交接包
        
        Args:
            to_skill: 目标 Skill ID
            session_id: 会话 ID
            
        Returns:
            最新的交接包
        """
        if session_id not in self._memory_store:
            return None
        
        for handoff in reversed(self._memory_store[session_id]):
            if handoff.to_skill == to_skill:
                return handoff
        
        return None
    
    def get_chain(self, session_id: str = "default") -> List[HandoffPackage]:
        """
        获取完整的交接包链路
        
        Args:
            session_id: 会话 ID
            
        Returns:
            交接包列表（按时间顺序）
            
        Example:
            >>> manager = HandoffManager()
            >>> chain = manager.get_chain()
            >>> for handoff in chain:
            ...     print(f"{handoff.from_skill} → {handoff.to_skill}")
        """
        return self._memory_store.get(session_id, [])
    
    def get_chain_summary(self, session_id: str = "default") -> str:
        """
        获取链路摘要
        
        Args:
            session_id: 会话 ID
            
        Returns:
            人类可读的链路摘要
        """
        chain = self.get_chain(session_id)
        
        if not chain:
            return "📭 无交接包记录"
        
        lines = ["🔗 交接包链路:"]
        for i, handoff in enumerate(chain, 1):
            lines.append(f"  {i}. {handoff.from_skill} → {handoff.to_skill}")
            if handoff.handoff_type:
                lines.append(f"     类型: {handoff.handoff_type}")
        
        return "\n".join(lines)
    
    def clear(self, session_id: str = "default"):
        """
        清空指定会话的交接包
        
        Args:
            session_id: 会话 ID
        """
        if session_id in self._memory_store:
            del self._memory_store[session_id]
    
    def validate_chain(self, session_id: str = "default") -> List[Dict]:
        """
        验证链路完整性
        
        检查：
        - 相邻交接包的 to_skill 和 from_skill 是否匹配
        - 所有交接包是否有效
        
        Args:
            session_id: 会话 ID
            
        Returns:
            问题列表
        """
        chain = self.get_chain(session_id)
        issues = []
        
        for i, handoff in enumerate(chain):
            # 验证交接包本身
            validation_issues = handoff.validate()
            if validation_issues:
                issues.append({
                    'index': i,
                    'type': 'invalid_handoff',
                    'issues': validation_issues
                })
            
            # 验证链路连续性
            if i > 0:
                previous = chain[i - 1]
                if previous.to_skill != handoff.from_skill:
                    issues.append({
                        'index': i,
                        'type': 'chain_break',
                        'message': f"链路断裂: {previous.to_skill} != {handoff.from_skill}"
                    })
        
        return issues
    
    def export_session(
        self,
        session_id: str = "default",
        format: str = "yaml"
    ) -> str:
        """
        导出会话的所有交接包
        
        Args:
            session_id: 会话 ID
            format: 导出格式 (yaml/json)
            
        Returns:
            格式化的字符串
        """
        chain = self.get_chain(session_id)
        
        if format == "yaml":
            import yaml
            data = {
                'session_id': session_id,
                'chain': [h.to_dict() for h in chain]
            }
            return yaml.dump(data, allow_unicode=True, default_flow_style=False)
        else:
            data = {
                'session_id': session_id,
                'chain': [h.to_dict() for h in chain]
            }
            return json.dumps(data, ensure_ascii=False, indent=2)
    
    def import_session(
        self,
        data_str: str,
        session_id: str = "default",
        format: str = "yaml"
    ):
        """
        导入会话的交接包
        
        Args:
            data_str: 格式化的字符串
            session_id: 会话 ID
            format: 导入格式 (yaml/json)
        """
        if format == "yaml":
            import yaml
            data = yaml.safe_load(data_str)
        else:
            data = json.loads(data_str)
        
        chain_data = data.get('chain', [])
        
        self._memory_store[session_id] = []
        for handoff_data in chain_data:
            handoff = HandoffPackage.from_dict(handoff_data)
            self._memory_store[session_id].append(handoff)
    
    # ===== 内部方法 =====
    
    def _generate_id(self, handoff: HandoffPackage) -> str:
        """生成唯一 ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{handoff.from_skill}_{handoff.to_skill}_{timestamp}"
    
    def _persist(self, handoff: HandoffPackage, session_id: str, handoff_id: str):
        """持久化到文件"""
        if not self._storage_path:
            return
        
        # 创建会话目录
        session_path = self._storage_path / session_id
        session_path.mkdir(exist_ok=True)
        
        # 写入文件
        file_path = session_path / f"{handoff_id}.yaml"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(handoff.to_yaml())
    
    def __len__(self) -> int:
        """返回存储的交接包总数"""
        return sum(len(v) for v in self._memory_store.values())
    
    def __repr__(self) -> str:
        return f"HandoffManager(sessions={len(self._memory_store)}, total_handoffs={len(self)})"


class HandoffChainBuilder:
    """
    交接包链路构建器
    
    辅助构建完整的工作流链路
    
    Example:
        >>> builder = HandoffChainBuilder()
        >>> builder.add_skill("skill-00", "skill-03")
        >>> builder.add_skill("skill-03", "skill-02")
        >>> builder.add_skill("skill-02", "skill-05")
        >>> print(builder.get_path())
        skill-00 → skill-03 → skill-02 → skill-05
    """
    
    def __init__(self):
        self._chain: List[tuple] = []
    
    def add_skill(self, from_skill: str, to_skill: str, payload: Dict = None):
        """
        添加一个 Skill 转换
        
        Args:
            from_skill: 来源 Skill
            to_skill: 目标 Skill
            payload: 可选的 payload
        """
        self._chain.append((from_skill, to_skill, payload or {}))
    
    def get_path(self) -> str:
        """获取路径描述"""
        if not self._chain:
            return "空链路"
        
        skills = [self._chain[0][0]]
        for _, to_skill, _ in self._chain:
            skills.append(to_skill)
        
        return " → ".join(skills)
    
    def build_handoffs(self) -> List[HandoffPackage]:
        """构建交接包列表"""
        handoffs = []
        
        for from_skill, to_skill, payload in self._chain:
            handoff = HandoffPackage(
                from_skill=from_skill,
                to_skill=to_skill,
                payload=payload
            )
            handoffs.append(handoff)
        
        return handoffs


__all__ = ['HandoffManager', 'HandoffChainBuilder']
