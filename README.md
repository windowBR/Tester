# ***Vibe Coding 太好用啦***
本脚本几乎完全由 AI 编写，*如果写得不好，那一定是 AI 的问题*
## 项目由来
本项目来源是因为最近在写 CS61B 的 Gitlet，但是 UCB 官方提供的测试脚本我用不明白也懒得去弄明白（理直气壮

因此我决定让 AI 自己写一个符合我自己要求的测试运行器，它功能十分简陋，但足够简单易懂，适合十分轻量场景的使用

## 使用示例
脚本接收一个参数，即测试模板的路径
```
$ python3 ./test_runner.py ./UnitTest/template.in
--- Running: Step 1 ---
Command: echo "helloworld!"
PASS
STDOUT:
helloworld!
MATCH: output matches expected
----------------------------------------
--- Running: Step 2 ---
Command: echo "line 1"
echo "line 2"
PASS
STDOUT:
line 1
line 2
MATCH: output matches expected
----------------------------------------
--- Running: Step 3 ---
Code:
print("line 3")
print("line 4")

PASS
STDOUT:
line 3
line 4
MATCH: output matches expected
----------------------------------------
--- Running: Step 4 ---
Code:
print("DEBUG: 应当不纳入测试")
print("line 5")

PASS
STDOUT:
DEBUG: 应当不纳入测试
line 5
MATCH: output matches expected
----------------------------------------
--- Running: Step 5 ---
Command: echo "DEBUG: 同上"
echo "line 6"
PASS
STDOUT:
DEBUG: 同上
line 6
MATCH: output matches expected
----------------------------------------

--- Test Summary ---
5 passed, 0 failed
```

### 测试模板语法
使用 `sh> ` 后接 sh 脚本

使用 `py> ` 后接 python 脚本

使用 `<<< ` 后接预期输出

以上语法均支持多行输入输出

使用 `# ` 开头代表单行注释

若输出为 `DEBUG:` 开头，则不将该输出与预期输出对比，将无视该输出

可参考提供的测试模板
```
# 单行测试
sh> echo "helloworld!"
<<< helloworld!

# 多行测试
sh> echo "line 1"
    echo "line 2"
<<< line 1
    line 2

# 多行 py 测试
py> print("line 3")
    print("line 4")
<<< line 3
    line 4

# DEBUG 测试
py> print("DEBUG: 应当不纳入测试")
    print("line 5")
<<< line 5

sh> echo "DEBUG: 同上"
    echo "line 6"
<<< line 6
```

什么你觉得输入输出语法有点啰嗦？这是因为这样刚好所有输入输出都缩进四个空格，让我看着更加舒服，没有什么特殊原因也不打算改（