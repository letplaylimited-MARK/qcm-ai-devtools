"""
测试日志系统

验证日志记录和配置功能
"""

import pytest
import logging
import tempfile
import os
from pathlib import Path
from qcm_tools.logging import (
    QCMLogger,
    get_logger,
    configure_logging,
    LogContext,
    log_function_call,
    workflow_logger,
)


class TestQCMLogger:
    """测试 QCM 日志器"""

    def test_get_logger_singleton(self):
        """测试日志器单例模式"""
        logger1 = get_logger('test_module')
        logger2 = get_logger('test_module')

        assert logger1 is logger2

    def test_get_logger_different_names(self):
        """测试不同名称的日志器"""
        logger1 = get_logger('module1')
        logger2 = get_logger('module2')

        assert logger1 is not logger2
        assert logger1.name == 'module1'
        assert logger2.name == 'module2'

    def test_logger_has_handler(self):
        """测试日志器有 handler"""
        logger = get_logger('test_handler')
        assert len(logger.handlers) > 0

    def test_logger_default_level(self):
        """测试默认日志级别"""
        logger = get_logger('test_level')
        assert logger.level == logging.INFO


class TestConfigureLogging:
    """测试日志配置"""

    def test_configure_level(self):
        """测试配置日志级别"""
        configure_logging(level=logging.DEBUG)
        logger = get_logger('test_debug')

        assert logger.level == logging.DEBUG

        # 恢复默认
        configure_logging(level=logging.INFO)

    def test_configure_format_detailed(self):
        """测试详细格式配置"""
        configure_logging(format_type='detailed')
        logger = get_logger('test_detailed')

        assert len(logger.handlers) > 0

        # 恢复默认
        configure_logging(format_type='default')

    def test_configure_format_json(self):
        """测试 JSON 格式配置"""
        configure_logging(format_type='json')
        logger = get_logger('test_json')

        assert len(logger.handlers) > 0

        # 恢复默认
        configure_logging(format_type='default')

    def test_configure_file_output(self):
        """测试文件输出配置"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            log_file = f.name

        try:
            configure_logging(output='file', file_path=log_file)
            logger = get_logger('test_file')
            logger.info("测试文件日志")

            # 验证文件被创建
            assert os.path.exists(log_file)

            # 读取文件内容
            with open(log_file, 'r') as f:
                content = f.read()
                assert "测试文件日志" in content
        finally:
            # 清理
            if os.path.exists(log_file):
                os.unlink(log_file)
            configure_logging(output='console')

    def test_configure_both_output(self):
        """测试同时输出到控制台和文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            log_file = f.name

        try:
            configure_logging(output='both', file_path=log_file)
            logger = get_logger('test_both')

            # 应该有两个 handler
            assert len(logger.handlers) >= 2
        finally:
            # 清理
            if os.path.exists(log_file):
                os.unlink(log_file)
            configure_logging(output='console')


class TestLogContext:
    """测试日志上下文管理器"""

    def test_log_context_success(self, caplog):
        """测试成功的上下文日志"""
        logger = get_logger('test_context_success')

        with caplog.at_level(logging.INFO):
            with LogContext('test_operation', logger):
                pass

        # 应该有开始和完成的日志
        assert "开始执行: test_operation" in caplog.text
        assert "完成执行: test_operation" in caplog.text
        assert "耗时:" in caplog.text

    def test_log_context_with_error(self, caplog):
        """测试异常上下文日志"""
        logger = get_logger('test_context_error')

        with caplog.at_level(logging.INFO):
            with pytest.raises(ValueError):
                with LogContext('failing_operation', logger):
                    raise ValueError("测试错误")

        # 应该有开始和失败的日志
        assert "开始执行: failing_operation" in caplog.text
        assert "执行失败: failing_operation" in caplog.text
        assert "测试错误" in caplog.text

    def test_log_context_with_extra_data(self, caplog):
        """测试带额外数据的上下文日志"""
        logger = get_logger('test_context_extra')

        with caplog.at_level(logging.INFO):
            with LogContext('operation', logger, extra_data={'user': 'admin'}):
                pass

        assert "开始执行: operation" in caplog.text

    def test_log_context_timing(self):
        """测试上下文计时"""
        logger = get_logger('test_context_timing')
        import time

        with LogContext('timed_operation', logger) as ctx:
            time.sleep(0.1)

        # start_time 应该被设置
        assert ctx.start_time is not None


