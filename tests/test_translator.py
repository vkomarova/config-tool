import unittest

from src.translator import ConfigError, to_yaml, translate


class TestNumbers(unittest.TestCase):
    """Тесты чисел."""

    def test_simple(self):
        """Число с экспонентой."""
        self.assertEqual(translate("1e2"), 100.0)

    def test_with_point(self):
        """Число с дробной частью."""
        self.assertEqual(translate("2.5E1"), 25.0)

    def test_point_without_digits(self):
        """Число с точкой без цифр после неё."""
        self.assertEqual(translate("3.e0"), 3.0)

    def test_signs(self):
        """Знаки у числа и у экспоненты."""
        self.assertEqual(translate("-1.5e-1"), -0.15)
        self.assertEqual(translate("+2e+1"), 20.0)

    def test_without_exponent(self):
        """Число без экспоненты — ошибка."""
        with self.assertRaises(ConfigError):
            translate("12")


class TestStrings(unittest.TestCase):
    """Тесты строк."""

    def test_string(self):
        """Обычная строка."""
        self.assertEqual(translate("'Это строка'"), "Это строка")

    def test_empty_string(self):
        """Пустая строка."""
        self.assertEqual(translate("''"), "")

    def test_unclosed_string(self):
        """Незакрытая строка — ошибка."""
        with self.assertRaises(ConfigError):
            translate("'abc")


class TestArrays(unittest.TestCase):
    """Тесты массивов."""

    def test_array(self):
        """Массив из разных значений."""
        self.assertEqual(translate("[ 1e0 'a' 2e0 ]"), [1.0, "a", 2.0])

    def test_empty_array(self):
        """Пустой массив."""
        self.assertEqual(translate("[ ]"), [])

    def test_nested_array(self):
        """Массив внутри массива."""
        self.assertEqual(translate("[ [ 1e0 ] [ ] ]"), [[1.0], []])

    def test_dict_in_array(self):
        """Словарь внутри массива."""
        text = "[ begin a := 1e0; end ]"
        self.assertEqual(translate(text), [{"a": 1.0}])

    def test_unclosed_array(self):
        """Незакрытый массив — ошибка."""
        with self.assertRaises(ConfigError):
            translate("[ 1e0")


class TestDicts(unittest.TestCase):
    """Тесты словарей."""

    def test_dict(self):
        """Словарь из нескольких пар."""
        text = "begin\n  a := 1e0;\n  _b2 := 'x';\nend"
        self.assertEqual(translate(text), {"a": 1.0, "_b2": "x"})

    def test_empty_dict(self):
        """Пустой словарь."""
        self.assertEqual(translate("begin end"), {})

    def test_nested_dict(self):
        """Словарь и массив внутри словаря."""
        text = "begin inner := begin x := [ 1e0 ]; end; end"
        self.assertEqual(translate(text), {"inner": {"x": [1.0]}})

    def test_missing_semicolon(self):
        """Пропущена точка с запятой — ошибка."""
        with self.assertRaises(ConfigError):
            translate("begin a := 1e0 end")

    def test_bad_name(self):
        """Имя не может начинаться с цифры."""
        with self.assertRaises(ConfigError):
            translate("begin 1a := 1e0; end")


class TestConstants(unittest.TestCase):
    """Тесты объявления констант."""

    def test_declare_and_use(self):
        """Объявление константы и её использование."""
        self.assertEqual(translate("5e0 -> x; @(x)"), 5.0)

    def test_constant_array(self):
        """Константа может хранить массив."""
        self.assertEqual(translate("[ 1e0 ] -> a; @(a)"), [1.0])

    def test_constant_from_expression(self):
        """Константа из выражения с другой константой."""
        text = "2e0 -> a; @(a a *) -> b; @(b)"
        self.assertEqual(translate(text), 4.0)

    def test_unknown_constant(self):
        """Неизвестная константа — ошибка."""
        with self.assertRaises(ConfigError):
            translate("@(nothing)")

    def test_missing_semicolon(self):
        """Объявление без точки с запятой — ошибка."""
        with self.assertRaises(ConfigError):
            translate("1e0 -> a 1e0")


class TestExpressions(unittest.TestCase):
    """Тесты константных выражений."""

    def test_add(self):
        """Сложение."""
        self.assertEqual(translate("1e0 -> x; @(x 1e0 +)"), 2.0)

    def test_subtract(self):
        """Вычитание."""
        self.assertEqual(translate("@(5e0 2e0 -)"), 3.0)

    def test_multiply(self):
        """Умножение."""
        self.assertEqual(translate("@(3e0 4e0 *)"), 12.0)

    def test_ord(self):
        """Функция ord()."""
        self.assertEqual(translate("@('A' ord)"), 65)

    def test_complex(self):
        """Несколько операций подряд."""
        self.assertEqual(translate("@(1e0 2e0 + 3e0 *)"), 9.0)

    def test_negative_number(self):
        """Отрицательное число внутри выражения."""
        self.assertEqual(translate("@(1e0 -2e0 +)"), -1.0)

    def test_in_dict_and_array(self):
        """Выражения внутри словаря и массива."""
        text = "begin a := [ @(1e0 1e0 +) ]; end"
        self.assertEqual(translate(text), {"a": [2.0]})

    def test_not_enough_operands(self):
        """Не хватает операндов — ошибка."""
        with self.assertRaises(ConfigError):
            translate("@(1e0 +)")

    def test_too_many_values(self):
        """Лишние значения в выражении — ошибка."""
        with self.assertRaises(ConfigError):
            translate("@(1e0 2e0)")

    def test_wrong_types(self):
        """Сложение числа и строки — ошибка."""
        with self.assertRaises(ConfigError):
            translate("@(1e0 'a' +)")

    def test_ord_wrong_string(self):
        """ord() от длинной строки — ошибка."""
        with self.assertRaises(ConfigError):
            translate("@('ab' ord)")

    def test_unknown_operation(self):
        """Неизвестная операция — ошибка."""
        with self.assertRaises(ConfigError):
            translate("@(1e0 2e0 /)")


class TestYaml(unittest.TestCase):
    """Тесты вывода в YAML."""

    def test_yaml(self):
        """Словарь превращается в YAML."""
        data = translate("begin a := 1e0; b := [ 'x' ]; end")
        self.assertEqual(to_yaml(data), "a: 1.0\nb:\n- x\n")

    def test_examples(self):
        """Примеры из папки examples переводятся без ошибок."""
        for path in ["examples/web_server.txt", "examples/game.txt"]:
            with open(path, encoding="utf-8") as file:
                self.assertIsInstance(translate(file.read()), dict)


if __name__ == "__main__":
    unittest.main()
