# Транслятор учебного конфигурационного языка в YAML

## 1. Общее описание

Инструмент командной строки переводит текст на учебном конфигурационном
языке в формат YAML.

- Входной текст читается из **стандартного ввода**.
- Результат на YAML записывается в **файл**, путь к которому задаётся
  ключом `-o` (`--output`).
- При синтаксических ошибках выводится сообщение с номером строки и столбца.

Для синтаксического разбора используется библиотека **pyparsing**,
для вывода - **PyYAML**.

### Синтаксис языка

Числа (`[+-]?\d+\.?\d*[eE][+-]?\d+`):

```
1e2   2.5E1   -1.5e-3   +3.e0
```

Строки:

```
'Это строка'
```

Массивы:

```
[ значение значение значение ... ]
```

Словари:

```
begin
  имя := значение;
  имя := значение;
end
```

Имена: `[_a-zA-Z][_a-zA-Z0-9]*`

Значения: числа, строки, массивы, словари.

Объявление константы на этапе трансляции:

```
значение -> имя;
```

Вычисление константного выражения (постфиксная форма):

```
@(имя 1e0 +)
```

Операции и функции в выражениях: `+` (сложение), `-` (вычитание),
`*` (умножение), `ord()` (код символа, пример: `@('A' ord)` даёт `65`).

## 2. Описание функций и настроек

Ключи командной строки:

| Ключ | Описание |
|------|----------|
| `-o`, `--output` | путь к выходному YAML-файлу (обязательный) |
| `-h`, `--help` | справка |

Файл `src/translator.py`:

| Функция / класс | Описание |
|-----------------|----------|
| `translate(text)` | переводит текст конфигурации в данные Python |
| `to_yaml(data)` | превращает данные Python в текст YAML |
| `Translator` | хранит грамматику и таблицу констант |
| `Translator.build_parser()` | описывает грамматику языка |
| `Translator.save_constant()` | запоминает константу |
| `Translator.get_constant()` | возвращает значение константы |
| `evaluate_postfix(tokens)` | вычисляет постфиксное выражение через стек |
| `apply_operation(stack, name)` | применяет операцию к вершине стека |
| `to_number`, `to_string`, `to_array`, `to_dict`, `to_operation` | превращают разобранный текст в данные |
| `ConfigError` | ошибка в тексте конфигурации |

Файл `src/main.py`:

| Функция | Описание |
|---------|----------|
| `parse_args()` | читает ключи командной строки |
| `main()` | читает stdin, переводит текст и записывает YAML в файл |

## 3. Команды для сборки проекта и запуска тестов

Установка зависимостей:

```
make install
```

или

```
pip install -r requirements.txt
```

Запуск тестов:

```
make test
```

или

```
python -m unittest discover -s tests -v
```

Перевод примеров из папки `examples`:

```
make example
```

Запуск программы:

```
./run.sh -o result.yaml < examples/web_server.txt
```

В Windows:

```
run.bat -o result.yaml < examples\web_server.txt
```

## 4. Примеры использования

### Пример 1. Настройки веб-сервера (`examples/web_server.txt`)

```
8.0e3 -> base_port;
4.0e0 -> workers;

begin
  name := 'my-site';
  host := '127.0.0.1';
  port := @(base_port 8.0e1 +);
  admin_port := @(base_port 1.0e0 +);
  threads := @(workers 2.0e0 *);
  timeout := 3.0e1;
  locations := [ '/' '/api' '/static' ];
  database := begin
    user := 'admin';
    pool := @(workers 1.0e0 -);
  end;
end
```

Результат:

```yaml
name: my-site
host: 127.0.0.1
port: 8080.0
admin_port: 8001.0
threads: 8.0
timeout: 30.0
locations:
- /
- /api
- /static
database:
  user: admin
  pool: 3.0
```

### Пример 2. Настройки игры (`examples/game.txt`)

```
1.0e2 -> max_health;
'W' -> up_key;

begin
  title := 'Space Adventure';
  player := begin
    health := @(max_health);
    armor := @(max_health 5.0e-1 *);
    speed := 2.5e0;
  end;
  controls := begin
    up := @(up_key ord);
    down := @('S' ord);
  end;
  levels := [
    begin name := 'Moon'; enemies := 5.0e0; end
    begin name := 'Mars'; enemies := @(5.0e0 3.0e0 *); end
  ];
end
```

Результат:

```yaml
title: Space Adventure
player:
  health: 100.0
  armor: 50.0
  speed: 2.5
controls:
  up: 87
  down: 83
levels:
- name: Moon
  enemies: 5.0
- name: Mars
  enemies: 15.0
```

### Пример ошибки

```
$ echo "begin a := 1e0 end" | ./run.sh -o result.yaml
Ошибка: Синтаксическая ошибка (строка 1, столбец 7): Expected Keyword 'end'
```
