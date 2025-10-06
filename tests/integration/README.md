# 集成测试文档

本目录包含 AI PowerShell 智能助手的集成测试套件，用于验证系统各个模块的协作和整体功能。

## 测试文件概述

### 1. test_end_to_end.py - 端到端集成测试

测试完整的用户请求处理流程，从输入到输出，验证所有模块的协作。

**测试类：**

- `TestEndToEndFlow`: 端到端流程测试
  - `test_complete_safe_command_flow`: 测试安全命令的完整流程
  - `test_multiple_commands_in_session`: 测试会话中执行多个命令
  - `test_context_awareness`: 测试上下文感知能力
  - `test_error_recovery`: 测试错误恢复能力
  - `test_history_persistence`: 测试历史记录持久化

- `TestModuleCollaboration`: 模块协作测试
  - `test_ai_to_security_flow`: 测试 AI 引擎到安全引擎的流程
  - `test_security_to_executor_flow`: 测试安全引擎到执行引擎的流程
  - `test_executor_to_storage_flow`: 测试执行引擎到存储引擎的流程
  - `test_context_manager_integration`: 测试上下文管理器与其他模块的集成

- `TestErrorHandlingAcrossModules`: 跨模块错误处理测试
  - `test_ai_engine_failure_handling`: 测试 AI 引擎失败时的处理
  - `test_security_engine_blocking`: 测试安全引擎阻止命令
  - `test_executor_timeout_handling`: 测试执行器超时处理
  - `test_storage_failure_graceful_handling`: 测试存储失败时的优雅处理

- `TestConcurrentRequests`: 并发请求测试
  - `test_sequential_requests_in_same_session`: 测试同一会话中的顺序请求

**运行示例：**
```bash
# 运行所有端到端测试
python -m pytest tests/integration/test_end_to_end.py -v

# 运行特定测试类
python -m pytest tests/integration/test_end_to_end.py::TestEndToEndFlow -v

# 运行特定测试
python -m pytest tests/integration/test_end_to_end.py::TestEndToEndFlow::test_complete_safe_command_flow -v
```

### 2. test_performance.py - 性能基准测试

测试系统各个组件的性能指标，包括 AI 翻译延迟、命令执行延迟等。

**测试类：**

- `TestAITranslationPerformance`: AI 翻译性能测试
  - `test_single_translation_latency`: 测试单次翻译延迟（< 1秒）
  - `test_batch_translation_performance`: 测试批量翻译性能
  - `test_cache_effectiveness`: 测试缓存有效性

- `TestSecurityValidationPerformance`: 安全验证性能测试
  - `test_single_validation_latency`: 测试单次安全验证延迟（< 100ms）
  - `test_batch_validation_performance`: 测试批量安全验证性能

- `TestCommandExecutionPerformance`: 命令执行性能测试
  - `test_simple_command_execution_latency`: 测试简单命令执行延迟（< 2秒）
  - `test_multiple_commands_execution_performance`: 测试多个命令执行性能

- `TestEndToEndPerformance`: 端到端性能测试
  - `test_complete_request_latency`: 测试完整请求处理延迟（< 3秒）
  - `test_throughput_measurement`: 测试系统吞吐量
  - `test_memory_efficiency`: 测试内存效率

- `TestPerformanceUnderLoad`: 负载下的性能测试
  - `test_sustained_load_performance`: 测试持续负载下的性能
  - `test_performance_degradation`: 测试性能退化（< 50%）

**性能指标：**
- AI 翻译延迟: < 1秒
- 安全验证延迟: < 100ms
- 命令执行延迟: < 2秒
- 完整请求延迟: < 3秒
- 性能退化: < 50%

**运行示例：**
```bash
# 运行所有性能测试
python -m pytest tests/integration/test_performance.py -v -s

# 运行特定性能测试
python -m pytest tests/integration/test_performance.py::TestAITranslationPerformance -v -s
```

### 3. test_security.py - 安全集成测试

测试系统的安全机制，包括危险命令阻止、权限检查、沙箱隔离等。

**测试类：**

- `TestDangerousCommandBlocking`: 危险命令阻止测试
  - `test_recursive_delete_blocked`: 测试递归删除命令被阻止
  - `test_format_volume_blocked`: 测试格式化磁盘命令被阻止
  - `test_system_shutdown_blocked`: 测试系统关机命令被阻止
  - `test_system_directory_deletion_blocked`: 测试系统目录删除被阻止
  - `test_safe_commands_allowed`: 测试安全命令被允许

- `TestPermissionChecking`: 权限检查测试
  - `test_admin_command_detection`: 测试管理员命令检测
  - `test_regular_user_commands`: 测试普通用户命令

