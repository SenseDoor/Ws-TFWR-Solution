# === 任务中心 ===
# 负责任务生命周期管理，是系统的任务调度核心
# 动态按需生成任务，按权重随机选择任务类型

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

# ============ 资源链映射 ============

# Item → Entity 映射
ITEM_TO_ENTITY = {
	Items.Pumpkin: Entities.Pumpkin,
	Items.Carrot: Entities.Carrot,
	Items.Wood: Entities.Tree,
	Items.Hay: Entities.Grass,
	Items.Cactus: Entities.Cactus,
}

# Entity → task_type 映射
ENTITY_TO_TASK = {
	Entities.Pumpkin: "pumpkin",
	Entities.Carrot: "carrot",
	Entities.Tree: "tree",
	Entities.Grass: "grass",
	Entities.Cactus: "cactus",
}

# ============ 任务类型选择 ============

# 按权重随机选择目标 Item
def _select_target_item():
	items = []
	weights = []
	for item in Config.TARGET_WEIGHTS:
		items.append(item)
		weights.append(Config.TARGET_WEIGHTS[item])

	total = 0
	for w in weights:
		total = total + w

	r = random() * total
	cumulative = 0
	for i in range(len(items)):
		cumulative = cumulative + weights[i]
		if r < cumulative:
			return items[i]
	return items[len(items) - 1]

# 递归查找缺口资源对应的任务
def _find_needed_task(target_item):
	entity = ITEM_TO_ENTITY[target_item]
	cost = get_cost(entity)

	# 检查是否缺少依赖资源
	if cost != None:
		for item in cost:
			if num_items(item) < cost[item]:
				# 缺少此资源，递归查找
				return _find_needed_task(item)

	# 依赖满足，执行此任务
	return ENTITY_TO_TASK[entity]

# 根据目标权重选择目标，再反推资源链
def _select_task_type():
	target = _select_target_item()
	return _find_needed_task(target)

# 根据任务类型获取区域类型
def _get_zone_type(task_type):
	if task_type == "pumpkin":
		return "pumpkin"
	return "patrol"

# ============ 任务生命周期 ============

# 内部：创建单个任务
def _create_task(task_type):
	global next_task_id
	task_id = next_task_id
	next_task_id = next_task_id + 1
	tasks[task_id] = {"type": task_type, "status": TASK_PENDING}
	return task_id

# 尝试创建并分发单个任务，返回是否成功
def _try_dispatch_one(task_type):
	task_id = _create_task(task_type)

	# 主无人机先分配区域
	zone_type = _get_zone_type(task_type)
	zone = ZoneManager.request_zone(task_id, zone_type)
	if zone == None:
		# 无可用区域
		tasks[task_id]["status"] = TASK_COMPLETED
		return False

	tasks[task_id]["status"] = TASK_RUNNING
	tasks[task_id]["zone"] = zone

	# 获取执行器函数
	executor = _get_executor()
	executor_func = executor.get_executor(task_type)

	# 创建闭包捕获 task_id 和 zone
	def run_task():
		executor_func(task_id, zone)

	# 尝试 spawn 无人机
	drone = spawn_drone(run_task)
	if drone == None:
		# spawn 失败，释放区域
		ZoneManager.release_zone(task_id)
		tasks[task_id]["status"] = TASK_COMPLETED
		return False

	tasks[task_id]["drone"] = drone
	return True

# 清理已完成的任务
def _cleanup_finished():
	running = list_tasks_by_status(TASK_RUNNING)
	for task_id in running:
		task = tasks[task_id]
		drone = None
		if "drone" in task:
			drone = task["drone"]
		# drone 为 None 或已完成
		if drone == None or has_finished(drone):
			if "zone" in task:
				ZoneManager.release_zone(task_id)
			task["status"] = TASK_COMPLETED

# 主无人机执行彩蛋（回退逻辑）
def _do_fallback():
	executor = _get_executor()
	fallback_func = executor.get_executor("fallback")
	fallback_func(0, None)

# ============ 公共接口 ============

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

# ============ 监控循环 ============

# 监控循环：动态生成任务
def monitor():
	# 1. 清理已完成任务
	_cleanup_finished()

	# 2. 按权重随机选择任务类型
	task_type = _select_task_type()

	# 3. 尝试创建并分发任务
	success = _try_dispatch_one(task_type)

	# 4. 失败则主无人机执行彩蛋
	if not success:
		_do_fallback()
