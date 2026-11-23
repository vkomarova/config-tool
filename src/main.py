import argparse
import sys

from src.translator import ConfigError, to_yaml, translate


def parse_args():
    """Читает ключи командной строки."""
    parser = argparse.ArgumentParser(
        description="Переводит учебный конфигурационный язык в YAML"
    )
    parser.add_argument(
        "-o", "--output", required=True,
        help="путь к выходному YAML-файлу"
    )
    return parser.parse_args()


def main():
    """Читает текст из stdin и записывает YAML в файл."""
    args = parse_args()
    sys.stdin.reconfigure(encoding="utf-8")
    text = sys.stdin.read()
    try:
        data = translate(text)
    except ConfigError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        sys.exit(1)
    with open(args.output, "w", encoding="utf-8") as file:
        file.write(to_yaml(data))


if __name__ == "__main__":
    main()
