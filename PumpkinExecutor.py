# === 南瓜执行器 ===
# 负责 6x6 巨型南瓜的种植和收获
# 优化：螺旋扩展种植 2x2 → 3x3 → ... → 6x6
# 每级必须全部成熟无坏南瓜才能扩展

import Config
import ZoneManager

# 当前任务 ID（模块级变量，避免传递）
_task_id = 0

# 坏南瓜位置列表
_bad_positions = []

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
def run(task_id, zone):
	global _task_id
	global _bad_positions
	_task_id = task_id
	_bad_positions = []

	# 等待资源
	while num_items(Items.Carrot) < Config.MIN_CARROT_FOR_PUMPKIN:
		pass

	sx = zone["x"]
	sy = zone["y"]
	target_size = zone["width"]

	# 螺旋扩展：从 2x2 开始
	current_size = 2
	while current_size <= target_size:
		# 种植当前层级
		_plant_ring(sx, sy, current_size)

		# 等待当前层级全部成熟
		while not _check_ring_ready(sx, sy, current_size):
			_fix_bad_positions()

		# 当前层级完成，扩展到下一级
		current_size = current_size + 1

	# 收获
	ZoneManager.move_to(_task_id, sx, sy)
	harvest()

# 种植指定大小的区域（只种新增的边缘）
def _plant_ring(sx, sy, size):
	if size == 2:
		# 初始 2x2，全部种植
		for dy in range(2):
			for dx in range(2):
				ZoneManager.move_to(_task_id, sx + dx, sy + dy)
				_plant_at()
	else:
		# 种植新增的边缘（右边一列 + 上边一行）
		# 右边一列：x = sx + size - 1, y = sy 到 sy + size - 2
		for dy in range(size - 1):
			ZoneManager.move_to(_task_id, sx + size - 1, sy + dy)
			_plant_at()
		# 上边一行：y = sy + size - 1, x = sx 到 sx + size - 1
		for dx in range(size):
			ZoneManager.move_to(_task_id, sx + dx, sy + size - 1)
			_plant_at()

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
	_do_water()

# 检查当前层级边缘是否全部成熟（内部已完成区域无需检查）
def _check_ring_ready(sx, sy, size):
	global _bad_positions
	_bad_positions = []
	all_ready = True

	if size == 2:
		# 初始 2x2，检查全部
		for dy in range(2):
			for dx in range(2):
				if not _check_tile(sx + dx, sy + dy):
					all_ready = False
	else:
		# 只检查新增边缘（右边一列 + 上边一行）
		# 右边一列
		for dy in range(size - 1):
			if not _check_tile(sx + size - 1, sy + dy):
				all_ready = False
		# 上边一行
		for dx in range(size):
			if not _check_tile(sx + dx, sy + size - 1):
				all_ready = False

	return all_ready

# 检查单个格子，发现问题顺手补种
def _check_tile(x, y):
	global _bad_positions
	ZoneManager.move_to(_task_id, x, y)
	entity = get_entity_type()

	if entity != Entities.Pumpkin:
		# 坏南瓜或空地，顺手补种
		if can_harvest():
			harvest()
		if get_ground_type() == Grounds.Grassland:
			till()
		if num_items(Items.Carrot) >= 1:
			plant(Entities.Pumpkin)
		_do_water()
		# 记录位置，下次验证
		_bad_positions.append({"x": x, "y": y})
		return False
	elif not can_harvest():
		# 未成熟，浇水
		_do_water()
		return False

	return True

# 验证并修复坏南瓜位置（已在 _check_tile 中补种，这里只验证）
def _fix_bad_positions():
	global _bad_positions

	if len(_bad_positions) == 0:
		return

	# 直接前往坏南瓜位置验证
	for pos in _bad_positions:
		ZoneManager.move_to(_task_id, pos["x"], pos["y"])
		entity = get_entity_type()
		# 如果还不是南瓜，再补种一次
		if entity != Entities.Pumpkin:
			if can_harvest():
				harvest()
			if get_ground_type() == Grounds.Grassland:
				till()
			if num_items(Items.Carrot) >= 1:
				plant(Entities.Pumpkin)
		_do_water()

	# 清空列表，下次检查会重新收集
	_bad_positions = []
