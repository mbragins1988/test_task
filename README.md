# test_task

### Описание 
Тестовое задание, скрипт Python читает файл и формирует отчет со списком эндпоинтов, количеством запросов по каждому эндпоинту и средним временем ответа. при формировании отчета есть возможность указать дату, чтобы сформировать отчет только по записям с указанной датой, например --date 2025-22-06. Для примера файлы логов example1.log и example2.log и скрины работы тестов в проекте. 

### Как запустить проект

Клонировать репозиторий:

```
git clone https://github.com/mbragins1988/test_task.git
```

Перейти в папку test_task

```
cd test_task
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```
для Windows
```
source venv/Scripts/activate
```
для Mac
```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
pip3 install -r requirements.txt
```

В директории test_task запустить скрипт:

```
python test_task.py --file <Путь к одному или нескольким файлам через пробел> --report average
```

В директории test_task запустить скрипт для условия с датой:

```
python test_task.py --file <Путь к одному или нескольким файлам через пробел> --report average --date <Дата в формате гггг-чч-мм>
```

Например

```
python test_task.py --file example1.log example2.log --report average
```
```
python test_task.py --file example1.log example2.log --report average --date 2025-22-06   
```

Запуск тестов test_test_task.py в директории test_task:

```
pytest
```

### Стек технологий:
- Python 3.8.10

### Авторы проекта
Михаил Брагин
