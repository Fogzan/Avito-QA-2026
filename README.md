# Avito-QA-2026

## Задане #1
[Решение](./Task1.md)

## Задание #2
[Тест-кейсы](TESTCASES.md)  
[Баг-репорт](BUGS.md)

Для запусков автотеста:
1. Создание виртуального окружения
```python -m venv ve```
2. Скачивание всех зависимостей 
```pip install -r requirements.txt```
3. Запуск автотестов (Без Allure)
```pytest .\auto_tests.py```  

**Для доп заданий:**
- E2E-тестирование находится в [коде](auto_tests.py) (API-004)

- Allure добавлен в код  
[Результат](Allure_report.png)  
Для запуска авто-тестов с использованием allure:  
    1.Для запуска автотестов с сохранением результатов в формате allure: `pytest auto_tests.py --alluredir=allure-results`
    2.Для сбора результатов в отчет: `allure generate allure-results -o allure-report --clean`
    3.Для запуска веб-приложения с отчетом: `allure open allure-report`

- Линтер кода - Flake8  
[Настройки Flake8](.flake8)  
Для запуска: `black <Название файла с кодом>` или `black <Путь до директории>`  
Пример (можно запустить в проекте после п.2): `black .\auto_tests.py`

- Форматтер кода - black  
[Настройки black](pyproject.toml)  
Для запуска: `flake8 <Название файла с кодом>` или `flake8 <Путь до директории>`  
Пример(можно запустить в проекте после п.2): `flake8 .\auto_tests.py`
