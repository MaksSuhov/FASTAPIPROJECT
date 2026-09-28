import os
import logging
from typing import Any
from unittest import result

import httpx
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

mcp = FastMCP('Weather')

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENWEATHER_BASE_URL = "https://openweathermap.org/data/2.5"


async def make_weather_request(endpoint: str, params: dict[str, Any]) -> dict[str, Any] | None:
    """
    Вспомогательная функция для выполнения запросов к OpenWeatherMap API

    Args:
        endpoint: конечная точка API (например, 'weather' или 'forecast')
        params: параметры запроса
    returns:
        JSON ответ от API или None в случае ошибки
    """

    if not OPENWEATHER_API_KEY:
        logger.error("OPENWEATHER_API_KEY не найден в переменной окружения")
        return None

    params['appid'] = OPENWEATHER_API_KEY
    params['lang'] = 'ru'

    url = f"{OPENWEATHER_BASE_URL}/{endpoint}"

    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"запрос к API:{url}")
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"http ошибка: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        logger.error(f"ошибка при запросе к API: {str(e)}")
        return None


@mcp.tool()
async def get_current_user(city:str, units:str = 'metric') -> str:
    """
    получить текущую погоду для указанного города

    args:
        city: название города на русском или на английском(например "Москва" или "Moscow")
        units: система измерения - 'metric'(цельсий) или "imperial"(фаренгейт)

    returns:
        строка с описанием текущей погоды
    """
    logger.info(f"запрос погоды для города: {city}")
    params = {
        'q': city,
        'units': units
    }

    data = await make_weather_request('weather', params)

    if not data:
        return f"не удалось получить погоду для города '{city}'.проверьте название города."

    if 'cod' in data and data['cod'] != 200:
        return "ошибка API"

    try:
        main = data['main']
        weather = data['weather'][0]
        wind = data['wind']

        temp_unit = "°C" if units == 'metric' else '°F'
        wind_unit = 'м/с' if units == 'metric' else "миль/ч"

        result = f"""
        Погода в городе {data['name']}, {data['sys']['country']}

        🌡 Температура: {main['temp']:.1f}{temp_unit}
        🌡 Ощущается как: {main['feels_like']:.1f}{temp_unit}
        📊 Мин/Макс: {main['temp_min']:.1f}{temp_unit} / {main['temp_max']:.1f}{temp_unit}

        ☁ Условия: {weather['description'].capitalize()}
        💧 Влажность: {main['humidity']}%
        🧭 Давление: {main['pressure']} гПа
        💨 Ветер: {wind['speed']} {wind_unit}, направление {wind.get('deg', 'н/д')}°
        """.strip()

        logger.info(f"успешно получена погода для {city}")
        return result

    except KeyError as e:
        logger.error("ошибка при обработке данных")
        return f"ошибка при обработке данных о погоде: {str(e)}"


@mcp.tool()
async def get_forecast(city: str, days: int = 3, units: str = "metric") -> str:
    """
    Получить прогноз погоды на несколько дней

    Args:
        city: Название города на русском или английском
        days: Количество дней для прогноза (1-5)
        units: Система измерения - "metric" (Цельсий) или "imperial" (Фаренгейт)

    Returns:
        Строка с прогнозом погоды
    """
    logger.info(f"Запрос прогноза для города: {city} на {days} дней")

    # Ограничиваем количество дней
    days = min(max(days, 1), 5)

    # Формируем параметры запроса
    params = {
        "q": city,
        "units": units,
        "cnt": days * 8  # API возвращает данные каждые 3 часа, 8 записей = 1 день
    }

    # Выполняем запрос к API
    data = await make_weather_request("forecast", params)

    # Обработка ошибок
    if not data:
        return f"❌ Не удалось получить прогноз для города '{city}'."

    if "cod" not in data or data["cod"] != "200":
        return f"❌ Ошибка API: {data.get('message', 'Неизвестная ошибка')}"

    try:
        # Символы температуры
        temp_unit = "°C" if units == "metric" else "°F"

        # Группируем данные по дням
        forecasts = []
        current_date = None
        day_data = []

        for item in data["list"]:
            # Извлекаем дату
            date = item["dt_txt"].split()[0]

            if current_date != date:
                # Если накопили данные за день, обрабатываем их
                if day_data:
                    forecasts.append(format_day_forecast(day_data, temp_unit))
                    if len(forecasts) >= days:
                        break

                # Начинаем новый день
                current_date = date
                day_data = [item]
            else:
                day_data.append(item)

        # Обрабатываем последний день
        if day_data and len(forecasts) < days:
            forecasts.append(format_day_forecast(day_data, temp_unit))

        # Формируем итоговый ответ
        result = f"📅 Прогноз погоды для {data['city']['name']}, {data['city']['country']}\n\n"
        result += "\n\n".join(forecasts)

        logger.info(f"Успешно получен прогноз для {city}")
        return result

    except Exception as e:
        logger.error(f"Ошибка при обработке прогноза: {e}")
        return f"❌ Ошибка при обработке данных прогноза: {str(e)}"


def format_day_forecast(day_data: list, temp_unit: str) -> str:
    """
    Форматирует прогноз на один день

    Args:
        day_data: Список данных о погоде за день (каждые 3 часа)
        temp_unit: Символ единицы температуры

    Returns:
        Отформатированная строка с прогнозом
    """
    # Берем первую запись для даты
    date = day_data[0]["dt_txt"].split()[0]

    # Вычисляем средние значения
    temps = [item["main"]["temp"] for item in day_data]
    avg_temp = sum(temps) / len(temps)
    min_temp = min(temps)
    max_temp = max(temps)

    # Самое частое описание погоды
    descriptions = [item["weather"][0]["description"] for item in day_data]
    most_common_desc = max(set(descriptions), key=descriptions.count)

    # Средняя влажность и ветер
    avg_humidity = sum(item["main"]["humidity"] for item in day_data) / len(day_data)
    avg_wind = sum(item["wind"]["speed"] for item in day_data) / len(day_data)

    return f"""
📆 {date}
🌡️ Средняя температура: {avg_temp:.1f}{temp_unit}
📊 Мин/Макс: {min_temp:.1f}{temp_unit} / {max_temp:.1f}{temp_unit}
☁️ Условия: {most_common_desc.capitalize()}
💧 Влажность: {avg_humidity:.0f}%
💨 Ветер: {avg_wind:.1f} м/с
    """.strip()



































































