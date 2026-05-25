import interface
import weather_api

app, result_label, update_btn, city_entry, map_widget = interface.create_window()

def click_action():
    target_city = city_entry.get().strip()
    if not target_city:
        result_label.configure(text="❌ Ошибка: Введи город!")
        return

    result_label.configure(text="⏳ Сканирование локации...")
    app.update()
    
    data = weather_api.get_weather(target_city)
    
    if "error" in data:
        result_label.configure(text=f"❌ {data['error']}")
    else:
        # Управляем картой: летим в город и ставим маркер
        map_widget.set_position(data['lat'], data['lon'])
        map_widget.set_zoom(10)
        map_widget.delete_all_marker()
        map_widget.set_marker(data['lat'], data['lon'], text=data['city'])

        # Красиво форматированный текст
        text = (
            f"📍 {data['city']}\n"
            f"🕒 Обновлено: {data['time']}\n"
            f"───────────────\n"
            f"🌡 Температура: {data['temp']}°C\n"
            f"🏃 Ощущается: {data['feels_like']}°C\n"
            f"💧 Влажность: {data['humidity']}%\n"
            f"💨 Ветер: {data['wind']} м/с\n"
            f"───────────────\n"
            f"📅 Завтра:\nот {data['tomorrow_min']}°C до {data['tomorrow_max']}°C\n"
            f"───────────────\n"
            f"💡 Рекомендация:\n{data['advice']}"
        )
        result_label.configure(text=text)

update_btn.configure(command=click_action)
app.mainloop()
