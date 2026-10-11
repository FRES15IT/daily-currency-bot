import os
import sys
import traceback
import requests

LOG_FILE = "crash_log.txt"

def write_log(text):
    print(text)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")

# Проверяем секреты (для GitHub) или берем жестко прописанные данные (для ПК)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_crypto_rates():
    write_log("[1/3] Подключаюсь к Центробанку...")
    
    # Запасной стабильный URL напрямую от ЦБ РФ
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    
    try:
        # Добавляем timeout=5 (если за 5 секунд сайт не ответит, сработает защита)
        response = requests.get(url, timeout=5).json()
        
        usd = response["Valute"]["USD"]["Value"]
        eur = response["Valute"]["EUR"]["Value"]
        cny = response["Valute"]["CNY"]["Value"]
        
        write_log("[2/3] Курсы валют успешно получены!")
        return f"📊 **Официальный курс ЦБ РФ на сегодня:**\n\n💵 Доллар (USD): {usd:.2f} руб.\n💶 Евро (EUR): {eur:.2f} руб.\n🇨🇳 Юань (CNY): {cny:.2f} руб."
    
    except requests.exceptions.Timeout:
        write_log("⚠️ Ошибка: Превышено время ожидания ответа от сервера (Timeout)!")
        return "⚠️ Сервер Центробанка временно недоступен. Попробуйте позже."
    except Exception as e:
        write_log(f"❌ Ошибка при запросе к Центробанку: {e}")
        return None

def send_telegram_message(text):
    if not text:
        return

    write_log("[3/3] Отправляю сообщение в Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    try:
        # Для Telegram тоже ставим тайм-аут, чтобы не зависать
        res = requests.post(url, json=payload, timeout=5)
        res_json = res.json()
        
        if res_json.get("ok"):
            write_log("🚀 ПОБЕДА! Бот успешно отправил сообщение в Telegram!")
        else:
            write_log(f"❌ Ошибка от Telegram API: {res_json.get('description')}")
            
    except Exception as e:
        write_log(f"❌ Не удалось связаться с сервером Telegram: {e}")

if __name__ == "__main__":
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
        
    try:
        write_log("=== ЗАПУСК ОТЛАДКИ ===")
        message_text = get_crypto_rates()
        send_telegram_message(message_text)
        write_log("======================")
        
    except Exception as e:
        write_log("\n💥 КРИТИЧЕСКИЙ КРАШ СИСТЕМЫ!\n")
        write_log(traceback.format_exc())