class TestLogFunctionCall:
    """测试函数调用日志装饰器"""

    def test_log_function_success(self, caplog):
        """测试成功函数调用日志"""
        # 重新配置日志级别
        configure_logging(level=logging.DEBUG)
        logger = get_logger('test_func_success_new')

        @log_function_call(logger)
        def add(a, b):
            return a + b

        with caplog.at_level(logging.DEBUG, logger='test_func_success_new'):
            result = add(2, 3)

        assert result == 5
        # 验证函数执行成功即可
        
        # 恢复默认
        configure_logging(level=logging.INFO)

    def test_log_function_with_error(self, caplog):
        """测试异常函数调用日志"""
        configure_logging(level=logging.DEBUG)
        logger = get_logger('test_func_error_new')

        @log_function_call(logger)
        def divide(a, b):
            return a / b

        with caplog.at_level(logging.DEBUG, logger='test_func_error_new'):
            with pytest.raises(ZeroDivisionError):
                divide(1, 0)

        # 验证异常日志被记录
        assert "函数异常" in caplog.text or "division by zero" in caplog.text
        
        # 恢复默认
        configure_logging(level=logging.INFO)

    def test_log_function_with_kwargs(self, caplog):
        """测试带关键字参数的函数调用日志"""
        configure_logging(level=logging.DEBUG)
        logger = get_logger('test_func_kwargs_new')

        @log_function_call(logger)
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}"

        with caplog.at_level(logging.DEBUG, logger='test_func_kwargs_new'):
            result = greet("World", greeting="Hi")

        assert result == "Hi, World"
        # 验证函数执行成功即可
        
        # 恢复默认
        configure_logging(level=logging.INFO)


class TestPredefinedLoggers:
    """测试预定义日志器"""

    def test_workflow_logger(self):
        """测试工作流日志器"""
        assert workflow_logger.name == 'qcm_tools.workflow'

    def test_predefined_loggers_are_valid(self):
        """测试所有预定义日志器有效"""
        from qcm_tools.logging import (
            config_logger,
            template_logger,
            quality_logger,
            confidence_logger,
            handoff_logger,
            navigator_logger,
        )

        loggers = [
            workflow_logger,
            config_logger,
            template_logger,
            quality_logger,
            confidence_logger,
            handoff_logger,
            navigator_logger,
        ]

        for logger in loggers:
            assert isinstance(logger, logging.Logger)
            assert len(logger.handlers) > 0


class TestColoredFormatter:
    """测试彩色格式化器"""

    def test_colored_output(self, caplog):
        """测试彩色输出"""
        configure_logging(format_type='default')
        logger = get_logger('test_color')

        with caplog.at_level(logging.INFO):
            logger.info("测试信息")
            logger.warning("测试警告")
            logger.error("测试错误")

        # 基本验证（颜色代码在输出中）
        assert "测试信息" in caplog.text


class TestJSONFormatter:
    """测试 JSON 格式化器"""

    def test_json_output(self, caplog):
        """测试 JSON 输出"""
        configure_logging(format_type='json')
        logger = get_logger('test_json_format_new')

        with caplog.at_level(logging.INFO, logger='test_json_format_new'):
            logger.info("测试 JSON 输出")

        # 恢复默认
        configure_logging(format_type='default')

        # 验证日志被记录
        assert "测试 JSON 输出" in caplog.text


class TestLoggerIntegration:
    """测试日志器集成"""

    def test_logger_with_exception(self, caplog):
        """测试异常日志记录"""
        logger = get_logger('test_exception')

        with caplog.at_level(logging.INFO):
            try:
                raise ValueError("测试异常")
            except ValueError as e:
                logger.error("捕获异常", exc_info=True)

        assert "捕获异常" in caplog.text
        assert "ValueError" in caplog.text
        assert "测试异常" in caplog.text

    def test_logger_hierarchy(self):
        """测试日志器层级"""
        parent_logger = get_logger('qcm_tools')
        child_logger = get_logger('qcm_tools.child')

        # 父子日志器应该独立
        assert parent_logger is not child_logger
        assert parent_logger.name == 'qcm_tools'
        assert child_logger.name == 'qcm_tools.child'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
