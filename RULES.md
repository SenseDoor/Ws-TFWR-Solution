# The Farmer Was Replaced - Game Knowledge

Wiki: https://thefarmerwasreplaced.wiki.gg/

---

## Syntax Limitations (语法限制)

此游戏使用简化版 Python，以下语法**不支持**：

| 不支持 | 替代方案 |
|--------|----------|
| `del x` | `dict.pop(key)` 或 `list.remove(elem)` |
| `"""docstring"""` | 只能用 `#` 注释 |
| `lambda x: x+1` | 定义普通函数 |
| `from folder import x` | 只支持 `import module` |
| `global a, b` | 分开写 `global a` 和 `global b` |
| `int(x)` | 不支持类型转换，用整数运算代替 |

---

## List (列表)

```python
list = [2, True, Items.Hay]
empty_list = []
list[0]  # 访问第一个元素
```

| 方法 | 说明 |
|------|------|
| `list.append(x)` | 末尾添加 |
| `list.remove(x)` | 移除首个匹配项 |
| `list.insert(i, x)` | 在索引处插入 |
| `list.pop()` | 移除并返回最后一项 |
| `list.pop(i)` | 移除并返回索引处元素 |
| `len(list)` | 长度 |

**引用语义**：赋值不复制，修改会影响所有引用。

---

## Dict (字典)

```python
d = {North: East, East: South}
d[key]          # 获取
d[key] = value  # 设置
d.pop(key)      # 删除
key in d        # 检查存在
```

遍历：`for key in d:` （顺序不保证）

---

## Multi-Drone (多无人机)

### 基础 API

| 函数 | 说明 |
|------|------|
| `spawn_drone(func)` | 生成无人机执行 func，返回 drone 句柄，达上限返回 None |
| `max_drones()` | 无人机数量上限 |
| `num_drones()` | 当前无人机数量 |
| `wait_for(drone)` | 等待无人机完成，返回其函数返回值 |
| `has_finished(drone)` | 检查是否完成（非阻塞） |

### 关键特性

1. **无共享内存** - 每架无人机有独立的全局变量副本
2. **无碰撞** - 无人机不会相互碰撞
3. **无主从** - 所有无人机平等，第一架完成后消失

### 竞态条件

多无人机同时操作同一格子时，结果取决于执行顺序：

```python
# 危险：多无人机可能重复浇水
if get_water() < 0.5:
    use_item(Items.Water)
```

### 常用模式

```python
# 有空闲无人机就生成，否则自己执行
if not spawn_drone(task):
    task()
```

---

## 区域管理设计原则

1. 区域是宝贵资源，按需分配，尽可能小粒度
2. 长期任务（如南瓜）申请后不释放
3. 短期任务（如巡逻）处理完立即释放
4. 分配策略：优先小块（4x4），紧张时降级（2x2 → 1x1）

---

# RAW (未整理)

以下是未经整理的原始知识，待后续学习整合。

---

## 多无人机原始文档

巨型农场让你能够使用多架无人机。

和以前一样，一开始只有一架无人机。额外的无人机必须先被生成，且程序终止后便会消失。
每架无人机运行的都是自己独立的程序。新无人机可以使用 spawn_drone(function) 函数生成。

```python
def drone_function():
    move(North)
    do_a_flip()

spawn_drone(drone_function)
```

以上代码会在运行 spawn_drone(function) 命令的无人机所在位置生成一架新的无人机。新无人机随后开始执行指定的函数，完成后便会自动消失。

示例：
```python
def harvest_column():
    for _ in range(get_world_size()):
        harvest()
        move(North)

while True:
    if spawn_drone(harvest_column):
        move(East)
```

为每架无人机传递不同方向：
```python
for dir in [North, East, South, West]:
    def task():
        move(dir)
        do_a_flip()
    spawn_drone(task)
```

并行 for_all 函数：
```python
def for_all(f):
    def row():
        for _ in range(get_world_size()-1):
            f()
            move(East)
        f()
    for _ in range(get_world_size()):
        if not spawn_drone(row):
            row()
        move(North)

for_all(harvest)
```

无共享内存示例：
```python
x = 0

def increment():
    global x
    x += 1

wait_for(spawn_drone(increment))
print(x)  # 打印 0，因为新无人机修改的是自己的 x 副本
```
