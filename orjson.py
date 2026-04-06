import orjson
import datetime
import uuid
import decimal
from dataclasses import dataclass

@dataclass
class Sensor:
    id: uuid.UUID
    temperature: float
    is_active: bool

class FinancialMetric:
    """Пользовательский класс, не поддерживаемый orjson по умолчанию."""
    def __init__(self, value: str):
        self.value = decimal.Decimal(value)

def custom_encoder(obj):
    """
    Обработчик для типов, которые orjson не умеет сериализовать нативно.
    В данном случае обрабатываем FinancialMetric и Decimal.
    """
    if isinstance(obj, FinancialMetric):
        return f"{obj.value:.4f} USD"
    if isinstance(obj, decimal.Decimal):
        return str(obj)
    raise TypeError(f"Type {type(obj)} is not serializable")

def generate_complex_payload():
    """Создание структуры данных со сложными типами."""
    
    # Имитация заранее подготовленного или закешированного JSON-ответа
    # orjson.Fragment позволяет вставить эти байты как валидный JSON без повторного парсинга
    cached_metadata = b'{"version": "1.4.2", "hash": "a1b2c3d4e5f6"}'
    
    data = {
        "transaction_id": uuid.uuid4(),
        "timestamp": datetime.datetime.now(datetime.timezone.utc),
        "sensors": [
            Sensor(uuid.uuid4(), 22.4, True),
            Sensor(uuid.uuid4(), -1.2, False)
        ],
        "metrics": FinancialMetric("14500.5025"),
        "raw_meta": orjson.Fragment(cached_metadata),
        # Словарь с нестроковыми ключами (int)
        100: "code_ok",
        404: "code_not_found"
    }
    return data

def process_telemetry():
    """Основной цикл сериализации и десериализации."""
    payload = generate_complex_payload()
    
    # Конфигурация поведения orjson.dumps через побитовое ИЛИ (OR):
    # OPT_INDENT_2: Pretty-print с отступом в 2 пробела.
    # OPT_SORT_KEYS: Алфавитная сортировка ключей словарей.
    # OPT_NON_STR_KEYS: Разрешает использование чисел в качестве ключей (приведет к строкам).
    # OPT_OMIT_MICROSECONDS: Отсекает микросекунды у объектов datetime.
    # OPT_APPEND_NEWLINE: Добавляет символ перевода строки \n в конец байтовой строки.
    serialization_flags = (
        orjson.OPT_INDENT_2 |
        orjson.OPT_SORT_KEYS |
        orjson.OPT_NON_STR_KEYS |
        orjson.OPT_OMIT_MICROSECONDS |
        orjson.OPT_APPEND_NEWLINE
    )
    
    # Сериализация в байты. Используем default для пользовательских типов
    print("Выполняется сериализация данных...")
    json_bytes = orjson.dumps(
        payload, 
        default=custom_encoder, 
        option=serialization_flags
    )
    
    # Запись в файл
    with open("telemetry_dump.json", "wb") as f:
        f.write(json_bytes)
        
    # Десериализация обратно в Python-объекты
    print("Выполняется чтение и десериализация...")
    parsed_data = orjson.loads(json_bytes)
    
    print(f"ID восстановленной транзакции: {parsed_data['transaction_id']}")
    print(f"Статус завершения: Успешно. Данные сохранены в telemetry_dump.json")

if __name__ == "__main__":
    process_telemetry()
