# === 南瓜执行器 ===
# 负责 6x6 巨型南瓜的种植和收获

import Config
import TaskCenter
import ZoneManager
from Base import move_to, do_water

# 南瓜执行器主循环
def run(task_id):
	# 1. 申请区域
	zone = ZoneManager.request_zone(task_id, "pumpkin")
	if zone == None:
		print("Pumpkin task " + str(task_id) + " failed: no zone")
		TaskCenter.complete_task(task_id)
		return

	while True:
		# 2. 等待资源
		while num_items(Items.Carrot) < Config.MIN_CARROT_FOR_PUMPKIN:
			pass

		# 3. 种植 6x6
		_plant_grid(zone)

		# 4. 等待成熟并修复
		while not _check_all_ready(zone):
			_scan_and_fix(zone)

		# 5. 收获
		move_to(zone["x"], zone["y"])
		harvest()

# 种植南瓜网格
def _plant_grid(zone):
	sx = zone["x"]
	sy = zone["y"]
	size = zone["width"]

	move_to(sx, sy)

	for dy in range(size):
		if dy % 2 == 0:
			# 向东
			for dx in range(size):
				_plant_at()
				if dx < size - 1:
					move(East)
		else:
			# 向西
			for dx in range(size - 1, -1, -1):
				_plant_at()
				if dx > 0:
					move(West)
		if dy < size - 1:
			move(North)

# 在当前位置种植南瓜
def _plant_at():
	entity = get_entity_type()
	if entity != Entities.Pumpkin:
		if can_harvest():
			harvest()
		if get_ground_type() == Grounds.Grassland:
			till()
		if num_items(Items.Carrot) >= 1:
			plant(Entities.Pumpkin)
	do_water()

# 检查是否全部成熟
def _check_all_ready(zone):
	sx = zone["x"]
	sy = zone["y"]
	size = zone["width"]

	for dy in range(size):
		for dx in range(size):
			move_to(sx + dx, sy + dy)
			entity = get_entity_type()
			if entity != Entities.Pumpkin:
				return False
			if not can_harvest():
				return False
	return True

# 扫描并修复
def _scan_and_fix(zone):
	sx = zone["x"]
	sy = zone["y"]
	size = zone["width"]

	for dy in range(size):
		y = sy + dy
		if dy % 2 == 0:
			for dx in range(size):
				move_to(sx + dx, y)
				_fix_tile()
		else:
			for dx in range(size - 1, -1, -1):
				move_to(sx + dx, y)
				_fix_tile()

# 修复单个格子
def _fix_tile():
	entity = get_entity_type()

	if entity == Entities.Pumpkin:
		if can_harvest():
			return
		if num_items(Items.Carrot) >= 1:
			plant(Entities.Pumpkin)
		do_water()
	else:
		if can_harvest():
			harvest()
		if get_ground_type() == Grounds.Grassland:
			till()
		if num_items(Items.Carrot) >= 1:
			plant(Entities.Pumpkin)
		do_water()
