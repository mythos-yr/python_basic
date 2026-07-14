# 使用集合推导式对列表去重复,但是不保证顺序
ls = [1, 1, 1, 5, 5, 23, 17, 16, 17]

cols = {x for x in ls if x > 3}

print(cols)

# 测试提取字段值去重复
records = [
    {"role": "admin", "dept": "IT"},
    {"role": "user", "dept": "HR"},
    {"role": "admin", "dept": "IT"},
    {"role": "manager", "dept": "Finance"},
]
# 去重复角色
roles = {r["role"] for r in records}
# 去重复部门
depts = {d["dept"] for d in records}

print(roles,depts)

