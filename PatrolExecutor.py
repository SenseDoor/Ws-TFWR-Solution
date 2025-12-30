# === 巡逻执行器 ===
# 负责遍历区域，收获、种植、浇水

import Config
import TaskCenter
import ZoneManager
from Base import move_to, do_water, do_harvest, do_plant

# 巡逻执行器主循环
def run(task_id):
	# 1. 申请区域
	zone = ZoneManager.request_zone(task_id, "patrol")
	if zone == None:
		print("Patrol task " + str(task_id) + " failed: no zone")
		TaskCenter.complete_task(task_id)
		return

	while True:
		# 2. 遍历区域
		for y in range(zone["y"], zone["y"] + zone["height"]):
			for x in range(zone["x"], zone["x"] + zone["width"]):
				# 跳过被其他任务占用的格子
				if ZoneManager.is_occupied(x, y):
					continue
				move_to(x, y)
				_process_tile(x, y)

# 处理单个格子
def _process_tile(x, y):
	do_water()

	if do_harvest():
		_plant_after_harvest(x, y)
	elif get_entity_type() == None:
		_plant_empty(x, y)

# 收获后种植
def _plant_after_harvest(x, y):
	is_tree_pos = (x + y) % 2 == 0
	if is_tree_pos:
		do_plant(Entities.Tree)
	elif num_items(Items.Wood) >= Config.MIN_WOOD_FOR_CARROT:
		do_plant(Entities.Carrot)
	else:
		do_plant(Entities.Grass)

# 空地种植
def _plant_empty(x, y):
	_plant_after_harvest(x, y)
