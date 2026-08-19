from flask import Flask
import threading
import time
import feedparser
import random
import re
import requests
import asyncio
from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest, InviteToChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import InputPeerUser, InputPeerChannel
import csv
import os

app = Flask(__name__)

# ---- КОНФИГ ----
BOT_TOKEN = '8836968982:AAH_Hoa6mAA3ZVbNwzMjKtvFwBKBKNTxSRY'
TELEGRAM_API = f'https://api.telegram.org/bot{BOT_TOKEN}'
API_ID = 6
API_HASH = 'eb06d4abfb49dc3eeb1aeb98ae0f581e'

# ---- КАНАЛЫ (все 17) ----
channel_config = {
    '@Honest_1VPN': {
        'feeds': ['https://xakep.ru/feed/'],
        'emojis': ['🔐', '🛡️', '🌐', '⚡', '💻'],
        'tags': ['#VPN', '#безопасность', '#технологии'],
        'poll_frequency': 0.1,
        'poll_question': 'Какой VPN вы используете?',
        'poll_options': ['ExpressVPN', 'NordVPN', 'ProtonVPN', 'Другой']
    },
    '@stydensvv': {
        'feeds': ['https://mel.fm/rss'],
        'emojis': ['📚', '🎓', '📝', '🧠', '💡'],
        'tags': ['#студент', '#учеба', '#лайфхаки'],
        'poll_frequency': 0.15,
        'poll_question': 'Что помогает лучше учиться?',
        'poll_options': ['Кофе', 'Четкий план', 'Музыка', 'Хороший сон']
    },
    '@bobszsz': {
        'feeds': ['https://www.starhit.ru/export/rss/'],
        'emojis': ['⭐', '🌟', '💫', '🎬', '🎭'],
        'tags': ['#звезды', '#блогеры', '#новости'],
        'poll_frequency': 0.12,
        'poll_question': 'Кто ваш любимый блогер?',
        'poll_options': ['Моргенштерн', 'Ксения Собчак', 'Лена Миро', 'Другой']
    },
    '@radostlio': {
        'feeds': ['https://www.adme.ru/rss.xml'],
        'emojis': ['👀', '🤔', '😅', '🔥', '💬'],
        'tags': ['#истории', '#жизнь', '#наблюдения'],
        'poll_frequency': 0.08,
        'poll_question': 'Случалась ли с вами похожая история?',
        'poll_options': ['Да', 'Нет', 'Почти', 'Сейчас расскажу']
    },
    '@sochialso': {
        'feeds': ['https://www.psychologies.ru/feed/'],
        'emojis': ['🧠', '💭', '🌱', '🫂', '🕊️'],
        'tags': ['#психология', '#отношения', '#созависимость'],
        'poll_frequency': 0.18,
        'poll_question': 'Сталкивались ли вы с созависимостью?',
        'poll_options': ['Да', 'Нет', 'Сейчас прохожу терапию', 'Хочу узнать больше']
    },
    '@malliebali': {
        'feeds': ['https://www.psychologies.ru/feed/'],
        'emojis': ['🌿', '🧘', '🫂', '🕊️', '💙'],
        'tags': ['#тревога', '#паника', '#поддержка'],
        'poll_frequency': 0.2,
        'poll_question': 'Как вы справляетесь с тревогой?',
        'poll_options': ['Дыхание', 'Спорт', 'Терапия', 'Никак']
    },
    '@tvoilaxak': {
        'feeds': ['https://lifehacker.ru/feed/'],
        'emojis': ['🛠️', '💡', '⚡', '🧩', '🔧'],
        'tags': ['#лайфхак', '#советы', '#полезно'],
        'poll_frequency': 0.1,
        'poll_question': 'Какой лайфхак помог вам больше всего?',
        'poll_options': ['Организация времени', 'Уборка', 'Кулинария', 'Другой']
    },
    '@krippaaif': {
        'feeds': ['https://cryptonews.ru/feed'],
        'emojis': ['💰', '📈', '🚀', '💎', '📊'],
        'tags': ['#крипта', '#заработок', '#инвестиции'],
        'poll_frequency': 0.14,
        'poll_question': 'Что вы купите в крипте?',
        'poll_options': ['Bitcoin', 'Ethereum', 'Solana', 'Только мем-койны']
    },
    '@geyilig': {
        'feeds': ['https://cyber.sports.ru/rss/'],
        'emojis': ['🎮', '🕹️', '🔥', '💥', '👾'],
        'tags': ['#стримеры', '#игры', '#киберспорт'],
        'poll_frequency': 0.09,
        'poll_question': 'Кого смотрите чаще всех?',
        'poll_options': ['Бустер', 'Crystallis', 'Shadow', 'Другой']
    },
    '@ttemnaya_komnata': {
        'feeds': ['https://www.psychologies.ru/feed/'],
        'emojis': ['🌙', '🖤', '🕯️', '💫', '🌌'],
        'tags': ['#депрессия', '#поддержка', '#честность'],
        'poll_frequency': 0.16,
        'poll_question': 'Как вы себя чувствуете сегодня?',
        'poll_options': ['Нормально', 'Средне', 'Плохо', 'Не знаю']
    },
    '@otnashena': {
        'feeds': ['https://www.psychologies.ru/feed/'],
        'emojis': ['❤️', '💔', '🫂', '💬', '🌹'],
        'tags': ['#отношения', '#любовь', '#дружба'],
        'poll_frequency': 0.17,
        'poll_question': 'Что важнее в отношениях?',
        'poll_options': ['Доверие', 'Понимание', 'Страсть', 'Дружба']
    },
    '@patryry': {
        'feeds': [],
        'emojis': ['😂', '🤣', '😅', '🔥', '💀'],
        'tags': ['#мемы', '#кринж', '#юмор'],
        'poll_frequency': 0.05,
        'poll_question': 'Какой мем сегодня лучший?',
        'poll_options': ['Белый медведь', 'Грустный кот', 'Плачущий Джей', 'Лягушка']
    },
    '@depozit20': {
        'feeds': ['https://www.rbc.ru/rss/'],
        'emojis': ['📊', '💹', '💰', '📈', '🏦'],
        'tags': ['#финансы', '#инвестиции', '#деньги'],
        'poll_frequency': 0.11,
        'poll_question': 'Куда вложили бы 100 000 ₽?',
        'poll_options': ['Акции', 'Облигации', 'Крипта', 'Недвижимость']
    },
    '@expert_na_minimalkah': {
        'feeds': ['https://bash.im/rss/'],
        'emojis': ['😂', '🤪', '😎', '🔥', '💀'],
        'tags': ['#юмор', '#москва', '#советы'],
        'poll_frequency': 0.06,
        'poll_question': 'Как выжить в Москве?',
        'poll_options': ['Кофе', 'Метро', 'Друзья', 'Терпение']
    },
    '@mozg_vkluchi': {
        'feeds': ['https://www.psychologies.ru/feed/'],
        'emojis': ['🧠', '💅', '💕', '👑', '💪'],
        'tags': ['#психология', '#девушки', '#самооценка'],
        'poll_frequency': 0.19,
        'poll_question': 'Поднимаешь самооценку?',
        'poll_options': ['Да', 'Нет', 'Пытаюсь', 'А что это?']
    },
    '@kotdyrova': {
        'feeds': ['https://habr.com/ru/rss/all/all/?fl=ru'],
        'emojis': ['💻', '🖥️', '🤖', '⚡', '🔧'],
        'tags': ['#технологии', '#IT', '#безопасность'],
        'poll_frequency': 0.09,
        'poll_question': 'Чего ждать от IT в 2026?',
        'poll_options': ['ИИ', 'Квантовые компьютеры', 'Метавселенные', 'Другое']
    },
    '@internetdemo': {
        'feeds': ['https://lenta.ru/rss/top7'],
        'emojis': ['📰', '🌐', '📱', '💬', '🔥'],
        'tags': ['#новости', '#интернет', '#тренды'],
        'poll_frequency': 0.07,
        'poll_question': 'Что важнее в новостях?',
        'poll_options': ['Политика', 'Технологии', 'Спорт', 'Культура']
    }
}

