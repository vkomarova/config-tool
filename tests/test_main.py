import os
import subprocess
import sys
import tempfile
import unittest


def run_tool(text, output):
    """Запускает программу и передаёт ей текст через stdin."""
    return subprocess.run(
        [sys.executable, "-m", "src.main", "-o", output],
        input=text, capture_output=True, text=True, encoding="utf-8"
    )


class TestMain(unittest.TestCase):
    """Тесты программы целиком."""

    def test_writes_yaml_file(self):
        """Результат записывается в файл."""
        with tempfile.TemporaryDirectory() as folder:
            output = os.path.join(folder, "out.yaml")
            run_tool("begin name := 'test'; end", output)
            with open(output, encoding="utf-8") as file:
                self.assertEqual(file.read(), "name: test\n")

    def test_error_message(self):
        """При ошибке выводится сообщение."""
        with tempfile.TemporaryDirectory() as folder:
            output = os.path.join(folder, "out.yaml")
            result = run_tool("begin", output)
            self.assertIn("Ошибка", result.stderr)
            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
