# === 区域管理器 ===
# 动态分配区域，与任务生命周期绑定
# 负责路径规划，避开禁止穿越区域

import Config

# 区域存储: {task_id: {"x": int, "y": int, "width": int, "height": int}}
zones = {}

# 已占用格子集合: {(x, y), ...}
occupied = set()

# 巡逻小块默认大小
PATROL_BLOCK_SIZE = 4

# ============ 移动 ============

def move_to(task_id, target_x, target_y):
	current_x = get_pos_x()
	current_y = get_pos_y()
	_do_move(current_x, current_y, target_x, target_y)

def _do_move(from_x, from_y, to_x, to_y):
	dx = to_x - from_x
	dy = to_y - from_y

	if dx > 0:
		if dx <= Config.WORLD_SIZE - dx:
			for _ in range(dx):
				move(East)
		else:
			for _ in range(Config.WORLD_SIZE - dx):
				move(West)
	elif dx < 0:
		dx = -dx
		if dx <= Config.WORLD_SIZE - dx:
			for _ in range(dx):
				move(West)
		else:
			for _ in range(Config.WORLD_SIZE - dx):
				move(East)

	if dy > 0:
		if dy <= Config.WORLD_SIZE - dy:
			for _ in range(dy):
				move(North)
		else:
			for _ in range(Config.WORLD_SIZE - dy):
				move(South)
	elif dy < 0:
		dy = -dy
		if dy <= Config.WORLD_SIZE - dy:
			for _ in range(dy):
				move(South)
		else:
			for _ in range(Config.WORLD_SIZE - dy):
				move(North)

# ============ 区域分配 ============

def request_zone(task_id, zone_type):
	if zone_type == "pumpkin":
		return _request_fixed_zone(task_id, 6, 6)
	elif zone_type == "patrol":
		return _request_patrol_zone(task_id)
	print("Unknown zone type: " + zone_type)
	return None

# 申请固定大小区域（南瓜等）
def _request_fixed_zone(task_id, width, height):
	for start_y in range(Config.WORLD_SIZE - height + 1):
		for start_x in range(Config.WORLD_SIZE - width + 1):
			if _is_area_free(start_x, start_y, width, height):
				zone = {"x": start_x, "y": start_y, "width": width, "height": height}
				_occupy_area(task_id, zone)
				return zone

	print("No free zone " + str(width) + "x" + str(height) + " for task " + str(task_id))
	return None

# 申请巡逻区域（智能分配：优先小块，紧张时单格）
def _request_patrol_zone(task_id):
	# 优先尝试分配小块
	block = _find_free_block(PATROL_BLOCK_SIZE, PATROL_BLOCK_SIZE)
	if block != None:
		zone = {"x": block[0], "y": block[1], "width": PATROL_BLOCK_SIZE, "height": PATROL_BLOCK_SIZE}
		_occupy_area(task_id, zone)
		return zone

	# 降级：尝试更小的块
	for size in [2, 1]:
		block = _find_free_block(size, size)
		if block != None:
			zone = {"x": block[0], "y": block[1], "width": size, "height": size}
			_occupy_area(task_id, zone)
			return zone

	return None

def _find_free_block(width, height):
	for start_y in range(Config.WORLD_SIZE - height + 1):
		for start_x in range(Config.WORLD_SIZE - width + 1):
			if _is_area_free(start_x, start_y, width, height):
				return (start_x, start_y)
	return None

def _is_area_free(start_x, start_y, width, height):
	for dy in range(height):
		for dx in range(width):
			if (start_x + dx, start_y + dy) in occupied:
				return False
	return True

def _occupy_area(task_id, zone):
	zones[task_id] = zone
	for dy in range(zone["height"]):
		for dx in range(zone["width"]):
			occupied.add((zone["x"] + dx, zone["y"] + dy))

# ============ 区域释放 ============

def release_zone(task_id):
	if task_id not in zones:
		return

	zone = zones[task_id]

	for dy in range(zone["height"]):
		for dx in range(zone["width"]):
			pos = (zone["x"] + dx, zone["y"] + dy)
			if pos in occupied:
				occupied.remove(pos)

	zones.pop(task_id)

# ============ 查询 ============

def get_zone(task_id):
	if task_id in zones:
		return zones[task_id]
	return None

def is_occupied(x, y):
	return (x, y) in occupied

def is_in_zone(x, y, task_id):
	if task_id not in zones:
		return False

	zone = zones[task_id]
	return (zone["x"] <= x < zone["x"] + zone["width"] and
			zone["y"] <= y < zone["y"] + zone["height"])

def get_free_count():
	return Config.WORLD_SIZE * Config.WORLD_SIZE - len(occupied)