# ---- 1. РЕГУЛЯРНЫЙ ПОСТИНГ (БЫЛО) ----
def clean_summary(summary):
    return re.sub(r'<[^>]+>', '', summary)[:200]

def get_emoji(channel):
    return random.choice(channel_config.get(channel, {}).get('emojis', ['⭐']))

def get_image(entry):
    if 'media_content' in entry:
        return entry.media_content[0].get('url')
    if 'enclosure' in entry:
        return entry.enclosure.get('url')
    return None

def send_message(channel, text):
    url = f'{TELEGRAM_API}/sendMessage'
    payload = {'chat_id': channel, 'text': text}
    try:
        requests.post(url, json=payload, timeout=10)
        print(f'✅ Пост в {channel}')
    except Exception as e:
        print(f'❌ Ошибка в {channel}: {e}')

def send_photo(channel, image_url, caption):
    url = f'{TELEGRAM_API}/sendPhoto'
    payload = {'chat_id': channel, 'photo': image_url, 'caption': caption}
    try:
        requests.post(url, json=payload, timeout=10)
        print(f'✅ Фото в {channel}')
    except Exception as e:
        print(f'❌ Ошибка фото в {channel}: {e}')

def send_poll(channel, question, options):
    url = f'{TELEGRAM_API}/sendPoll'
    payload = {'chat_id': channel, 'question': question, 'options': options}
    try:
        requests.post(url, json=payload, timeout=10)
        print(f'📊 Опрос в {channel}')
    except Exception as e:
        print(f'❌ Ошибка опроса в {channel}: {e}')

