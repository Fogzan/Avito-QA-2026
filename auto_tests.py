import requests
import time
import pytest
import re
import allure

BASE_URL = "https://qa-internship.avito.com"

# Тестовые переменные
'''
    *так как если likes, viewCount или contacts == 0, то API возвращает ошибку, то в валидные данные они записаны как 10
    *но так как по идее, при создании объявления, логично, что likes, viewCount и contacts должны быть равны 0, то при первом тест-кейсе, создается запрос, где: 
    "statistics": {
            "likes": 0,
            "viewCount": 0,
            "contacts": 0
        }
'''
VALID_SELLER_ID = 864678
VALID_NAME = "Телефон"
VALID_PRICE = 90850
VALID_STATISTICS = {
    "likes": 10,
    "viewCount": 10,
    "contacts": 10
}

VALID_PAYLOAD = {
    "sellerID": VALID_SELLER_ID,
    "name": VALID_NAME,
    "price": VALID_PRICE,
    "statistics": VALID_STATISTICS
}


# Вспомогательные функции
'''
Функции делающие запросы к API и возвращающие ответ
Здесь же прописаны Content-Type и Accept у запросов
А так же функция извлечения id у ответа от запроса на создание объявления
'''
def create_item(payload):
    response = requests.post(
        f"{BASE_URL}/api/1/item",
        json=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"}
    )
    return response


def get_item_by_id(item_id):
    response = requests.get(
        f"{BASE_URL}/api/1/item/{item_id}",
        headers={"Accept": "application/json"}
    )
    return response


def get_items_by_seller(seller_id):
    response = requests.get(
        f"{BASE_URL}/api/1/{seller_id}/item",
        headers={"Accept": "application/json"}
    )
    return response


def get_statistics(item_id):
    response = requests.get(
        f"{BASE_URL}/api/2/statistic/{item_id}",
        headers={"Accept": "application/json"}
    )
    return response


def delete_item(item_id):
    response = requests.delete(
        f"{BASE_URL}/api/2/item/{item_id}",
        headers={"Accept": "application/json"}
    )
    return response


def extract_item_id_from_response(response):
    response_json = response.json()
    status_message = response_json.get("status", "")
    status_message_elements = status_message.split(" ")
    if len(status_message_elements) != 4:
        return None
    return status_message_elements[-1]


# API-001 Создание объявления с валидными значениями
@allure.title("API-001: Создание объявления с валидными значениями")
@allure.description("Проверяет успешное создание объявления с валидными данными (статистика = 0)")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_item_success():
    payload = {
        "sellerID": VALID_SELLER_ID,
        "name": VALID_NAME,
        "price": VALID_PRICE,
        "statistics": {
            "likes": 0,
            "viewCount": 0,
            "contacts": 0
        }
    }
    with allure.step("Отправка POST запроса на создание объявления"):
        response = create_item(payload)
    
    with allure.step("Проверка статус-кода 200"):
        assert response.status_code == 200, f"Ожидался 200, получили {response.status_code}"
    
    response_json = response.json()
    with allure.step("Проверка наличия поля status в ответе"):
        assert "status" in response_json, f"Ответ не содержит поле status: {response_json}"
    
    with allure.step("Извлечение и проверка ID объявления"):
        item_id = extract_item_id_from_response(response)
        assert item_id is not None, f"Не найден item_id"
        assert "Сохранили объявление - " in response_json["status"], f"В ответе не найдено сообщение о сохраненном объявлении: {response_json["status"]}"


# API-002 Создание объявления без обязательного поля sellerID
@allure.title("API-002: Создание объявления без обязательного поля sellerID")
@allure.description("Проверяет, что API возвращает ошибку 400 при отсутствии поля sellerID")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_item_missing_seller_id():
    payload = {
        "name": VALID_NAME,
        "price": VALID_PRICE,
        "statistics": VALID_STATISTICS
    }
    
    with allure.step("Отправка POST запроса без поля sellerID"):
        response = create_item(payload)
    
    with allure.step("Проверка статус-кода 400"):
        assert response.status_code == 400, f"Ожидался 400, получили {response.status_code}"
    
    response_json = response.json()
    
    with allure.step("Проверка сообщения об ошибке"):
        assert response_json["result"]["message"] == "поле sellerID обязательно", f"В ответе находится некорректное сообщение об отсутствии поля sellerID: {response_json["result"]["message"]}"


# API-003 Многократное получение одного и того же объявления
@allure.title("API-003: Многократное получение одного и того же объявления")
@allure.description("Проверяет идемпотентность GET запросов")
@allure.severity(allure.severity_level.NORMAL)
def test_get_item_multiple_times():
    # Создаём объявление
    with allure.step("Создание тестового объявления"):
        create_response = create_item(VALID_PAYLOAD)
        assert create_response.status_code == 200, f"Ожидался 200, получили {create_response.status_code}"
        item_id = extract_item_id_from_response(create_response)
    
    # Три GET запроса
    with allure.step("Выполнение трёх GET запросов"):
        response1 = get_item_by_id(item_id)
        response2 = get_item_by_id(item_id)
        response3 = get_item_by_id(item_id)
    
    with allure.step("Проверка статус-кодов 200"):
        assert response1.status_code == 200, f"Ожидался 200, получили {response1.status_code}"
        assert response2.status_code == 200, f"Ожидался 200, получили {response2.status_code}"
        assert response3.status_code == 200, f"Ожидался 200, получили {response3.status_code}"
    with allure.step("Проверка идентичности ответов"):
        assert response1.json() == response2.json() == response3.json(), f"Ответы запросов не идентичны: {response1.json()} {response2.json()} {response3.json()}"


