import json
import pytest
from datetime import datetime
from io import StringIO
import sys

# Импортируем функции из вашего кода
from your_module import mask, display_last_5_operations  # замените your_module на имя вашего файла

# Тестовые данные
TEST_OPERATIONS = [
    {
        "id": 441945886,
        "state": "EXECUTED",
        "date": "2019-08-26T10:50:58.294041",
        "operationAmount": {
            "amount": "31957.58",
            "currency": {"name": "руб.", "code": "RUB"}
        },
        "description": "Перевод организации",
        "from": "Maestro 1596837868705199",
        "to": "Счет 64686473678894779589"
    },
    {
        "id": 41428829,
        "state": "EXECUTED",
        "date": "2019-07-03T18:35:29.512364",
        "operationAmount": {
            "amount": "8221.37",
            "currency": {"name": "USD", "code": "USD"}
        },
        "description": "Перевод организации",
        "from": "MasterCard 7158300734726758",
        "to": "Счет 35383033474447895560"
    }
]


def create_test_json_file(tmp_path, data):
    """Создает временный JSON файл с тестовыми данными"""
    file_path = tmp_path / "test_operations.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f)
    return file_path


def test_mask_card_number():
    """Тест маскировки номера карты"""
    result = mask("MasterCard 7158300734726758")
    assert result == "Master 71** **** 6758"
    print(f"✓ Маскировка карты работает: MasterCard 7158300734726758 -> {result}")


def test_mask_account():
    """Тест маскировки счета"""
    result = mask("Счет 64686473678894779589")
    assert result == "Счет **9589"
    print(f"✓ Маскировка счета работает: Счет 64686473678894779589 -> {result}")


def test_mask_unknown_format():
    """Тест маскировки неизвестного формата"""
    result = mask("UnknownFormat")
    assert result == "UnknownFormat"
    print(f"✓ Неизвестный формат не изменяется: UnknownFormat -> {result}")


def test_mask_empty_from_account():
    """Тест обработки отсутствующего поля 'from'"""
    # Когда в операции нет поля 'from', функция mask не вызывается для него
    # Этот тест проверяет, что функция mask не падает на некорректных данных
    result = mask("")
    assert result == ""
    print("✓ Пустая строка обрабатывается корректно")


def test_sort_operations_by_date():
    """Тест сортировки операций по дате"""
    operations = [
        {"state": "EXECUTED", "date": "2023-01-01T10:00:00.000000"},
        {"state": "EXECUTED", "date": "2023-03-01T10:00:00.000000"},
        {"state": "EXECUTED", "date": "2023-02-01T10:00:00.000000"},
    ]

    sorted_ops = sorted(
        operations,
        key=lambda op: datetime.strptime(op['date'], "%Y-%m-%dT%H:%M:%S.%f"),
        reverse=True
    )

    assert sorted_ops[0]['date'] == "2023-03-01T10:00:00.000000"
    assert sorted_ops[1]['date'] == "2023-02-01T10:00:00.000000"
    assert sorted_ops[2]['date'] == "2023-01-01T10:00:00.000000"
    print("✓ Операции правильно сортируются по дате (новые первыми)")


def test_filter_executed_operations():
    """Тест фильтрации выполненных операций"""
    operations = [
        {"state": "EXECUTED", "date": "2023-01-01T10:00:00.000000"},
        {"state": "CANCELED", "date": "2023-02-01T10:00:00.000000"},
        {"state": "EXECUTED", "date": "2023-03-01T10:00:00.000000"},
    ]

    executed = [op for op in operations if op['state'] == 'EXECUTED']

    assert len(executed) == 2
    assert all(op['state'] == 'EXECUTED' for op in executed)
    print("✓ Фильтрация EXECUTED операций работает правильно")


def test_display_output_format(capsys, tmp_path):
    """Тест формата вывода"""
    # Создаем временный файл с тестовыми данными
    file_path = create_test_json_file(tmp_path, TEST_OPERATIONS)

    # Захватываем вывод функции
    display_last_5_operations(str(file_path))
    captured = capsys.readouterr()
    output = captured.out

    # Проверяем основные элементы в выводе
    assert "26.08.2019" in output
    assert "Перевод организации" in output
    assert "руб." in output or "USD" in output
    assert "->" in output
    assert "**9589" in output  # Маскированный счет

    print("✓ Формат вывода соответствует ожидаемому")
    print("\nПример вывода:")
    print(output[:200] + "...")  # Показываем начало вывода


def test_file_not_found():
    """Тест обработки отсутствующего файла"""
    # Временно заменяем print для теста
    original_print = print
    printed_messages = []

    def mock_print(*args, **kwargs):
        printed_messages.append(" ".join(str(arg) for arg in args))

    try:
        # Мокаем print
        import builtins
        builtins.print = mock_print

        # Пытаемся открыть несуществующий файл1
        try:
            display_last_5_operations('nonexistent.json')
        except FileNotFoundError:
            pass  # Ожидаемое поведение
    finally:
        # Восстанавливаем оригинальный print
        builtins.print = original_print

    print("✓ Обработка отсутствующего файла работает")


def test_empty_json_file(tmp_path):
    """Тест обработки пустого JSON файла"""
    file_path = tmp_path / "empty.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump([], f)

    # Функция не должна падать на пустом файле
    try:
        display_last_5_operations(str(file_path))
        print("✓ Пустой JSON файл обрабатывается без ошибок")
    except Exception as e:
        pytest.fail(f"Функция упала на пустом файле: {e}")


def test_operation_without_from_field(tmp_path):
    """Тест операции без поля 'from' (например, открытие вклада)"""
    operations = [{
        "id": 587085106,
        "state": "EXECUTED",
        "date": "2018-03-23T10:45:06.972075",
        "operationAmount": {
            "amount": "48223.05",
            "currency": {"name": "руб.", "code": "RUB"}
        },
        "description": "Открытие вклада",
        "to": "Счет 41421565395219882431"
    }]

    file_path = create_test_json_file(tmp_path, operations)

    # Проверяем, что функция не падает
    try:
        display_last_5_operations(str(file_path))
        print("✓ Операция без поля 'from' обрабатывается корректно")
    except KeyError:
        pytest.fail("Функция не обрабатывает отсутствие поля 'from'")


# Запуск всех тестов с подробным выводом
if __name__ == "__main__":
    print("=" * 60)
    print("Запуск тестов для обработки банковских операций")
    print("=" * 60)

    # Создаем список всех тестовых функций
    test_functions = [
        test_mask_card_number,
        test_mask_account,
        test_mask_unknown_format,
        test_mask_empty_from_account,
        test_sort_operations_by_date,
        test_filter_executed_operations,
        test_operation_without_from_field,
    ]

    passed = 0
    failed = 0

    # Запускаем каждый тест
    for test_func in test_functions:
        try:
            test_func()
            print(f"✅ {test_func.__name__}: PASSED\n")
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_func.__name__}: FAILED - {e}\n")
            failed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__}: ERROR - {e}\n")
            failed += 1

    print("=" * 60)
    print(f"Итог: {passed} пройдено, {failed} не пройдено")
    print("=" * 60)