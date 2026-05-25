import flet as ft
import requests
from datetime import datetime

# --- ОФИЦИАЛЬНАЯ ЛОГИКА API ---
def get_weather_desc(code):
    if code == 0: return "☀️ Ясно"
    elif code in [1, 2, 3]: return "☁️ Облачно"
    elif code in [45, 48]: return "🌫 Туман"
    elif code in [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82]: return "🌧 Дождь"
    elif code in [71, 73, 75, 77, 85, 86]: return "❄️ Снег"
    elif code in [95, 96, 99]: return "⛈ Гроза"
    return "🌪 Неизвестно"

def get_weather(city):
    try:
        # 1. Поиск координат
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru&format=json"
        geo_response = requests.get(geo_url).json()
        
        if "results" not in geo_response:
            return {"error": f"Ошибка: Локация '{city}' не найдена в базе данных."}
        
        lat = geo_response["results"][0]["latitude"]
        lon = geo_response["results"][0]["longitude"]
        real_name = geo_response["results"][0].get("name", city)

        # 2. Поиск погоды (С ПРОГНОЗОМ И СОЛНЦЕМ)
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,weather_code&daily=temperature_2m_max,temperature_2m_min,sunrise,sunset&timezone=Europe/Moscow"
        data = requests.get(weather_url).json()
        
        current = data["current"]
        daily = data["daily"]
        
        feels_like = round(current["apparent_temperature"])
        
        # 3. Умный совет ИИ
        if feels_like < 0: advice = "Надевай зимнюю куртку и шапку!"
        elif feels_like < 12: advice = "Прохладно, нужна плотная куртка."
        elif feels_like < 20: advice = "Комфортно, хватит легкой ветровки."
        else: advice = "Жара! Можно идти в футболке."
        
        if current["weather_code"] >= 51: advice += " ☔ Обязательно захвати зонт!"

        # 4. Запрос интересного факта из Википедии
        fact = "Информация о городе загружается..."
        try:
            wiki_url = f"https://ru.wikipedia.org/api/rest_v1/page/summary/{real_name}"
            wiki_res = requests.get(wiki_url).json()
            if "extract" in wiki_res:
                fact = wiki_res["extract"].split(". ")[0] + "."
        except:
            fact = "Данные энциклопедии временно недоступны."
        
        return {
            "city": real_name,
            "desc": get_weather_desc(current["weather_code"]),
            "temp": round(current["temperature_2m"]),
            "feels_like": feels_like,
            "humidity": current["relative_humidity_2m"],
            "wind": round(current["wind_speed_10m"]),
            "tomorrow_min": round(daily["temperature_2m_min"][1]),
            "tomorrow_max": round(daily["temperature_2m_max"][1]),
            "sunrise": daily["sunrise"][0][-5:],
            "sunset": daily["sunset"][0][-5:],
            "advice": advice,
            "fact": fact,
            "time": datetime.now().strftime("%H:%M")
        }
    except Exception as e:
        return {"error": "Системная ошибка: Сбой подключения к серверу."}

# --- ИНТЕРФЕЙС WEATHER RADAR ---
def main(page: ft.Page):
    page.title = "Weather Radar"
    page.window_width = 380
    page.window_height = 750
    page.theme_mode = ft.ThemeMode.DARK 
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO # Включили плавный скролл экрана!

    title = ft.Text("WEATHER RADAR", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_400)
    subtitle = ft.Text("Мобильный терминал", size=12, color=ft.colors.GREY_400)
    
    city_input = ft.TextField(label="Введите населенный пункт", width=320, border_radius=8, text_align=ft.TextAlign.CENTER)
    city_input.value = "Путилково"
    
    result_text = ft.Text("Ожидание запроса...", size=15, text_align=ft.TextAlign.LEFT)
    fact_text = ft.Text("", size=14, color=ft.colors.BLUE_200, italic=True, text_align=ft.TextAlign.CENTER)
    
    result_container = ft.Container(
        content=ft.Column([result_text, ft.Divider(color=ft.colors.GREY_700), fact_text]),
        padding=20,
        bgcolor=ft.colors.SURFACE_VARIANT,
        border_radius=12,
        width=320
    )

    signature = ft.Text("© 2026 Сделано Yardo и WinCore", size=12, color=ft.colors.GREY_500)

    def fetch_data(e):
        if not city_input.value:
            result_text.value = "Внимание: Укажите локацию для поиска."
            result_text.color = ft.colors.RED_400
            fact_text.value = ""
            page.update()
            return
            
        result_text.value = "Синхронизация с метеоспутниками..."
        result_text.color = ft.colors.WHITE
        fact_text.value = ""
        page.update()
        
        data = get_weather(city_input.value)
        
        if "error" in data:
            result_text.value = data["error"]
            result_text.color = ft.colors.RED_400
            fact_text.value = ""
        else:
            result_text.color = ft.colors.WHITE
            result_text.value = (
                f"📍 {data['city']} | 🕒 {data['time']}\n"
                f"──────────────────────\n"
                f"Текущая сводка:\n"
                f"{data['desc']}\n"
                f"🌡 Температура: {data['temp']} °C\n"
                f"🏃 Ощущается: {data['feels_like']} °C\n"
                f"💧 Влажность: {data['humidity']} %\n"
                f"💨 Скорость ветра: {data['wind']} м/с\n"
                f"──────────────────────\n"
                f"📅 Прогноз на завтра:\n"
                f"от {data['tomorrow_min']} °C до {data['tomorrow_max']} °C\n"
                f"──────────────────────\n"
                f"☀️ Рассвет: {data['sunrise']} | 🌙 Закат: {data['sunset']}\n"
                f"──────────────────────\n"
                f"🤖 Совет системы:\n{data['advice']}"
            )
            fact_text.value = f"💡 {data['fact']}"
            
        page.update()

    search_btn = ft.ElevatedButton("ЗАПРОСИТЬ ДАННЫЕ", on_click=fetch_data, width=320, height=50, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))

    page.add(
        title,
        subtitle,
        ft.Divider(height=10, color=ft.colors.TRANSPARENT),
        city_input,
        ft.Divider(height=5, color=ft.colors.TRANSPARENT),
        search_btn,
        ft.Divider(height=10, color=ft.colors.TRANSPARENT),
        result_container,
        ft.Divider(height=10, color=ft.colors.TRANSPARENT),
        signature
    )

if __name__ == "__main__":
    ft.app(target=main)
