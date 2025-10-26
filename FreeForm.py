import re
from typing import Dict, Any, Callable, List, Union

# 类型别名
Expression = Union[str, int, float, List[Any]]
OperatorTable = Dict[str, Callable[[List[Expression]], Any]]


def tokenize(expression: str) -> List[str]:
    """
    将表达式字符串分割成标记(tokens)，支持字符串常量
    """
    tokens = []
    i = 0
    n = len(expression)

    while i < n:
        char = expression[i]

        # 跳过空白字符
        if char.isspace():
            i += 1
            continue

        # 处理字符串常量（单引号或双引号）
        if char in ['"', "'"]:
            quote_char = char
            j = i + 1
            # 查找匹配的结束引号，处理转义情况
            while j < n:
                if expression[j] == quote_char:
                    # 检查是否是转义的引号
                    if j > 0 and expression[j - 1] == '\\':
                        j += 1
                        continue
                    break
                j += 1

            if j >= n:
                raise ValueError(f"Unclosed string literal starting at position {i}")

            # 提取整个字符串（包含引号）
            token = expression[i:j + 1]
            tokens.append(token)
            i = j + 1
            continue

        # 处理括号
        if char in ['(', ')']:
            tokens.append(char)
            i += 1
            continue

        # 处理其他标记（运算符、变量、数字等）
        j = i
        while j < n and not expression[j].isspace() and expression[j] not in ['(', ')', '"', "'"]:
            j += 1

        if j > i:
            token = expression[i:j]
            tokens.append(token)
            i = j
        else:
            i += 1

    return tokens
# def tokenize(expression: str) -> List[str]:
#     """
#     将表达式字符串分割成标记(tokens)
#     """
#     # 在括号前后添加空格，然后分割
#     expression = re.sub(r'([()])', r' \1 ', expression)
#     # 移除多余空格并分割
#     tokens = [token for token in expression.split() if token]
#     return tokens


def parse(tokens: List[str]) -> Expression:
    """
    解析标记列表为表达式树
    """
    if not tokens:
        raise ValueError("Unexpected end of expression")

    token = tokens.pop(0)

    if token == '(':
        # 开始解析子表达式
        expr = []
        while tokens and tokens[0] != ')':
            expr.append(parse(tokens))
        if not tokens or tokens.pop(0) != ')':
            raise ValueError("Missing closing parenthesis")
        return expr
    elif token == ')':
        raise ValueError("Unexpected closing parenthesis")
    else:
        # 尝试解析为数字，否则作为字符串返回
        try:
            return int(token)
        except ValueError:
            try:
                return float(token)
            except ValueError:
                return token


def evaluate(
        expr: Expression,
        env: Dict[str, Any],
        op_table: OperatorTable
) -> Any:
    """
    递归计算表达式树
    """
    # 原子值处理（数字或变量）
    if not isinstance(expr, list) or len(expr) == 1:
        test = expr
        if isinstance(expr, list) and len(expr) == 1:
            test = expr[0]
        if isinstance(test, (int, float)):
            return test
        # 变量查找
        if (test[0] == '"' and test[-1] == '"') or (test[0] == '\'' and test[-1] == '\''):
            return test[1:-1]
        if not test in env:
            env[test] = 0
        return env[test]
        # raise ValueError(f"Undefined variable: {expr}")

    # 空列表处理
    if not expr:
        raise ValueError("Empty expression")

    # 获取运算符和操作数
    operator = expr[0]
    operands = expr[1:]

    # 检查运算符是否定义
    if operator not in op_table:
        raise ValueError(f"Undefined operator: {operator}")

    # 获取运算符函数并计算
    op_func = op_table[operator]
    evaluated_operands = [evaluate(op, env, op_table) for op in operands]
    return op_func(evaluated_operands)

def toBool(val)->bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, list):
        return len(val) > 0
    if isinstance(val, int):
        return val > 0
    if isinstance(val, str):
        return len(val) > 0
    pass

def switchFunc(ops):
    for i in range(0, len(ops), 2):
        if len(ops) <= i + 1:
            break
        op = ops[i]
        param = ops[i+1]
        if toBool(op):
            return param
    return ops[-1]

# 预定义基础运算符
DEFAULT_OPERATOR_TABLE: OperatorTable = {
    # 条件运算符
    'if': lambda ops: ops[1] if toBool(ops[0]) else ops[2],
    "switch": lambda ops: switchFunc(ops),

    # 字符串运算符
    'concat': lambda ops: ''.join(ops),
    'str-length': lambda ops: len(ops[0]),
    'str-equal': lambda ops: ops[0] == ops[1],

    # 比较运算符
    '<': lambda ops: ops[0] < ops[1],
    '>': lambda ops: ops[0] > ops[1],
    '<=': lambda ops: ops[0] <= ops[1],
    '>=': lambda ops: ops[0] >= ops[1],
    '==': lambda ops: ops[0] == ops[1],
    '!=': lambda ops: ops[0] != ops[1],

    # 算术运算符
    '+': lambda ops: sum(ops),
    '-': lambda ops: ops[0] - sum(ops[1:]) if len(ops) > 1 else -ops[0],
    '*': lambda ops: ops[0] * ops[1],
    '/': lambda ops: ops[0] / ops[1],
    'avg': lambda ops: sum(ops) / len(ops),
    'max': lambda ops: max(ops),
    'min': lambda ops: min(ops),

    # 逻辑运算符
    'and': lambda ops: all([toBool(o) for o in ops]),
    'or': lambda ops: any([toBool(o) for o in ops]),
    'not': lambda ops: not toBool(ops[0])
}


