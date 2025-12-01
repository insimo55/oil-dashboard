# backend/wells/notifications.py

import requests
import logging
from django.conf import settings
from html import escape
from .models import Well

logger = logging.getLogger(__name__)

def send_telegram_alert(well: Well, message: str):
    """
    Отправляет сообщение-тревогу в Telegram.
    Безопасно экранирует текст, сохраняя теги <b> и <i>.
    """
    bot_token = getattr(settings, 'TELEGRAM_ALERTS_BOT_TOKEN', None)
    chat_id = well.telegram_chat_id
    topic_id = well.telegram_topic_id

    if not bot_token:
        logger.error("TELEGRAM_ALERTS_BOT_TOKEN не настроен. Уведомление не отправлено.")
        return
    if not chat_id:
        logger.warning(f"Для скважины '{well.name}' не указан Telegram Chat ID. Уведомление не отправлено.")
        return

    # 1️⃣ Экранируем весь текст, чтобы Telegram не сломал HTML
    safe = escape(message, quote=True)

    # 2️⃣ Разрешаем только теги <b> и <i>
    safe = (safe
            .replace('&lt;b&gt;', '<b>')
            .replace('&lt;/b&gt;', '</b>')
            .replace('&lt;i&gt;', '<i>')
            .replace('&lt;/i&gt;', '</i>')
            )

    # Все остальные теги останутся экранированными → Telegram не упадёт

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': safe,
        'parse_mode': 'HTML',
    }

    if topic_id:
        payload['message_thread_id'] = topic_id

    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        logger.info(
            f"Уведомление для скважины '{well.name}' успешно отправлено в чат {chat_id}."
        )
    except requests.exceptions.RequestException as e:
        logger.error(
            f"Ошибка при отправке уведомления в Telegram для скважины '{well.name}': {e}\n"
            f"Текст ошибки Telegram: {getattr(e.response, 'text', None)}"
        )
