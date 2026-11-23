import operator

import pyparsing as pp
import yaml

BINARY_OPERANDS = 2
UNARY_OPERANDS = 1
RESULT_COUNT = 1

OPERATIONS = {
    "+": (BINARY_OPERANDS, operator.add),
    "-": (BINARY_OPERANDS, operator.sub),
    "*": (BINARY_OPERANDS, operator.mul),
    "ord": (UNARY_OPERANDS, ord),
}


class ConfigError(Exception):
    """Ошибка в тексте конфигурации."""


def to_number(tokens):

    return float(tokens[0])


def to_string(tokens):
    return tokens[0][1:-1]


def to_array(tokens):
    return [list(tokens)]


def to_dict(tokens):
    result = {}
    for pair in tokens:
        result[pair[0]] = pair[1]
    return [result]


def to_operation(tokens):
    return [("operation", tokens[0])]


def apply_operation(stack, name):
    count, function = OPERATIONS[name]
    if len(stack) < count:
        raise ConfigError(f"Недостаточно операндов для '{name}'")
    args = stack[-count:]
    del stack[-count:]
    try:
        stack.append(function(*args))
    except TypeError:
        raise ConfigError(f"Неверные операнды для '{name}': {args}")


def evaluate_postfix(tokens):
    stack = []
    for item in tokens:
        if isinstance(item, tuple):
            apply_operation(stack, item[1])
        else:
            stack.append(item)
    if len(stack) != RESULT_COUNT:
        raise ConfigError("Выражение должно давать ровно одно значение")
    return [stack[0]]


class Translator:

    def __init__(self):
        self.constants = {}
        self.parser = self.build_parser()

    def get_constant(self, tokens):
        name = tokens[0]
        if name not in self.constants:
            raise ConfigError(f"Неизвестная константа '{name}'")
        return [self.constants[name]]

    def save_constant(self, tokens):
        self.constants[tokens[1]] = tokens[0]
        return []

    def build_parser(self):
        number = pp.Regex(r"[+-]?\d+\.?\d*[eE][+-]?\d+")
        number.set_parse_action(to_number)
        number.set_name("число")
        string = pp.Regex(r"'[^']*'")
        string.set_parse_action(to_string)
        string.set_name("строка")
        name = pp.Regex(r"[_a-zA-Z][_a-zA-Z0-9]*")
        name.set_name("имя")
        value = pp.Forward()
        value.set_name("значение")

        array = pp.Suppress("[") + pp.ZeroOrMore(value) + pp.Suppress("]")
        array.set_parse_action(to_array)
        array.set_name("массив")

        pair = pp.Group(name + pp.Suppress(":=") + value + pp.Suppress(";"))
        dictionary = (pp.Suppress(pp.Keyword("begin")) + pp.ZeroOrMore(pair)
                      + pp.Suppress(pp.Keyword("end")))
        dictionary.set_parse_action(to_dict)
        dictionary.set_name("словарь")

        operation = pp.one_of("+ - *") | pp.Keyword("ord")
        operation.set_parse_action(to_operation)
        reference = name.copy()
        reference.set_parse_action(self.get_constant)
        item = number | string | operation | reference
        expression = (pp.Suppress("@(") + pp.OneOrMore(item)
                      + pp.Suppress(")"))
        expression.set_parse_action(evaluate_postfix)
        expression.set_name("выражение")

        value <<= expression | array | dictionary | number | string
        declaration = value + pp.Suppress("->") + name + pp.Suppress(";")
        declaration.set_parse_action(self.save_constant)
        return pp.ZeroOrMore(declaration) + value


def translate(text):
    translator = Translator()
    try:
        result = translator.parser.parse_string(text, parse_all=True)
    except pp.ParseException as error:
        raise ConfigError(
            f"Синтаксическая ошибка (строка {error.lineno}, "
            f"столбец {error.col}): {error.msg}"
        )
    return result[0]


def to_yaml(data):
    return yaml.dump(data, allow_unicode=True, sort_keys=False)
