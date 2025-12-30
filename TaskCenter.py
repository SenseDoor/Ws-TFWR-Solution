# === 任务中心 ===
# 负责任务生命周期管理，是系统的任务调度核心

import Config
import ZoneManager

# 任务状态常量
TASK_PENDING = 0
TASK_RUNNING = 1
TASK_COMPLETED = 2

# 任务存储: {task_id: {"type": str, "status": int, "drone": handle, "zone": zone}}
tasks = {}
next_task_id = 1

# 执行器引用（延迟导入避免循环依赖）
_executor_module = None

def _get_executor():
	global _executor_module
	if _executor_module == None:
		import Executor
		_executor_module = Executor
	return _executor_module

# 初始化任务中心
def init():
	global tasks
	global next_task_id
	tasks = {}
	next_task_id = 1

# 根据 Config 配置创建所有任务
def create_all_tasks():
	for task_type in Config.ENABLED_TASKS:
		_create_task(task_type)

# 内部：创建单个任务
def _create_task(task_type):
	global next_task_id
	task_id = next_task_id
	next_task_id = next_task_id + 1
	tasks[task_id] = {"type": task_type, "status": TASK_PENDING}
	return task_id

# 为所有待处理任务启动执行器
def dispatch_all():
	for task_id in tasks:
		if tasks[task_id]["status"] == TASK_PENDING:
			_dispatch_task(task_id)

# 根据任务类型获取区域类型
def _get_zone_type(task_type):
	if task_type == "pumpkin":
		return "pumpkin"
	return "patrol"

# 内部：启动执行器（生成无人机）
def _dispatch_task(task_id):
	task_type = tasks[task_id]["type"]

	# 主无人机先分配区域（解决无共享内存问题）
	zone_type = _get_zone_type(task_type)
	zone = ZoneManager.request_zone(task_id, zone_type)
	if zone == None:
		# 无可用区域，任务失败
		tasks[task_id]["status"] = TASK_COMPLETED
		return

	tasks[task_id]["status"] = TASK_RUNNING
	tasks[task_id]["zone"] = zone

	# 获取对应的执行器函数
	executor = _get_executor()
	executor_func = executor.get_executor(task_type)

	# 创建闭包捕获 task_id 和 zone
	def run_task():
		executor_func(task_id, zone)

	drone = spawn_drone(run_task)
	tasks[task_id]["drone"] = drone

# 完成任务
def complete_task(task_id):
	if task_id in tasks:
		tasks[task_id]["status"] = TASK_COMPLETED
	else:
		print("Task not found: " + str(task_id))

# 获取任务信息
def get_task(task_id):
	if task_id in tasks:
		return tasks[task_id]
	return None

# 获取任务类型
def get_task_type(task_id):
	if task_id in tasks:
		return tasks[task_id]["type"]
	return None

# 按状态列出任务
def list_tasks_by_status(status):
	result = []
	for task_id in tasks:
		if tasks[task_id]["status"] == status:
			result.append(task_id)
	return result

# 监控循环：检测任务完成，重新创建并分发
def monitor():
	# 检查运行中的任务，看无人机是否完成
	running = list_tasks_by_status(TASK_RUNNING)
	for task_id in running:
		task = tasks[task_id]
		# 检查无人机是否存在且已完成
		drone = None
		if "drone" in task:
			drone = task["drone"]
		# drone 为 None 表示 spawn 失败，视为完成
		if drone == None or has_finished(drone):
			# 无人机完成，释放区域并标记任务完成
			if "zone" in task:
				ZoneManager.release_zone(task_id)
			task["status"] = TASK_COMPLETED

	# 检查是否还有未完成的任务
	running = list_tasks_by_status(TASK_RUNNING)
	pending = list_tasks_by_status(TASK_PENDING)

	if len(running) > 0 or len(pending) > 0:
		return  # 还有任务在执行

	# 所有任务完成，重新创建并分发
	create_all_tasks()
	dispatch_all()
