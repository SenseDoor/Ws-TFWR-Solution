# === 执行器注册表 ===
# 负责管理和分发执行器

import PumpkinExecutor
import PatrolExecutor
import DefaultExecutor

# 执行器注册表
EXECUTORS = {
	"pumpkin": PumpkinExecutor.run,
	"patrol": PatrolExecutor.run,
}

# 根据任务类型返回执行器函数
def get_executor(task_type):
	if task_type in EXECUTORS:
		return EXECUTORS[task_type]
	return DefaultExecutor.run

# 动态注册执行器
def register(task_type, executor_func):
	EXECUTORS[task_type] = executor_func
