import argparse
import json
from datetime import datetime
from tabulate import tabulate


def parse_date(date_str):
    """Преобразует строку даты в объект datetime."""

    try:
        # Формат 2025-22-06 (22 июня 2025)
        return datetime.strptime(date_str, "%Y-%d-%m").date()
    except ValueError:
        print(
            "Неверный формат даты. Используйте YYYY-DD-MM"
            )
        return None


def process_log_file(file_path, results, filter_date=None):
    """Обрабатывает один файл логов с возможной фильтрацией по дате."""

    try:
        with open(file_path, 'r') as file:
            for line in file:
                try:
                    log = json.loads(line)

                    # Проверяем дату если нужно
                    if filter_date:
                        log_date_str = log.get('@timestamp', '')
                        try:
                            log_date = (datetime.fromisoformat(log_date_str)
                                        .date())
                            if log_date != filter_date:
                                continue
                        except (ValueError, TypeError):
                            continue

                    url = log.get('url', '')
                    response_time = log.get('response_time', 0)

                    if not url or response_time <= 0:
                        continue

                    endpoint = url.split('?')[0]

                    if endpoint not in results:
                        results[endpoint] = {'requests': 0, 'total_time': 0.0}

                    results[endpoint]['requests'] += 1
                    results[endpoint]['total_time'] += response_time

                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        print(f"⚠️ Файл {file_path} не найден, пропускаем")


def generate_average_report(results):
    """Генерирует отчёт со средним временем ответа"""
    report_data = []

    for endpoint in sorted(results.keys()):
        stats = results[endpoint]
        avg_time = stats['total_time'] / stats['requests']
        report_data.append([
            endpoint,
            stats['requests'],
            f"{avg_time:.3f} сек"
        ])

    headers = ["Эндпоинт", "Кол-во запросов", "Среднее время"]
    return tabulate(report_data, headers=headers, tablefmt="grid")


def main():
    parser = argparse.ArgumentParser(description='Анализатор логов')
    parser.add_argument('--file', required=True, nargs='+',
                        help='Файлы логов (можно несколько)')
    parser.add_argument('--report', choices=['average'],
                        default='average', help='Тип отчёта')
    parser.add_argument('--date', help='Фильтр по дате в формате YYYY-DD-MM')
    args = parser.parse_args()

    # Обрабатываем дату если указана
    filter_date = None
    if args.date:
        filter_date = parse_date(args.date)
        if filter_date is None:  # Если дата невалидная - выходим
            return

    all_results = {}

    for file_path in args.file:
        process_log_file(file_path, all_results, filter_date)

    if args.report == 'average':
        if not all_results:
            print("Нет данных для отображения. Проверьте фильтры или файлы.")
            return

        print("Отчёт по среднему времени ответа:", end='')
        if filter_date:
            print(f" (за {filter_date.strftime('%d.%m.%Y')})")
        else:
            print()

        print(generate_average_report(all_results))


if __name__ == '__main__':
    main()
