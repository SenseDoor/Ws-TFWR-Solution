# The Farmer Was Replaced - Game Knowledge

Wiki: https://thefarmerwasreplaced.wiki.gg/

---

## List (列表)

列表可以通过 1 个变量存储多个值。

```python
list = [2, True, Items.Hay]
empty_list = []
```

通过索引访问元素（从 0 开始）：
```python
list = [Entities.Tree, Entities.Carrot, Entities.Pumpkin]
plant(list[1])  # 种植胡萝卜
```

遍历列表：
```python
list = [4, 7, 2, 5]
sum = 0
for number in list:
    sum += number
# sum 现在是 18
```

### 列表方法

| 方法 | 说明 | 示例 |
|------|------|------|
| `list.append(elem)` | 末尾添加元素 | `[2,6,12].append(7)` → `[2,6,12,7]` |
| `list.remove(elem)` | 移除首次出现的元素 | `[1,2,4,2].remove(2)` → `[1,4,2]` |
| `list.insert(i, elem)` | 在索引处插入 | `[1,3].insert(1, 2)` → `[1,2,3]` |
| `list.pop()` | 移除最后一项 | `[3,5,8].pop()` → `[3,5]` |
| `list.pop(i)` | 移除索引处元素 | `[3,5,8].pop(1)` → `[3,8]` |
| `len(list)` | 返回长度 | `len([3,2,1])` → `3` |

### 引用语义

列表赋值不会复制，多个变量引用同一对象：
```python
a = [1, 2]
b = a
b.pop()
# a 和 b 现在都是 [1]
```

---

## Dict (字典)

字典将键 (key) 映射到值 (value)。

```python
right_of = {North:East, East:South, South:West, West:North}
entity_dict = {(x,y): get_entity_type()}
```

### 基本操作

| 操作 | 说明 |
|------|------|
| `dict[key]` | 获取值 |
| `dict[key] = value` | 设置值（key 存在则覆盖） |
| `dict.pop(key)` | 删除键值对 |
| `key in dict` | 检查 key 是否存在 |

### 遍历字典

```python
for key in dict:
    value = dict[key]
```

注意：迭代顺序不保证。

---

## Syntax Limitations (语法限制)

此游戏使用简化版 Python，以下语法**不支持**：

- `del` 语句 - 使用 `dict.pop(key)` 或 `list.remove(elem)` 代替
- `"""..."""` 多行字符串/docstring - 只能用 `#` 注释
- `lambda` 表达式 - 使用普通函数定义代替
- `from folder import module` 文件夹导入 - 只支持根目录 `import module`
- `global a, b` 多变量 - 需拆分为 `global a` 和 `global b`

---