- `TestRiskLevelAssessment`: 风险等级评估测试
  - `test_safe_risk_level`: 测试安全风险等级
  - `test_low_risk_level`: 测试低风险等级
  - `test_medium_risk_level`: 测试中等风险等级
  - `test_high_risk_level`: 测试高风险等级
  - `test_critical_risk_level`: 测试严重风险等级

- `TestSandboxIsolation`: 沙箱隔离测试
  - `test_sandbox_execution`: 测试沙箱执行（需要 Docker）
  - `test_sandbox_configuration_validation`: 测试沙箱配置验证

- `TestSecurityBypass`: 安全绕过测试（负面测试）
  - `test_obfuscated_dangerous_command`: 测试混淆的危险命令
  - `test_command_injection_prevention`: 测试命令注入防护

- `TestEndToEndSecurityFlow`: 端到端安全流程测试
  - `test_safe_command_full_flow`: 测试安全命令的完整流程
  - `test_dangerous_command_blocked_flow`: 测试危险命令被阻止的完整流程
  - `test_security_audit_logging`: 测试安全审计日志

- `TestSecurityConfiguration`: 安全配置测试
  - `test_strict_mode_configuration`: 测试严格模式配置
  - `test_permissive_mode_configuration`: 测试宽松模式配置

**运行示例：**
```bash
# 运行所有安全测试
python -m pytest tests/integration/test_security.py -v -s

# 运行危险命令阻止测试
python -m pytest tests/integration/test_security.py::TestDangerousCommandBlocking -v -s

# 跳过需要 Docker 的测试
python -m pytest tests/integration/test_security.py -v -m "not docker"
```

### 4. test_main_integration.py - 主控制器集成测试

测试 PowerShellAssistant 与各个模块的集成，验证完整的请求处理流程。

**测试类：**

- `TestMainIntegration`: 主控制器集成测试
  - `test_full_request_flow_with_safe_command`: 测试安全命令的完整请求流程
  - `test_context_persistence_across_requests`: 测试多个请求之间的上下文持久化
  - `test_dangerous_command_blocked`: 测试危险命令被阻止

- `TestMainWithMockedComponents`: 使用 mock 组件的主控制器测试
  - `test_error_handling_in_ai_engine`: 测试 AI 引擎错误处理
  - `test_error_handling_in_executor`: 测试执行器错误处理

## 运行所有集成测试

```bash
# 运行所有集成测试
python -m pytest tests/integration/ -v

# 运行所有集成测试并显示输出
python -m pytest tests/integration/ -v -s

# 运行所有集成测试并生成覆盖率报告
python -m pytest tests/integration/ -v --cov=src --cov-report=html

# 运行特定类型的测试
python -m pytest tests/integration/ -v -k "performance"
python -m pytest tests/integration/ -v -k "security"
python -m pytest tests/integration/ -v -k "end_to_end"
```

## 测试配置

所有集成测试使用临时配置文件，配置内容包括：

- AI 引擎配置（本地模式）
- 安全引擎配置（可配置的白名单模式）
- 执行引擎配置（30秒超时）
- 日志配置（输出到临时日志文件）
- 存储配置（使用临时目录）
- 上下文配置（100条历史记录）

## 测试数据

测试过程中生成的数据存储在以下位置：

- 日志文件: `logs/`
- 测试数据: `test_data/`
- 临时配置: pytest 临时目录

## 注意事项

1. **PowerShell 依赖**: 某些测试需要系统安装 PowerShell（pwsh 或 powershell）
2. **Docker 依赖**: 沙箱测试需要 Docker 环境，默认跳过
3. **性能测试**: 性能测试结果可能因系统配置而异
4. **并发测试**: 某些测试可能需要较长时间完成
5. **临时文件**: 测试会创建临时文件和目录，测试结束后会自动清理

## 持续集成

这些测试可以集成到 CI/CD 流程中：

```yaml
# .github/workflows/integration-tests.yml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run integration tests
        run: |
          python -m pytest tests/integration/ -v --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 贡献指南

添加新的集成测试时，请遵循以下原则：

1. 测试应该独立且可重复
2. 使用临时配置和数据目录
3. 清理测试产生的临时文件
4. 添加适当的文档和注释
5. 确保测试在不同平台上可运行
6. 使用有意义的测试名称
7. 包含性能断言（如适用）
8. 验证错误处理路径

## 相关需求

这些集成测试覆盖以下需求：

- **Requirement 6.1**: 完整的请求处理流程
- **Requirement 6.3**: 交互模式和命令行模式
- **Requirement 4.1**: 命令白名单验证
- **Requirement 4.2**: 权限检查
- **Requirement 4.3**: 沙箱执行
- **Requirement 5.1**: AI 翻译性能
- **Requirement 5.2**: AI 模型集成

## 测试覆盖率目标

- 端到端流程: > 90%
- 模块协作: > 85%
- 错误处理: > 80%
- 性能测试: 所有关键路径
- 安全测试: 所有安全机制
