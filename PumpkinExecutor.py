# === 南瓜执行器 ===
# 负责 6x6 巨型南瓜的种植和收获

import Config
import ZoneManager

# 当前任务 ID（模块级变量，避免传递）
_task_id = 0

# 浇水
def _do_water():
	if num_items(Items.Water) <= Config.MIN_WATER:
		return
	if get_water() >= Config.WATER_THRESHOLD:
		return
	while get_water() < Config.WATER_TARGET:
		if num_items(Items.Water) <= Config.MIN_WATER:
			break
		use_item(Items.Water)

# 南瓜执行器：单次执行
# zone 由 TaskCenter 预分配并通过闭包传入（解决无共享内存问题）
def run(task_id, zone):
	global _task_id
	_task_id = task_id

	# 等待资源
	while num_items(Items.Carrot) < Config.MIN_CARROT_FOR_PUMPKIN:
		pass

	# 种植
	_plant_grid(zone)

	# 等待成熟
	while not _check_all_ready(zone):
		_scan_and_fix(zone)

	# 收获
	ZoneManager.move_to(_task_id, zone["x"], zone["y"])
	harvest()
	# 注意：区域释放和任务完成由主无人机处理（因为无共享内存）

def _plant_grid(zone):
	sx = zone["x"]
	sy = zone["y"]
	size = zone["width"]

	ZoneManager.move_to(_task_id, sx, sy)

	for dy in range(size):
		if dy % 2 == 0:
			for dx in range(size):
				_plant_at()
				if dx < size - 1:
					move(East)
		else:
			for dx in range(size - 1, -1, -1):
				_plant_at()
				if dx > 0:
					move(West)
		if dy < size - 1:
			move(North)

def _plant_at():
	entity = get_entity_type()
	if entity != Entities.Pumpkin:
		if can_harvest():
			harvest()
		if get_ground_type() == Grounds.Grassland:
			till()
		if num_items(Items.Carrot) >= 1:
			plant(Entities.Pumpkin)
	_do_water()

def _check_all_ready(zone):
	sx = zone["x"]
	sy = zone["y"]
	size = zone["width"]

	for dy in range(size):
		for dx in range(size):
			ZoneManager.move_to(_task_id, sx + dx, sy + dy)
			entity = get_entity_type()
			if entity != Entities.Pumpkin:
				return False
			if not can_harvest():
				return False
	return True

def _scan_and_fix(zone):
	sx = zone["x"]
	sy = zone["y"]
	size = zone["width"]

	for dy in range(size):
		y = sy + dy
		if dy % 2 == 0:
			for dx in range(size):
				ZoneManager.move_to(_task_id, sx + dx, y)
				_fix_tile()
		else:
			for dx in range(size - 1, -1, -1):
				ZoneManager.move_to(_task_id, sx + dx, y)
				_fix_tile()

def _fix_tile():
	entity = get_entity_type()

	if entity == Entities.Pumpkin:
		if can_harvest():
			return
		if num_items(Items.Carrot) >= 1:
			plant(Entities.Pumpkin)
		_do_water()
	else:
		if can_harvest():
			harvest()
		if get_ground_type() == Grounds.Grassland:
			till()
		if num_items(Items.Carrot) >= 1:
			plant(Entities.Pumpkin)
		_do_water()
