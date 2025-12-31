# === 树执行器 ===
# 收获 + 种树
# 优化：棋盘格种植，避免相邻树减速（相邻树使生长时间翻倍）

import ZoneManager

_task_id = 0

# zone 由 TaskCenter 预分配并通过闭包传入（解决无共享内存问题）
def run(task_id, zone):
	global _task_id
	_task_id = task_id

	_process_zone(zone)
	# 注意：区域释放和任务完成由主无人机处理（因为无共享内存）

def _process_zone(zone):
	for y in range(zone["y"], zone["y"] + zone["height"]):
		for x in range(zone["x"], zone["x"] + zone["width"]):
			ZoneManager.move_to(_task_id, x, y)
			_process_tile(x, y)

# 棋盘格种植：只在 (x+y) % 2 == 0 的位置种树
def _process_tile(x, y):
	if can_harvest():
		harvest()

	if get_entity_type() == None:
		# 棋盘格模式：避免相邻树
		if (x + y) % 2 == 0:
			plant(Entities.Tree)
