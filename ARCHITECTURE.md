# 系统架构文档

## 核心原则

1. **模块化** - 主循环不得有业务参数及详细业务逻辑，只能有模块级调用
2. **任务中心** - 动态生成任务，监察所有任务状态，按权重和资源链选择任务类型
3. **执行器** - 对应游戏无人机，执行具体任务逻辑
4. **区域管理** - 主无人机预分配区域，通过闭包传递给子无人机（解决无共享内存问题）

---

## 架构图

```
┌─────────────────────────────────────────────────────┐
│                     main.py                          │
│            (纯调度，零业务参数)                        │
│           init() → while: monitor()                  │
├─────────────────────────────────────────────────────┤
│                   TaskCenter.py                      │
│  任务生命周期: pending → running → completed          │
│  资源链驱动：按权重选目标 → 反推资源链 → 分发任务      │
├─────────────────────────────────────────────────────┤
│                  ZoneManager.py                      │
│  动态区域分配，主无人机预分配，通过闭包传递            │
│  request_zone(task_id, type) → zone                 │
│  release_zone(task_id) / move_to(task_id, x, y)     │
├─────────────────────────────────────────────────────┤
│                   Executor.py                        │
│  执行器注册表，分发到具体执行器模块                   │
│  get_executor(task_type) → executor_func            │
├─────────────────────────────────────────────────────┤
│         *Executor.py (具体执行器模块)                │
│  PumpkinExecutor / TreeExecutor / CarrotExecutor    │
│  GrassExecutor / CactusExecutor / DefaultExecutor   │
├─────────────────────────────────────────────────────┤
│                    Config.py                         │
│  静态配置（目标权重、区域规格、资源阈值）              │
└─────────────────────────────────────────────────────┘
```

---

## 模块职责

### main.py
- **纯调度，零业务参数**
- 初始化 TaskCenter，进入监控循环
- 不包含任何业务逻辑或参数

### Config.py
- 定义产出目标权重 `TARGET_WEIGHTS`
- 定义区域规格 `ZONE_SPECS`
- 定义资源阈值（胡萝卜、水等）

### TaskCenter.py
- 任务生命周期管理（pending → running → completed）
- **资源链驱动**：按权重选择目标 Item，递归检查 get_cost() 补充缺口资源
- 主无人机预分配区域，spawn_drone 时通过闭包传递 zone
- 清理已完成任务，释放区域

### ZoneManager.py
- 动态区域分配（固定大小/巡逻区域）
- 区域与任务ID绑定
- 追踪已占用格子
- 提供 move_to() 移动函数

### Executor.py
- 执行器注册表
- 根据 task_type 返回对应执行器函数

### 具体执行器
- **PumpkinExecutor**: 螺旋扩展种植 2x2→6x6，处理枯萎南瓜
- **TreeExecutor**: 棋盘格种植，避免相邻减速
- **CarrotExecutor**: 耕地 + 种植，检查资源
- **GrassExecutor**: 收获 + 种草
- **CactusExecutor**: 种植 + 排序 + 连锁收获
- **DefaultExecutor**: 彩蛋动作（fallback）

---

## 核心流程

```
1. main.py
   │
   ├─ TaskCenter.init()
   │
   └─ while True: TaskCenter.monitor()
       │
       ├─ _cleanup_finished()
       │   └─ 检查 has_finished(drone)，释放区域
       │
       ├─ _select_task_type()
       │   ├─ _select_target_item()  # 按 TARGET_WEIGHTS 权重随机
       │   └─ _find_needed_task()    # 递归检查 get_cost()，补充缺口
       │
       ├─ _try_dispatch_one(task_type)
       │   ├─ ZoneManager.request_zone()  # 主无人机预分配
       │   ├─ 创建闭包捕获 zone
       │   └─ spawn_drone(run_task)
       │
       └─ 失败则 _do_fallback()

2. 执行器流程（以 pumpkin 为例）
   │
   ├─ run(task_id, zone)  # zone 通过闭包传入
   │
   ├─ 螺旋扩展种植
   │   ├─ _plant_ring(sx, sy, size)
   │   └─ _check_ring_ready() + _fix_bad_positions()
   │
   └─ 收获（区域释放由主无人机处理）
```

---

## 关键设计

### 无共享内存问题
- 每架无人机有独立的全局变量副本
- 解决方案：主无人机预分配区域，通过闭包传递给子无人机
- 区域释放由主无人机在 `_cleanup_finished()` 中处理

### 资源链驱动
- 按权重随机选择目标 Item（如 Pumpkin）
- 递归检查 `get_cost(entity)` 找到缺口资源
- 例：目标南瓜 → 缺胡萝卜 → 缺干草 → 执行草任务

---

## 文件结构

```
Claude/
├── __builtins__.py       # 游戏API类型定义
├── Config.py             # 静态配置
├── TaskCenter.py         # 任务中心
├── ZoneManager.py        # 区域管理
├── Executor.py           # 执行器注册表
├── PumpkinExecutor.py    # 南瓜执行器
├── TreeExecutor.py       # 树执行器
├── CarrotExecutor.py     # 胡萝卜执行器
├── GrassExecutor.py      # 草执行器
├── CactusExecutor.py     # 仙人掌执行器
├── DefaultExecutor.py    # 默认执行器
├── main.py               # 主入口
├── ARCHITECTURE.md       # 本文档
├── RULES.md              # 语法限制
└── PLANTS.md             # 作物知识
```

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2025-12-30 | 初始架构：任务中心 + 区域管理 + 执行器 |
| v2.0 | 2025-12-31 | 动态任务生成，资源链驱动，多目标权重配置 |
| v2.1 | 2025-12-31 | 添加 CactusExecutor，优化 PumpkinExecutor 螺旋扩展 |
