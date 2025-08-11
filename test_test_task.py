import pytest
from datetime import date, datetime
from unittest.mock import patch, mock_open
import json
import test_task


# Тестовые данные
TEST_LOG_ENTRY = ('{"@timestamp": "2025-06-22T12:00:00+00:00", '
                  '"url": "/api/test", "response_time": 0.1}\n')
TEST_LOG_ENTRY_INVALID = '{"invalid": "data"}\n'
TEST_LOG_ENTRY_NO_TIME = '{"url": "/api/test"}\n'
TEST_LOG_ENTRY_NO_URL = ('{"@timestamp": "2025-06-22T12:00:00+00:00", '
                         '"response_time": 0.1}\n')
TEST_LOG_ENTRY_ZERO_TIME = ('{"@timestamp": "2025-06-22T12:00:00+00:00", '
                            '"url": "/api/test", "response_time": 0}\n')


def test_parse_date_valid():
    """Тест корректного парсинга даты."""

    assert test_task.parse_date("2025-22-06") == date(2025, 6, 22)


def test_parse_date_invalid():
    """Тест некорректной даты."""

    assert test_task.parse_date("invalid-date") is None


def test_process_log_file_success():
    """Тест успешной обработки лог-файла."""

    results = {}
    test_data = TEST_LOG_ENTRY * 3

    with patch("builtins.open", mock_open(read_data=test_data)):
        test_task.process_log_file("test.log", results)

    assert "/api/test" in results
    assert results["/api/test"]["requests"] == 3
    assert results["/api/test"]["total_time"] == pytest.approx(0.3)


def test_process_log_file_with_date_filter():
    """Тест фильтрации по дате."""

    results = {}
    test_data = TEST_LOG_ENTRY

    with patch("builtins.open", mock_open(read_data=test_data)):
        test_task.process_log_file(
            "test.log", results, filter_date=date(2025, 6, 22)
            )

    assert "/api/test" in results


def test_process_log_file_wrong_date():
    """Тест неподходящей даты."""

    results = {}
    test_data = TEST_LOG_ENTRY

    with patch("builtins.open", mock_open(read_data=test_data)):
        test_task.process_log_file(
            "test.log", results, filter_date=date(2024, 1, 1)
            )

    assert not results


def test_process_log_file_invalid_json():
    """Тест невалидного JSON."""

    results = {}
    test_data = TEST_LOG_ENTRY_INVALID

    with patch("builtins.open", mock_open(read_data=test_data)):
        test_task.process_log_file("test.log", results)

    assert not results


def test_process_log_file_missing_fields():
    """Тест отсутствия обязательных полей."""

    results = {}
    test_data = TEST_LOG_ENTRY_NO_TIME

    with patch("builtins.open", mock_open(read_data=test_data)):
        test_task.process_log_file("test.log", results)

    assert not results


def test_process_log_file_missing_url():
    """Тест отсутствия URL."""

    results = {}
    test_data = TEST_LOG_ENTRY_NO_URL

    with patch("builtins.open", mock_open(read_data=test_data)):
        test_task.process_log_file("test.log", results)

    assert not results


def test_process_log_file_zero_time():
    """Тест нулевого времени ответа."""

    results = {}
    test_data = TEST_LOG_ENTRY_ZERO_TIME

    with patch("builtins.open", mock_open(read_data=test_data)):
        test_task.process_log_file("test.log", results)

    assert not results


def test_process_log_file_not_found(capsys):
    """Тест отсутствия файла."""

    results = {}
    test_task.process_log_file("nonexistent.log", results)
    captured = capsys.readouterr()
    assert "не найден" in captured.out


def test_generate_average_report():
    """Тест генерации отчёта."""

    test_data = {
        "/api/test": {"requests": 2, "total_time": 0.3},
        "/api/users": {"requests": 1, "total_time": 0.15}
    }
    report = test_task.generate_average_report(test_data)
    assert "/api/test" in report
    assert "0.150 сек" in report


def test_generate_average_report_empty():
    """Тест пустого отчёта."""

    report = test_task.generate_average_report({})
    assert "Эндпоинт" in report


def test_main_success(capsys):
    """Тест main с успешным выполнением."""

    test_args = ["test_task.py", "--file", "test.log", "--report", "average"]
    test_data = TEST_LOG_ENTRY * 2

    with patch("builtins.open", mock_open(read_data=test_data)):
        with patch("sys.argv", test_args):
            test_task.main()

    captured = capsys.readouterr()
    assert "Отчёт по среднему времени ответа" in captured.out
    assert "/api/test" in captured.out


def test_main_with_date_filter(capsys):
    """Тест main с фильтром по дате."""

    test_args = ["test_task.py", "--file", "test.log",
                 "--report", "average", "--date", "2025-22-06"]
    test_data = TEST_LOG_ENTRY

    with patch("builtins.open", mock_open(read_data=test_data)):
        with patch("sys.argv", test_args):
            test_task.main()

    captured = capsys.readouterr()
    assert "22.06.2025" in captured.out


def test_main_invalid_date(capsys):
    """Тест main с невалидной датой."""

    test_args = ["test_task.py", "--file", "test.log",
                 "--report", "average", "--date", "invalid"]

    with patch("sys.argv", test_args):
        test_task.main()

    captured = capsys.readouterr()
    assert "Неверный формат даты" in captured.out


def test_main_no_data(capsys):
    """Тест main без данных."""

    test_args = ["test_task.py", "--file", "empty.log", "--report", "average"]

    with patch("builtins.open", mock_open(read_data="")):
        with patch("sys.argv", test_args):
            test_task.main()

    captured = capsys.readouterr()
    assert "Нет данных" in captured.out
