"""
质量评估器实现

提供代码质量、文档完整性、安全性等多维度评估功能
"""

import os
import re
from typing import Dict, List, Optional
from pathlib import Path
from qcm_tools.quality.models import IndicatorResult, QualityReport
from qcm_tools.config.models import ProjectConfig
from qcm_tools.shared.enums import QualityLevel, ProjectType


class QualityChecker:
    """质量检查器基类"""
    
    def __init__(self, name: str):
        self.name = name
    
    def check(self, target: str, config: Optional[Dict] = None) -> IndicatorResult:
        """
        执行质量检查
        
        Args:
            target: 检查目标(项目路径或代码内容)
            config: 可选配置
            
        Returns:
            指标检查结果
        """
        raise NotImplementedError


class CodeQualityChecker(QualityChecker):
    """代码质量检查器"""
    
    # Python代码质量指标
    QUALITY_PATTERNS = {
        'has_docstring': r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'',
        'has_type_hints': r':\s*(str|int|float|bool|List|Dict|Optional)',
        'has_comments': r'#.*$',
        'has_functions': r'^\s*def\s+\w+',
        'has_classes': r'^\s*class\s+\w+',
    }
    
    # 代码异味模式
    CODE_SMELLS = {
        'long_function': (r'def\s+\w+\([^)]*\):[\s\S]{500,}', '函数过长'),
        'deep_nesting': (r'(\s{8,})if|(\s{8,})for|(\s{8,})while', '嵌套过深'),
        'magic_numbers': r'\b\d{3,}\b',
        'hardcoded_paths': r'["\']/[\w/]+["\']',
    }
    
    def __init__(self):
        super().__init__("代码质量")
    
    def check(self, target: str, config: Optional[Dict] = None) -> IndicatorResult:
        """
        检查代码质量
        
        Args:
            target: 项目路径或代码内容
            config: 质量标准配置
            
        Returns:
            代码质量检查结果
        """
        details = []
        recommendations = []
        score = 100.0
        
        # 检查是否为路径
        if os.path.isdir(target):
            # 扫描项目中的Python文件
            python_files = self._find_python_files(target)
            if not python_files:
                details.append("⚠️ 未找到Python代码文件")
                score -= 30
            else:
                details.append(f"✅ 找到 {len(python_files)} 个Python文件")
                
                # 统计代码质量指标
                stats = self._analyze_code_quality(python_files)
                
                # 文档字符串覆盖
                docstring_ratio = stats['has_docstring'] / max(stats['total_functions'], 1)
                details.append(f"文档字符串覆盖率: {docstring_ratio*100:.1f}%")
                if docstring_ratio < 0.5:
                    recommendations.append("建议增加函数文档字符串,提高代码可读性")
                    score -= 10
                
                # 类型提示覆盖
                type_hint_ratio = stats['has_type_hints'] / max(stats['total_functions'], 1)
                details.append(f"类型提示覆盖率: {type_hint_ratio*100:.1f}%")
                if type_hint_ratio < 0.3:
                    recommendations.append("建议添加类型提示,提高代码可维护性")
                    score -= 5
                
                # 代码复杂度
                avg_complexity = stats.get('avg_complexity', 5)
                details.append(f"平均代码复杂度: {avg_complexity:.1f}")
                if avg_complexity > 10:
                    recommendations.append("代码复杂度偏高,建议重构复杂函数")
                    score -= 15
                
                # 代码异味检测
                smells_found = stats.get('code_smells', {})
                if smells_found:
                    for smell_type, count in smells_found.items():
                        details.append(f"⚠️ 发现{smell_type}: {count}处")
                    score -= len(smells_found) * 5
        
        elif os.path.isfile(target):
            # 检查单个文件
            with open(target, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
            stats = self._analyze_single_file(code)
            details.extend(stats.get('details', []))
            score = stats.get('score', 70)
        
        else:
            # 当作代码内容处理
            stats = self._analyze_single_file(target)
            details.extend(stats.get('details', []))
            score = stats.get('score', 70)
        
        # 确定等级和是否通过
        level = self._score_to_level(score)
        passed = score >= 60
        
        return IndicatorResult(
            indicator_name=self.name,
            score=max(0, score),
            level=level,
            passed=passed,
            details=details,
            recommendations=recommendations
        )
    
    def _find_python_files(self, project_path: str) -> List[str]:
        """查找项目中的Python文件"""
        python_files = []
        for root, dirs, files in os.walk(project_path):
            # 跳过虚拟环境和缓存目录
            dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        return python_files[:20]  # 限制检查文件数量,避免耗时过长
    
    def _analyze_code_quality(self, python_files: List[str]) -> Dict:
        """分析代码质量"""
        stats = {
            'total_functions': 0,
            'has_docstring': 0,
            'has_type_hints': 0,
            'total_lines': 0,
            'code_smells': {},
            'avg_complexity': 5.0
        }
        
        total_complexity = 0
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    code = f.read()
                
                # 统计函数数量
                functions = re.findall(self.QUALITY_PATTERNS['has_functions'], code, re.MULTILINE)
                stats['total_functions'] += len(functions)
                
                # 统计文档字符串
                docstrings = re.findall(self.QUALITY_PATTERNS['has_docstring'], code)
                stats['has_docstring'] += len(docstrings)
                
                # 统计类型提示
                type_hints = re.findall(self.QUALITY_PATTERNS['has_type_hints'], code)
                stats['has_type_hints'] += len(type_hints)
                
                # 统计代码行数
                stats['total_lines'] += len(code.split('\n'))
                
                # 检测代码异味
                for smell_name, (pattern, _) in self.CODE_SMELLS.items():
                    matches = re.findall(pattern, code, re.MULTILINE)
                    if matches:
                        stats['code_smells'][smell_name] = len(matches)
                
                # 简单复杂度估算(基于嵌套层级)
                max_indent = 0
                for line in code.split('\n'):
                    if line.strip():
                        indent = len(line) - len(line.lstrip())
                        max_indent = max(max_indent, indent)
                total_complexity += min(max_indent // 4, 15)
                
            except Exception as e:
                continue
        
        if python_files:
            stats['avg_complexity'] = total_complexity / len(python_files)
        
        return stats
    
    def _analyze_single_file(self, code: str) -> Dict:
        """分析单个文件"""
        details = []
        score = 100.0
        
        # 检查文档字符串
        if re.search(self.QUALITY_PATTERNS['has_docstring'], code):
            details.append("✅ 包含文档字符串")
        else:
            details.append("⚠️ 缺少文档字符串")
            score -= 10
        
        # 检查类型提示
        if re.search(self.QUALITY_PATTERNS['has_type_hints'], code):
            details.append("✅ 包含类型提示")
        else:
            details.append("⚠️ 缺少类型提示")
            score -= 5
        
        # 检查注释
        comments = re.findall(self.QUALITY_PATTERNS['has_comments'], code, re.MULTILINE)
        if len(comments) > 3:
            details.append(f"✅ 包含 {len(comments)} 行注释")
        else:
            details.append("⚠️ 注释较少")
            score -= 5
        
        return {'details': details, 'score': score}
    
    def _score_to_level(self, score: float) -> QualityLevel:
        """分数转等级"""
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 80:
            return QualityLevel.GOOD
        elif score >= 60:
            return QualityLevel.PASS
        else:
            return QualityLevel.FAIL


class DocumentationChecker(QualityChecker):
    """文档完整性检查器"""
    
    # 必需文档列表
    REQUIRED_DOCS = {
        ProjectType.PRODUCTION: ['README.md', 'API文档', '部署文档'],
        ProjectType.RESEARCH: ['README.md', '实验说明', '论文文档'],
        ProjectType.TEACHING: ['README.md', '教程文档', '示例代码'],
        ProjectType.PERSONAL: ['README.md']
    }
    
    def __init__(self):
        super().__init__("文档完整性")
    
    def check(self, target: str, config: Optional[Dict] = None) -> IndicatorResult:
        """
        检查文档完整性
        
        Args:
            target: 项目路径
            config: 项目配置
            
        Returns:
            文档完整性检查结果
        """
        details = []
        recommendations = []
        score = 100.0
        
        if not os.path.isdir(target):
            details.append("⚠️ 目标不是项目目录")
            return IndicatorResult(
                indicator_name=self.name,
                score=0,
                level=QualityLevel.FAIL,
                passed=False,
                details=details
            )
        
        # 获取项目类型
        project_type = ProjectType.PERSONAL
        if config and 'project_type' in config:
            try:
                project_type_str = config['project_type']
                # 根据字符串匹配枚举
                for pt in ProjectType:
                    if pt.value == project_type_str:
                        project_type = pt
                        break
            except:
                pass
        
        # 检查必需文档
        required_docs = self.REQUIRED_DOCS.get(project_type, ['README.md'])
        missing_docs = []
        
        for doc in required_docs:
            doc_found = self._find_documentation(target, doc)
            if doc_found:
                details.append(f"✅ 找到: {doc}")
            else:
                missing_docs.append(doc)
                details.append(f"❌ 缺少: {doc}")
        
        if missing_docs:
            score -= len(missing_docs) * 20
            recommendations.append(f"建议补充缺失文档: {', '.join(missing_docs)}")
        
        # 检查README内容质量
        readme_path = os.path.join(target, 'README.md')
        if os.path.exists(readme_path):
            readme_quality = self._check_readme_quality(readme_path)
            if readme_quality < 0.5:
                details.append("⚠️ README内容不完整")
                recommendations.append("建议完善README,包含安装、使用、示例等内容")
                score -= 10
            else:
                details.append("✅ README内容完整")
        
        # 检查代码注释率
        python_files = self._find_python_files(target)
        if python_files:
            comment_ratio = self._calculate_comment_ratio(python_files)
            details.append(f"代码注释率: {comment_ratio*100:.1f}%")
            if comment_ratio < 0.1:
                recommendations.append("建议增加代码注释,提高可读性")
                score -= 10
        
        level = self._score_to_level(score)
        passed = score >= 60
        
        return IndicatorResult(
            indicator_name=self.name,
            score=max(0, score),
            level=level,
            passed=passed,
            details=details,
            recommendations=recommendations
        )
    
    def _find_documentation(self, project_path: str, doc_name: str) -> bool:
        """查找文档"""
        # 检查docs目录
        docs_dir = os.path.join(project_path, 'docs')
        if os.path.isdir(docs_dir):
            for file in os.listdir(docs_dir):
                if doc_name.lower() in file.lower():
                    return True
        
        # 检查根目录
        for file in os.listdir(project_path):
            if doc_name.lower() in file.lower():
                return True
        
        # 特殊检查
        if doc_name == 'README.md':
            return os.path.exists(os.path.join(project_path, 'README.md'))
        elif doc_name == 'API文档':
            return os.path.exists(os.path.join(project_path, 'docs', 'api.md')) or \
                   os.path.exists(os.path.join(project_path, 'API.md'))
        elif doc_name == '部署文档':
            return os.path.exists(os.path.join(project_path, 'docs', 'deployment.md')) or \
                   os.path.exists(os.path.join(project_path, 'docs', 'deploy.md')) or \
                   os.path.exists(os.path.join(project_path, 'DEPLOYMENT.md'))
        
        return False
    
    def _check_readme_quality(self, readme_path: str) -> float:
        """检查README质量"""
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查关键章节
            required_sections = ['安装', '使用', '示例', 'Install', 'Usage', 'Example']
            found_sections = 0
            
            for section in required_sections:
                if section in content:
                    found_sections += 1
            
            return found_sections / len(required_sections)
        except:
            return 0.0
    
    def _find_python_files(self, project_path: str) -> List[str]:
        """查找Python文件"""
        python_files = []
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git']]
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        return python_files[:10]
    
    def _calculate_comment_ratio(self, python_files: List[str]) -> float:
        """计算注释率"""
        total_lines = 0
        comment_lines = 0
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        total_lines += 1
                        if line.strip().startswith('#') or '"""' in line or "'''" in line:
                            comment_lines += 1
            except:
                continue
        
        return comment_lines / max(total_lines, 1)
    
    def _score_to_level(self, score: float) -> QualityLevel:
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 80:
            return QualityLevel.GOOD
        elif score >= 60:
            return QualityLevel.PASS
        else:
            return QualityLevel.FAIL


class SecurityChecker(QualityChecker):
    """安全性检查器"""
    
    # 安全风险模式
    SECURITY_PATTERNS = {
        'hardcoded_password': (r'password\s*=\s*["\'][^"\']+["\']', '硬编码密码'),
        'hardcoded_secret': (r'secret\s*=\s*["\'][^"\']+["\']|api_key\s*=\s*["\'][^"\']+["\']', '硬编码密钥'),
        'sql_injection': (r'execute\s*\(\s*["\'].*%s.*["\']', '潜在SQL注入'),
        'eval_usage': (r'\beval\s*\(', '使用eval函数'),
        'exec_usage': (r'\bexec\s*\(', '使用exec函数'),
        'pickle_usage': (r'pickle\.loads?\s*\(', '不安全的pickle使用'),
    }
    
    def __init__(self):
        super().__init__("安全性")
    
    def check(self, target: str, config: Optional[Dict] = None) -> IndicatorResult:
        """
        检查安全性
        
        Args:
            target: 项目路径或代码内容
            config: 质量标准配置
            
        Returns:
            安全性检查结果
        """
        details = []
        recommendations = []
        score = 100.0
        high_risks = []
        medium_risks = []
        
        # 检查是否为路径
        if os.path.isdir(target):
            python_files = self._find_python_files(target)
            if not python_files:
                details.append("⚠️ 未找到Python代码文件")
            else:
                details.append(f"✅ 扫描 {len(python_files)} 个Python文件")
                
                # 扫描安全风险
                for file_path in python_files:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            code = f.read()
                        
                        file_risks = self._scan_security_risks(code, file_path)
                        high_risks.extend(file_risks['high'])
                        medium_risks.extend(file_risks['medium'])
                    except:
                        continue
        
        elif os.path.isfile(target):
            with open(target, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
            file_risks = self._scan_security_risks(code, target)
            high_risks.extend(file_risks['high'])
            medium_risks.extend(file_risks['medium'])
        
        else:
            # 当作代码内容处理
            file_risks = self._scan_security_risks(target, "代码片段")
            high_risks.extend(file_risks['high'])
            medium_risks.extend(file_risks['medium'])
        
        # 处理发现的风险
        if high_risks:
            details.append(f"❌ 发现 {len(high_risks)} 个高危安全问题:")
            for risk in high_risks[:5]:  # 只显示前5个
                details.append(f"   - {risk}")
            score -= len(high_risks) * 30
            recommendations.append("存在高危安全漏洞,建议立即修复")
        
        if medium_risks:
            details.append(f"⚠️ 发现 {len(medium_risks)} 个中危安全问题:")
            for risk in medium_risks[:5]:
                details.append(f"   - {risk}")
            score -= len(medium_risks) * 10
            recommendations.append("建议修复中危安全问题")
        
        if not high_risks and not medium_risks:
            details.append("✅ 未发现明显安全问题")
        
        # 检查依赖安全
        requirements_file = os.path.join(target, 'requirements.txt') if os.path.isdir(target) else None
        if requirements_file and os.path.exists(requirements_file):
            details.append("✅ 找到requirements.txt")
            # 这里可以集成pip-audit等工具
        
        level = self._score_to_level(score)
        passed = score >= 60 and len(high_risks) == 0
        
        return IndicatorResult(
            indicator_name=self.name,
            score=max(0, score),
            level=level,
            passed=passed,
            details=details,
            recommendations=recommendations
        )
    
    def _find_python_files(self, project_path: str) -> List[str]:
        """查找Python文件"""
        python_files = []
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git']]
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        return python_files[:20]
    
    def _scan_security_risks(self, code: str, file_path: str) -> Dict:
        """扫描安全风险"""
        risks = {'high': [], 'medium': []}
        
        # 高危模式
        high_risk_patterns = {
            'hardcoded_password': self.SECURITY_PATTERNS['hardcoded_password'],
            'hardcoded_secret': self.SECURITY_PATTERNS['hardcoded_secret'],
            'eval_usage': self.SECURITY_PATTERNS['eval_usage'],
            'exec_usage': self.SECURITY_PATTERNS['exec_usage'],
        }
        
        # 中危模式
        medium_risk_patterns = {
            'sql_injection': self.SECURITY_PATTERNS['sql_injection'],
            'pickle_usage': self.SECURITY_PATTERNS['pickle_usage'],
        }
        
        # 检查高危模式
        for risk_name, (pattern, description) in high_risk_patterns.items():
            matches = re.findall(pattern, code, re.IGNORECASE)
            if matches:
                for match in matches[:3]:  # 每种类型最多显示3个
                    risks['high'].append(f"{description} in {os.path.basename(file_path)}")
        
        # 检查中危模式
        for risk_name, (pattern, description) in medium_risk_patterns.items():
            matches = re.findall(pattern, code, re.IGNORECASE)
            if matches:
                for match in matches[:3]:
                    risks['medium'].append(f"{description} in {os.path.basename(file_path)}")
        
        return risks
    
    def _score_to_level(self, score: float) -> QualityLevel:
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 80:
            return QualityLevel.GOOD
        elif score >= 60:
            return QualityLevel.PASS
        else:
            return QualityLevel.FAIL


class QualityAssessor:
    """
    质量评估器
    
    对项目进行全面的质量评估
    
    Example:
        >>> from qcm_tools.quality import QualityAssessor
        >>> from qcm_tools.config import ConfigGenerator
        >>> 
        >>> # 创建配置
        >>> config_gen = ConfigGenerator()
        >>> config = config_gen.generate_from_description("开发一个API系统")
        >>> 
        >>> # 评估质量
        >>> assessor = QualityAssessor()
        >>> report = assessor.assess("./my_project", config)
        >>> print(report.to_markdown())
    """
    
    def __init__(self):
        """初始化质量评估器"""
        self.checkers = [
            CodeQualityChecker(),
            DocumentationChecker(),
            SecurityChecker()
        ]
    
    def assess(
        self,
        target: str,
        config: Optional[ProjectConfig] = None
    ) -> QualityReport:
        """
        执行质量评估
        
        Args:
            target: 项目路径或代码内容
            config: 项目配置(可选)
            
        Returns:
            质量评估报告
            
        Example:
            >>> assessor = QualityAssessor()
            >>> report = assessor.assess("./my_project")
        """
        # 创建报告
        report = QualityReport(
            project_name=self._extract_project_name(target, config),
            project_type=config.project_type.value if config else "未知"
        )
        
        # 配置字典
        config_dict = config.to_dict() if config else {}
        
        # 执行所有检查
        for checker in self.checkers:
            try:
                result = checker.check(target, config_dict)
                report.indicator_results[checker.name] = result
            except Exception as e:
                # 如果检查失败,记录错误
                report.indicator_results[checker.name] = IndicatorResult(
                    indicator_name=checker.name,
                    score=0,
                    level=QualityLevel.FAIL,
                    passed=False,
                    details=[f"❌ 检查失败: {str(e)}"],
                    recommendations=["建议检查项目配置"]
                )
        
        # 计算总体得分
        report.calculate_overall_score()
        
        # 生成总结
        self._generate_summary(report)
        
        return report
    
    def assess_code(self, code: str, config: Optional[ProjectConfig] = None) -> QualityReport:
        """
        评估代码质量(快捷方法)
        
        Args:
            code: 代码内容
            config: 项目配置(可选)
            
        Returns:
            质量评估报告
        """
        return self.assess(code, config)
    
    def _extract_project_name(self, target: str, config: Optional[ProjectConfig]) -> str:
        """提取项目名称"""
        if config and config.name:
            return config.name
        
        if os.path.isdir(target):
            return os.path.basename(os.path.abspath(target))
        
        return "代码片段"
    
    def _generate_summary(self, report: QualityReport):
        """生成总结"""
        passed_count = sum(1 for r in report.indicator_results.values() if r.passed)
        total_count = len(report.indicator_results)
        
        report.summary = (
            f"质量评估完成。{passed_count}/{total_count}项指标通过。"
            f"总体得分{report.overall_score:.1f}分,质量等级: {report.overall_level.value}"
        )
        
        # 汇总所有建议
        for result in report.indicator_results.values():
            report.recommendations.extend(result.recommendations)
        
        # 去重
        report.recommendations = list(dict.fromkeys(report.recommendations))


__all__ = ['QualityAssessor', 'QualityChecker', 'CodeQualityChecker', 'DocumentationChecker', 'SecurityChecker']
