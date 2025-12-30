# === 区域管理器 ===
# 动态分配区域，与任务生命周期绑定

import Config

# 区域存储: {task_id: {"x": int, "y": int, "width": int, "height": int}}
zones = {}

# 已占用格子集合: {(x, y), ...}
occupied = set()

def request_zone(task_id, zone_type):
	if zone_type == "pumpkin":
		return _request_pumpkin_zone(task_id)
	elif zone_type == "patrol":
		return _request_patrol_zone(task_id)
	print("Unknown zone type: " + zone_type)
	return None

def _request_pumpkin_zone(task_id):
	spec = Config.ZONE_SPECS["pumpkin"]
	width = spec["width"]
	height = spec["height"]

	# 寻找一个空闲的 6x6 区域
	for start_y in range(Config.WORLD_SIZE - height + 1):
		for start_x in range(Config.WORLD_SIZE - width + 1):
			if _is_area_free(start_x, start_y, width, height):
				zone = {"x": start_x, "y": start_y, "width": width, "height": height}
				_occupy_area(task_id, zone)
				return zone

	print("No free pumpkin zone for task " + str(task_id))
	return None

def _request_patrol_zone(task_id):
	# 计算未被占用的区域
	# 简化实现：分配除已占用外的整个地图
	# 巡逻区只跳过已占用格子

	zone = {"x": 0, "y": 0, "width": Config.WORLD_SIZE, "height": Config.WORLD_SIZE}
	zones[task_id] = zone
	return zone

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

def release_zone(task_id):
	if task_id not in zones:
		return

	zone = zones[task_id]

	# 只有固定区域需要释放占用（巡逻区不占用格子）
	task_type = _get_task_type(task_id)
	if task_type == "pumpkin":
		for dy in range(zone["height"]):
			for dx in range(zone["width"]):
				pos = (zone["x"] + dx, zone["y"] + dy)
				if pos in occupied:
					occupied.remove(pos)

	zones.remove(task_id)

def _get_task_type(task_id):
	import TaskCenter
	return TaskCenter.get_task_type(task_id)

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