# ---- 2. НАКРУТКА ПОДПИСЧИКОВ (НОВОЕ) ----
class SubscriptionBooster:
    def __init__(self, api_id, api_hash):
        self.client = TelegramClient('booster_session', api_id, api_hash)
        self.target_channels = list(channel_config.keys())

    async def add_members_from_channel(self, source_channel, target_channel, limit=10):
        """Копирует подписчиков из одного канала в другой."""
        await self.client.start()
        source_entity = await self.client.get_entity(source_channel)
        target_entity = await self.client.get_entity(target_channel)
        
        participants = await self.client.get_participants(source_entity, limit=limit)
        added = 0
        for user in participants:
            try:
                await self.client(InviteToChannelRequest(target_entity, [user.id]))
                added += 1
                print(f'➕ Добавлен {user.first_name} в {target_channel}')
                time.sleep(random.randint(3, 7))
                if added >= limit:
                    break
            except Exception as e:
                print(f'❌ Ошибка добавления: {e}')
        return added

    async def add_from_public_groups(self, target_channel, limit=5):
        """Ищет публичные группы по теме и добавляет их участников."""
        await self.client.start()
        target_entity = await self.client.get_entity(target_channel)
        groups = ['@durov', '@tginfo', '@telegram']  # можно расширить
        added = 0
        for group in groups:
            try:
                group_entity = await self.client.get_entity(group)
                participants = await self.client.get_participants(group_entity, limit=limit)
                for user in participants:
                    try:
                        await self.client(InviteToChannelRequest(target_entity, [user.id]))
                        added += 1
                        print(f'➕ Добавлен {user.first_name} в {target_channel}')
                        time.sleep(random.randint(3, 7))
                        if added >= limit:
                            return added
                    except Exception as e:
                        print(f'❌ Ошибка: {e}')
            except Exception as e:
                print(f'❌ Не удалось получить группу {group}: {e}')
        return added

    async def run_boost(self):
        """Запускает накрутку для всех каналов."""
        await self.client.start()
        print('🚀 Запуск накрутки подписчиков...')
        for channel in self.target_channels:
            await self.add_members_from_channel('@durov', channel, limit=5)
            await self.add_from_public_groups(channel, limit=3)
            await asyncio.sleep(5)

