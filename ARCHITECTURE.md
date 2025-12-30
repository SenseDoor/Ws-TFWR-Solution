# 系统架构文档

## 核心原则

1. **模块化** - 主循环不得有业务参数及详细业务逻辑，只能有模块级调用
2. **任务中心** - 负责生成任务（唯一ID），监察所有任务状态
3. **执行器** - 对应游戏无人机，申领任务ID，向区域管理申请区域
4. **区域管理** - 由执行器持任务ID申领，生命周期与任务一致

---

## 架构图

```
┌─────────────────────────────────────────────────────┐
│                     main.py                          │
│            (纯调度，零业务参数)                        │
│  init() → create_all_tasks() → dispatch_all()       │
├─────────────────────────────────────────────────────┤
│                   TaskCenter.py                      │
│  任务生命周期: pending → running → completed          │
│  create_all_tasks() / dispatch_all() / complete()   │
├─────────────────────────────────────────────────────┤
│                  ZoneManager.py                      │
│  动态区域分配，与任务生命周期绑定                      │
│  request_zone(task_id, type) → zone                 │
│  release_zone(task_id) / is_occupied(x, y)          │
├─────────────────────────────────────────────────────┤
│                   Executor.py                        │
│  执行器 = 无人机包装 + 任务绑定                       │
│  run_pumpkin(task_id) / run_patrol(task_id)         │
├─────────────────────────────────────────────────────┤
│                    Config.py                         │
│  静态配置（任务列表、区域规格、资源阈值）              │
└─────────────────────────────────────────────────────┘
```

---

## 模块职责

### main.py
- **纯调度，零业务参数**
- 只调用 TaskCenter 的模块级函数
- 不包含任何业务逻辑或参数

### Config.py
- 定义启用的任务列表 `ENABLED_TASKS`
- 定义区域规格 `ZONE_SPECS`
- 定义资源阈值（胡萝卜、木头、水）

### TaskCenter.py
- 任务生命周期管理（pending → running → completed）
- 根据 Config 创建任务
- 分发任务到执行器（spawn_drone）
- 提供任务查询接口

### ZoneManager.py
- 动态区域分配
- 区域与任务ID绑定
- 追踪已占用格子
- 支持释放区域

### Executor.py
- 包含所有执行器实现
- 基础操作函数（move_to, do_water, do_harvest, do_plant）
- 南瓜执行器（run_pumpkin）
- 巡逻执行器（run_patrol）

---

## 核心流程

```
1. main.py
   │
   ├─ TaskCenter.init()
   │
   ├─ TaskCenter.create_all_tasks()
   │   └─ 读取 Config.ENABLED_TASKS
   │   └─ 为每个类型创建任务（分配 task_id）
   │
   ├─ TaskCenter.dispatch_all()
   │   └─ 为每个 pending 任务启动执行器
   │   └─ spawn_drone(executor_func)
   │
   └─ TaskCenter.monitor()
       └─ 主循环（可扩展）

2. 执行器流程（以 pumpkin 为例）
   │
   ├─ ZoneManager.request_zone(task_id, "pumpkin")
   │   └─ 分配 6x6 区域
   │   └─ 标记格子为已占用
   │
   ├─ while True:
   │   ├─ 等待资源
   │   ├─ 种植 6x6
   │   ├─ 等待成熟
   │   └─ 收获
   │
   └─ （任务完成时）
       ├─ ZoneManager.release_zone(task_id)
       └─ TaskCenter.complete_task(task_id)
```

---

## 文件结构

```
Claude/
├── __builtins__.py    # 游戏API类型定义（保留）
├── Config.py          # 静态配置
├── TaskCenter.py      # 任务中心
├── ZoneManager.py     # 区域管理
├── Executor.py        # 执行器
├── main.py            # 主入口
└── ARCHITECTURE.md    # 本文档
```

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2025-12-30 | 初始架构：任务中心 + 区域管理 + 执行器 |
