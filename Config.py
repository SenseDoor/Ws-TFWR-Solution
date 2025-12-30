# === 系统配置 ===
# 所有业务参数在此定义，main.py 不直接引用这些值

WORLD_SIZE = get_world_size()

# === 启用的任务列表 ===
ENABLED_TASKS = ["pumpkin", "patrol"]

# === 区域规格 ===
ZONE_SPECS = {
	"pumpkin": {"width": 6, "height": 6},
	"patrol": {"width": 0, "height": 0},  # 动态计算（剩余空间）
}

# === 资源阈值 ===
MIN_CARROT_FOR_PUMPKIN = 36
MIN_WOOD_FOR_CARROT = 1
MIN_WATER = 5

# === 浇水参数 ===
WATER_THRESHOLD = 0.25
WATER_TARGET = 0.75