# ---- 3. ВЗАИМОПИАР С OCR (НОВОЕ) ----
class MutualPRBot:
    """Бот для взаимопиара с проверкой скриншотов через OCR."""
    def __init__(self, bot_token):
        self.bot_token = bot_token
        self.api_url = f'https://api.telegram.org/bot{bot_token}'

    def send_message(self, chat_id, text):
        url = f'{self.api_url}/sendMessage'
        requests.post(url, json={'chat_id': chat_id, 'text': text})

    def check_screenshot(self, photo_path):
        """Здесь должна быть интеграция с easyocr для проверки скриншотов."""
        # Заглушка — в реальном коде добавляется easyocr
        print('📸 Проверка скриншота (OCR)...')
        return True

    def run_pr_cycle(self, channel):
        """Запускает цикл взаимопиара."""
        self.send_message(channel, '📢 Запущен взаимопиар! Отправьте ссылку на канал.')
        # Логика сбора ссылок и проверки — по аналогии с MagistrNeo/TelegramBot[citation:5]

# ---- 4. БЕСПЛАТНЫЕ БОНУСНЫЕ ПОДПИСЧИКИ (НОВОЕ) ----
def get_free_subscribers(channel, count=10):
    """Имитация получения бесплатных подписчиков через биржи заданий."""
    print(f'🎁 Получение {count} бесплатных подписчиков для {channel}...')
    # В реальности здесь API к SMMPrime, Likemania или другим сервисам[citation:11]
    # Для демонстрации — эмуляция:
    for i in range(count):
        print(f'➕ Бонусный подписчик #{i+1} добавлен в {channel}')
        time.sleep(0.5)
    return count

# ---- ОСНОВНОЙ ЦИКЛ ПОСТИНГА + НАКРУТКА ----
def posting_loop():
    print('🔄 Фоновый постинг запущен...')
    posted = set()
    booster = SubscriptionBooster(API_ID, API_HASH)

    while True:
        try:
            # 1. Регулярный постинг
            for channel, config in channel_config.items():
                if random.random() < config.get('poll_frequency', 0.1):
                    if 'poll_question' in config and 'poll_options' in config:
                        send_poll(channel, config['poll_question'], config['poll_options'])
                        time.sleep(2)
                    continue

                for url in config['feeds']:
                    feed = feedparser.parse(url)
                    for entry in feed.entries[:1]:
                        if entry.link in posted:
                            continue
                        title = f"{get_emoji(channel)} {entry.title}"
                        summary = clean_summary(entry.summary) if hasattr(entry, 'summary') else ''
                        link = entry.link
                        image_url = get_image(entry)
                        tags = ' '.join(config.get('tags', []))
                        text = f"{title}\n\n{summary}\n\n🔗 {link}\n\n{tags}"

                        if image_url:
                            send_photo(channel, image_url, text)
                        else:
                            send_message(channel, text)

                        posted.add(entry.link)
                        time.sleep(random.randint(5, 10))

            # 2. Накрутка подписчиков (раз в сутки)
            print('🚀 Запуск накрутки подписчиков...')
            asyncio.run(booster.run_boost())

            # 3. Бесплатные бонусные подписчики (через биржи заданий)
            for channel in channel_config.keys():
                get_free_subscribers(channel, count=5)

            print('⏳ Цикл завершён. Жду 4 часа...')
            time.sleep(14400)  # 4 часа

        except Exception as e:
            print(f'❌ Ошибка в цикле: {e}')
            time.sleep(60)

# ---- ЗАПУСК ----
@app.route('/')
def home():
    return 'Бот работает!'

@app.route('/start')
def start():
    threading.Thread(target=posting_loop, daemon=True).start()
    return 'Постинг и накрутка запущены!'

@app.route('/boost')
def boost():
    """Ручной запуск накрутки."""
    booster = SubscriptionBooster(API_ID, API_HASH)
    asyncio.run(booster.run_boost())
    return 'Накрутка выполнена!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
