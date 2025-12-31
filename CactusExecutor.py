# === 仙人掌执行器 ===
# 种植仙人掌，等待成熟，排序后连锁收获
# 排序规则：North/East >= 自身，South/West <= 自身
# 产出 = n² （n 为连锁收获的仙人掌数量）
# 排序策略：先排行（每行从左到右递增），再排列（每列从下到上递增）

import ZoneManager

_task_id = 0

def run(task_id, zone):
	global _task_id
	_task_id = task_id

	sx = zone["x"]
	sy = zone["y"]
	width = zone["width"]
	height = zone["height"]

	# 1. 种植仙人掌
	_plant_all(sx, sy, width, height)

	# 2. 等待全部成熟
	while not _all_mature(sx, sy, width, height):
		pass

	# 3. 排序：先排行，再排列
	_sort_all(sx, sy, width, height)

	# 4. 收获（从左下角开始，触发连锁）
	ZoneManager.move_to(_task_id, sx, sy)
	harvest()

# 种植全部仙人掌
def _plant_all(sx, sy, width, height):
	for y in range(sy, sy + height):
		for x in range(sx, sx + width):
			ZoneManager.move_to(_task_id, x, y)
			if get_entity_type() != Entities.Cactus:
				if can_harvest():
					harvest()
				if get_ground_type() == Grounds.Grassland:
					till()
				plant(Entities.Cactus)

# 检查全部是否成熟
def _all_mature(sx, sy, width, height):
	for y in range(sy, sy + height):
		for x in range(sx, sx + width):
			ZoneManager.move_to(_task_id, x, y)
			if not can_harvest():
				return False
	return True

# 排序全部仙人掌
def _sort_all(sx, sy, width, height):
	# 先排行：每行从左到右递增（冒泡排序）
	for y in range(sy, sy + height):
		_sort_row(sx, y, width)

	# 再排列：每列从下到上递增（冒泡排序）
	for x in range(sx, sx + width):
		_sort_column(x, sy, height)

# 排序单行（从左到右递增）
def _sort_row(sx, y, width):
	# 冒泡排序：多次遍历直到无交换
	sorted_flag = False
	while not sorted_flag:
		sorted_flag = True
		ZoneManager.move_to(_task_id, sx, y)
		for i in range(width - 1):
			current = measure()
			right = measure(East)
			# measure 可能返回 None，需要检查
			if current != None and right != None and current > right:
				swap(East)
				sorted_flag = False
			move(East)

# 排序单列（从下到上递增）
def _sort_column(x, sy, height):
	# 冒泡排序：多次遍历直到无交换
	sorted_flag = False
	while not sorted_flag:
		sorted_flag = True
		ZoneManager.move_to(_task_id, x, sy)
		for i in range(height - 1):
			current = measure()
			up = measure(North)
			# measure 可能返回 None，需要检查
			if current != None and up != None and current > up:
				swap(North)
				sorted_flag = False
			move(North)
