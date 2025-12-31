# === 系统配置 ===
# 所有业务参数在此定义，main.py 不直接引用这些值

WORLD_SIZE = get_world_size()

# === 产出目标权重 ===
TARGET_WEIGHTS = {
	Items.Pumpkin: 1,
	Items.Cactus: 2,
	Items.Carrot: 0,
}

# === 区域规格 ===
ZONE_SPECS = {
	"pumpkin": {"width": 6, "height": 6},
}

# === 资源阈值 ===
MIN_CARROT_FOR_PUMPKIN = 36
MIN_WATER = 5

# === 浇水参数 ===
WATER_THRESHOLD = 0.25
WATER_TARGET = 0.75

# === 区域分配 ===
# 是否紧凑分配同类区域（False 表示同类区域间保留 1 格间距）
COMPACT_ZONE = False
