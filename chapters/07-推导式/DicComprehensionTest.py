# 测试从列表构建字典
from curses.ascii import isupper

keys = ["name", "age", "gender", "address"]
values = ["Jack", "18", "M", "广州 白云"]

person_dic = {k: v for k, v in zip(keys, values)}
print(person_dic)

# 测试字典键值呼唤
ex_dic = {"Status": "ok", "StatusCode": 200}
ex_revert_dic = {k: v for v, k in ex_dic.items()}
print(ex_revert_dic)

# 测试过滤变换字典
score_dic = {"Jack": 70, "Alice": 90, "Mike": 50}
score_grade_dic = {name: "A" if score >= 90 else "B" if score >= 70 else "C" for name, score in score_dic.items() if
                   score > 60}
print(score_grade_dic)

# 从 Java 风格配置转为 Python 风格
java_config = {"dbHost": "localhost", "dbPort": 5432, "maxPoolSize": 50}


def camel_to_snake(s):
    return "".join("_" + c.lower() if isupper(c) else c for c in s)

config_dic = {camel_to_snake(k):v for k,v in java_config.items()}

print(config_dic)