# API-004 Полный жизненный цикл объявления (CRUD операция)
@allure.title("API-004: Полный жизненный цикл объявления (CRUD)")
@allure.description("Проверяет полный цикл: создание, чтение, чтение по продавцу, чтение статистики и удаление")
@allure.severity(allure.severity_level.CRITICAL)
def test_full_lifecycle():
    seller_id = VALID_SELLER_ID
    payload = VALID_PAYLOAD
    
    # Создание
    with allure.step("Создание объявления"):
        create_response = create_item(payload)
        assert create_response.status_code == 200, f"Ожидался 200, получили {create_response.status_code}"
        item_id = extract_item_id_from_response(create_response)
    
    # Чтение по ID
    with allure.step("Получение объявления по ID"):
        get_response = get_item_by_id(item_id)
        assert get_response.status_code == 200, f"Ожидался 200, получили {get_response.status_code}"
        get_data = get_response.json()[0]
        assert get_data["name"] == VALID_NAME, f"Поле name не совпадает с полем name, которое использовалось при создании: {get_data["name"]}"
        assert get_data["price"] == VALID_PRICE, f"Поле price не совпадает с полем price, которое использовалось при создании: {get_data["price"]}"
        assert get_data["sellerId"] == seller_id, f"Поле sellerId не совпадает с полем sellerId, которое использовалось при создании: {get_data["sellerId"]}"
    
    # Чтение по ID продавца
    with allure.step("Получение объявлений продавца"):
        seller_items_response = get_items_by_seller(seller_id)
        assert seller_items_response.status_code == 200, f"Ожидался 200, получили {seller_items_response.status_code}"
        item_ids = []
        for item in seller_items_response.json():
            item_ids.append(item["id"])
        assert item_id in item_ids, f"Среди объявлений продавца не найдено созданного ранее объявления: {item_ids}"
    
    # Чтение статистики
    with allure.step("Получение статистики"):
        stats_response = get_statistics(item_id)
        assert stats_response.status_code == 200, f"Ожидался 200, получили {stats_response.status_code}"
        stats = stats_response.json()[0]
        assert stats["likes"] == VALID_STATISTICS["likes"], f"В полученной статистике не найдено поле likes: {stats}"
        assert stats["viewCount"] == VALID_STATISTICS["viewCount"], f"В полученной статистике не найдено поле viewCount: {stats}"
        assert stats["contacts"] == VALID_STATISTICS["contacts"], f"В полученной статистике не найдено поле contacts: {stats}"

    # Удаление
    with allure.step("Удаление объявления"):
        delete_response = delete_item(item_id)
        assert delete_response.status_code == 200, f"Ожидался 200, получили {stats_response.status_code}"


# API-005 Время ответа API при создании объявления
@allure.title("API-005: Время ответа API при создании объявления")
@allure.description("Проверяет, что среднее время ответа не превышает 500мс")
@allure.severity(allure.severity_level.NORMAL)
def test_response_time():
    response_times = []
    
    with allure.step("Выполнение 10 запросов на создание объявления"):
        for i in range(10):
            start_time = time.time()
            response = create_item(VALID_PAYLOAD)
            end_time = time.time()

            assert response.status_code == 200, f"Ожидался 200, получили {response.status_code}"
            response_times.append((end_time - start_time) * 1000)
    
    with allure.step("Расчёт и проверка среднего времени"):
        average_time = sum(response_times) / len(response_times)
        assert average_time <= 500, f"Среднее время {average_time} мс превышает 500мс"


# API-006 Защита от XSS-инъекции в поле name
@allure.title("API-006: Защита от XSS-инъекции в поле name")
@allure.description("Проверяет, что API экранирует опасные символы в поле name")
@allure.severity(allure.severity_level.CRITICAL)
def test_xss_protection():
    xss_payload = {
        "sellerID": VALID_SELLER_ID,
        "name": "<script>alert('XSS')</script>",
        "price": VALID_PRICE,
        "statistics": VALID_STATISTICS
    }
    
    with allure.step("Создание объявления с XSS-инъекцией"):
        create_response = create_item(xss_payload)
        assert create_response.status_code == 200, f"Ожидался 200, получили {create_response.status_code}"
        item_id = extract_item_id_from_response(create_response)

    with allure.step("Получение созданного объявления"):
        get_response = get_item_by_id(item_id)
        assert get_response.status_code == 200, f"Ожидался 200, получили {create_response.status_code}"
    
    with allure.step("Проверка экранирования опасных символов"):
        # Получаем текст ответа (до парсинга JSON, так как если парсить, то экранирование визуально пропадет)
        raw_text = get_response.text
        # Проверяем текст (там должны быть \u003C == "<")
        assert "\\u003cscript\\u003e" in raw_text, f"В тексте ответе нет экранирования: {raw_text}"
    
        # Или проверяем, что нет незаэкранированных символов
        assert "<script>" not in raw_text, f"В тексте ответа есть незаэкранированный тег: {raw_text}"
        