def calculate(
        expression: str,
        variables: Dict[str, Any],
        operators: OperatorTable = None
) -> Any:
    """
    计算前序表达式
    :param expression: 表达式字符串
    :param variables: 变量字典
    :param operators: 自定义运算符表（可选）
    :return: 计算结果
    """
    # 使用默认运算符表（如果未提供自定义）
    op_table = DEFAULT_OPERATOR_TABLE.copy()
    if operators is not None:
        for k in operators:
            op_table[k] = operators[k]

    # 添加变量名到运算符表（防止变量名被误识别为运算符）
    for var in variables:
        if var not in op_table:
            op_table[var] = lambda ops, v=var: variables[v]

    # 处理表达式
    tokens = tokenize(expression)
    if tokens[0] != '(':
        tokens = ['('] + tokens + [')']
    expr_tree = parse(tokens)
    return evaluate(expr_tree, variables, op_table)


def rename():
    dir = r"S:\downloads\[WEBHD.co]小猪佩奇全4季 国语全156集 Peppa.Pig.2015-2016.WEB-DL.S01-S04.1080P.H265.AAC-JBY@WEBHD\mp3"
    files = os.listdir(dir)
    for f in files:
        match = re.match(r'^粉红猪小妹 第[0-9]+集', f)
        matchs2 = re.match(r'^粉红猪小妹 第2季 第[0-9]+集', f)
        matchs3 = re.match(r'^粉红猪小妹 第3季 第[0-9]+集', f)
        matchs4 = re.match(r'^粉红猪小妹 第4季 第[0-9]+集', f)

        if match is not None and len(match.group()) > 0:
            name = match.group()
            season = 1
            esp = str(name).split("第")[-1].split('集')[0]
        elif matchs2 is not None and len(matchs2.group()) > 0:
            name = matchs2.group()
            season = 2
            esp = str(name).split("第")[-1].split('集')[0]
        elif matchs3 is not None and len(matchs3.group()) > 0:
            name = matchs3.group()
            season = 3
            esp = str(name).split("第")[-1].split('集')[0]
        elif matchs4 is not None and len(matchs4.group()) > 0:
            name = matchs4.group()
            season = 4
            esp = str(name).split("第")[-1].split('集')[0]

        newname = F"S{season}E{esp}.mp3"
        newpath = os.path.join(dir, newname)
        print(newpath)
        frompath = os.path.join(dir, f)
        shutil.move(frompath, newpath)
    print(files)
#
# def testTriton():
#     import torch
#     import triton
#     import triton.language as tl
#
#     @triton.jit
#     def add_kernel(x_ptr, y_ptr, output_ptr, n_elements, BLOCK_SIZE: tl.constexpr):
#         pid = tl.program_id(axis=0)
#         block_start = pid * BLOCK_SIZE
#         offsets = block_start + tl.arange(0, BLOCK_SIZE)
#         mask = offsets< n_elements
#         x = tl.load(x_ptr + offsets, mask=mask)
#         y = tl.load(y_ptr + offsets, mask=mask)
#         output = x + y
#         tl.store(output_ptr + offsets, output, mask=mask)
#
#     def add(x: torch.Tensor, y: torch.Tensor):
#         output = torch.empty_like(x)
#         assert  x.is_cuda and y.is_cuda and output.is_cuda
#         n_elements = output.numel()
#         grid = lambda  meta:(triton.cdiv(n_elements, meta["BLOCK_SIZE"]), )
#         add_kernel(x, y, output, n_elements, BLOCK_SIZE=1024)
#         return output
#
#     a = torch.rand(3, device="cuda")
#     b = a + a
#     b_comiled = add(a, a)
#     print(b_comiled - b)
#     pass

# 示例使用
if __name__ == "__main__":
    # testTriton()
    # rename()
    # 示例1: 基本运算
    expr1 = "\"ab \t c\""
    vars1 = {'a': 1, 'b': 2}
    result1 = calculate(expr1, vars1)
    print(f"Example 1: {expr1} = {result1}")  # 输出: 2

    # 示例2: 自定义运算符
    expr2 = "+ \"a\" \"b\""
    vars2 = {'a': 10, 'b': 20, 'c': 30}

    # 定义avg运算符
    custom_ops = {
        'avg': lambda ops: sum(ops) / len(ops),
        '+': lambda ops: ops[0] + ops[1]
    }
    result2 = calculate(expr2, vars2, custom_ops)
    print(f"Example 2: {expr2} = {result2}")  # 输出: 20.0

    # 示例3: 嵌套表达式
    expr3 = "== \"infj\" \"infj\""
    vars3 = {}
    result3 = calculate(expr3, vars3)
    print(f"Example 3: {expr3} = {result3}")  # 输出: 100