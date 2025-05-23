import csv
from io import StringIO
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    Filters,
    ConversationHandler,
    Dispatcher,
    CallbackContext
)
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import chardet
import time
import logging
from datetime import datetime, timedelta
from telegram.utils.helpers import escape_markdown

import yake
import uuid
from fuzzywuzzy import process

import os
import threading
from flask import Flask, request

import pytz

import logging

# Настройка логгера
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = '7253322237:AAFRw8dOKC7Pus2MEsJkpFxw69z92M_BYk8'
TABULA = 'https://docs.google.com/spreadsheets/d/13VT8JYgHeV15OVWMyquFffqGK_YBO8nPuFzf6PTMFkw/export?format=csv'
TABULA_kids = 'https://docs.google.com/spreadsheets/d/1dsDE2ydedzEAwdtHJESx39o5Clb2cEnV5ySAGFjW_eQ/export?format=csv'
SCHEDULE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1YOMc2k5hTNFMYeie_zbDLjMqmBRPGPKKSD8r6Tr9R9Y/export?format=csv"
CHANNEL_ID = '-1002429128033'
CHANNEL_LINK_PART = "2429128033"
GROUP_ID = '-1002427182837'
TIMEZONE = pytz.timezone('Asia/Novosibirsk')
RENDER_EXTERNAL_HOSTNAME = 'cyberbyson-pre-alpha.onrender.com'

CODE_INPUT = 0
DIRECTOR_ACTION = 1
STAFF_ACTION = 2
CHOOSE_RECIPIENT = 3
INPUT_MESSAGE = 4
CHOOSE_DIRECTION = 5
CHOOSE_TEAM = 6
CHOOSE_TOURNAMENT = 7
STUDENTS_ACTION = 8
PARENTS_ACTION = 9
WAIT_FOR_RESPONSE = 10
REQUEST_EQUIPMENT = 11
INPUT_STUDENT_INFO = 12
CHOOSE_STUDENT = 13
INPUT_DUTY_TEXT = 14
INPUT_CHILD_NAME = 15
CHOOSE_CHILD = 16
INPUT_MESSAGE_FOR_CHILD = 17

def read_google_sheet(sheet_url):
    # Заменяем часть URL для экспорта в CSV
    csv_url = sheet_url.replace('/edit', '/export?format=csv')

    # Загружаем данные
    response = requests.get(csv_url)
    if response.status_code != 200:
        raise Exception("Не удалось загрузить таблицу. Проверьте ссылку и доступ.")

    # Определяем кодировку данных
    raw_data = response.content
    encoding = chardet.detect(raw_data)['encoding']

    # Декодируем данные с использованием определенной кодировки
    decoded_data = raw_data.decode(encoding)

    # Читаем CSV
    csv_data = StringIO(decoded_data)
    reader = csv.reader(csv_data)

    # Преобразуем данные в список словарей с указанием индексов колонок
    users_data = []
    for row in reader:
        if len(row) >= 9:  # Убедимся, что строка содержит все необходимые колонки
            user = {
                'код': row[0],        # 1-ая колонка
                'id': row[1],         # 2-ая колонка (ID телеграма)
                'имя': row[2],        # 3-я колонка
                'фамилия': row[3],    # 4-ая колонка (фамилия)
                'статус': row[4],     # 5-ая колонка
                'направление': row[5], # 6-ая колонка
                'команда': row[6],    # 7-ая колонка (команда)
                'судья': row[7],      # 8-ая колонка (судья)
                'технозондер': row[8], # 9-ая колонка (технозондер)
                'псин': row[9] # 10-ая колонка (псин)
            }
            users_data.append(user)

    return users_data

def read_google_sheet_sheet2(sheet_url):
    """
    Загружает данные из второй вкладки (Лист2) таблицы Google Sheets.
    """
    # Заменяем часть URL для экспорта в CSV и указываем gid второй вкладки
    csv_url = sheet_url.replace('/edit', '/export?format=csv&gid=GID_kids')

    # Загружаем данные
    response = requests.get(csv_url)
    if response.status_code != 200:
        raise Exception("Не удалось загрузить таблицу. Проверьте ссылку и доступ.")

    # Определяем кодировку данных
    raw_data = response.content
    encoding = chardet.detect(raw_data)['encoding']

    # Декодируем данные с использованием определенной кодировки
    decoded_data = raw_data.decode(encoding)

    # Читаем CSV
    csv_data = StringIO(decoded_data)
    reader = csv.reader(csv_data)

    # Преобразуем данные в список словарей с указанием индексов колонок
    parents_data = []
    for row in reader:
        if len(row) >= 5:  # Убедимся, что строка содержит все необходимые колонки
            parent = {
                'фамилия': row[0],        # 1-ая колонка
                'имя': row[1],    # 2-ая колонка
                'отчество': row[2],   # 3-я колонка
                'команда': row[3],    # 4-ая колонка
                'контакты': row[4]    # 5-ая колонка
            }
            parents_data.append(parent)

    return parents_data

def read_schedule_sheet(sheet_url: str) -> list:
    """
    Читает данные из таблицы расписания с нормализацией дат
    """
    csv_url = sheet_url.replace('/edit', '/export?format=csv')

    try:
        response = requests.get(csv_url)
        response.raise_for_status()

        raw_data = response.content
        encoding = chardet.detect(raw_data)['encoding']
        decoded_data = raw_data.decode(encoding)

        reader = csv.DictReader(decoded_data.splitlines())

        # Нормализуем даты в каждой строке
        normalized_data = []
        for row in reader:
            if 'дата' in row:
                row['дата'] = normalize_table_date(row['дата'])
            normalized_data.append(row)

        return normalized_data

    except Exception as e:
        raise Exception(f"Ошибка загрузки расписания: {str(e)}")

def get_current_date() -> str:
    """Возвращает текущую дату в формате 'd.mm' (например '8.04')"""
    now = datetime.now(TIMEZONE)
    return f"{now.day}.{now.month:02d}"

def normalize_table_date(date_str: str) -> str:
    """
    Приводит даты из таблицы к единому формату 'd.mm'
    Примеры:
      '8.04' -> '8.04'
      '08.04' -> '8.04'
      '8.4' -> '8.04'
    """
    try:
        day, month = map(int, date_str.split('.'))
        return f"{day}.{month:02d}"
    except:
        return date_str  # если не удалось разобрать, оставляем как есть

# Функция обработки команды /start. Отправляем приветственное сообщение и показываем главное меню.
def start(update: Update, context: CallbackContext) -> int:
    # Сбрасываем все данные пользователя
    context.user_data.clear()

    # Отправляем приветственное сообщение и показываем главное меню
    update.message.reply_text("Приветствуем, кожаный мешок!")
    show_main_menu(update, context)

    return ConversationHandler.END  # Сбрасываем состояние

# Главное меню – используется клавиатура первого типа (ReplyKeyboardMarkup)
# Главное меню – используется клавиатура первого типа (ReplyKeyboardMarkup)
def show_main_menu(update: Update, context: CallbackContext) -> None:
    keyboard = [
        ['Школьники', 'Сотрудники'],
        ['Родители'],
        ['Завершить диалог']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text("Выберите категорию:", reply_markup=reply_markup)

# Альтернативная функция для вызова главного меню из callback‑обработчика (так как update.message может отсутствовать)
def show_main_menu_in_chat(context: CallbackContext, chat_id: int) -> None:
    keyboard = [
        ['Школьники', 'Сотрудники'],
        ['Родители'],
        ['Завершить диалог']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    context.bot.send_message(chat_id=chat_id, text="Выберите категорию:", reply_markup=reply_markup)

# Inline‑меню для родителей
def show_parents_menu(update: Update, context: CallbackContext) -> int:
    # Загружаем данные из таблицы школьников (TABULA_kids)
    try:
        kids_data = read_google_sheet_sheet2(TABULA_kids)  # Функция для Лист2
        context.user_data['kids_data'] = kids_data  # Сохраняем данные школьников
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        update.message.reply_text("⚠️ Ошибка загрузки данных. Попробуйте позже.")
        return ConversationHandler.END

    # Показываем меню для родителей
    keyboard = [
        [InlineKeyboardButton("Пусть ребенок мне позвонит!", callback_data='parent_call')],
        [InlineKeyboardButton("Что привезти ребенку?", callback_data='parent_gift')],
        [InlineKeyboardButton("Расписание КЛШ", callback_data='parent_schedule')],
        [InlineKeyboardButton("Телефоны дирекции", callback_data='parent_director_phones')],
        [InlineKeyboardButton("Назад", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Выберите опцию для родителей:", reply_markup=reply_markup)
    return PARENTS_ACTION

# Inline‑меню для школьников
def show_students_menu(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton("Что такое КЛШ?", callback_data='student_info')],
        [InlineKeyboardButton("Как попасть в КЛШ?", callback_data='student_how_to')],
        [InlineKeyboardButton("Буклет этого года", callback_data='student_booklet')],
        [InlineKeyboardButton("Архив КЛШ", callback_data='student_archive')],
        [InlineKeyboardButton("Назад", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Выберите опцию для школьников:", reply_markup=reply_markup)
    return STUDENTS_ACTION  # Возвращаем состояние меню школьников

def show_director_menu(update: Update, context: CallbackContext) -> int:
    # Проверяем, есть ли сообщение в update
    if update.message:
        chat_id = update.message.chat_id
    else:
        chat_id = update.callback_query.message.chat_id

    keyboard = [
        [InlineKeyboardButton("НОВОСТИ", callback_data='news')],
        [InlineKeyboardButton("Сделать объявление...", callback_data='director_announcement')],
        [InlineKeyboardButton("Написать слона/педаль", callback_data='staff_write_something')],
        [InlineKeyboardButton("Попросить купить", callback_data='buy')],
        [InlineKeyboardButton("Узнать контакты", callback_data='director_employee_contacts')],
        [InlineKeyboardButton("Назад", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с клавиатурой
    context.bot.send_message(chat_id=chat_id, text="Меню дирекции:", reply_markup=reply_markup)
    return DIRECTOR_ACTION

def show_staff_menu(update: Update, context: CallbackContext) -> int:
    # Проверяем, есть ли сообщение в update
    if update.message:
        chat_id = update.message.chat_id
    else:
        chat_id = update.callback_query.message.chat_id

    keyboard = [
        [InlineKeyboardButton("НОВОСТИ", callback_data='news')],
        [InlineKeyboardButton("Запросить технику", callback_data='request_equipment')],
        [InlineKeyboardButton("Выдать наряд", callback_data='assign_duty')],
        [InlineKeyboardButton("Написать сообщение...", callback_data='staff_write_message')],
        [InlineKeyboardButton("Написать слона/педаль", callback_data='staff_write_something')],
        [InlineKeyboardButton("Турниры", callback_data='staff_tournaments')],
        [InlineKeyboardButton("Дежурство", callback_data='nadzor')],
        [InlineKeyboardButton("Назад", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с клавиатурой
    context.bot.send_message(chat_id=chat_id, text="Меню сотрудников:", reply_markup=reply_markup)
    return STAFF_ACTION

def show_directions_menu(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    keyboard = [
        [InlineKeyboardButton("НТН", callback_data='НТН')],
        [InlineKeyboardButton("НЕН", callback_data='НЕН')],
        [InlineKeyboardButton("НОН", callback_data='НОН')],
        [InlineKeyboardButton("НФН", callback_data='НФН')],
        [InlineKeyboardButton("Назад", callback_data='back_to_director')]  # Кнопка "Назад"
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Выберите направление:", reply_markup=reply_markup)
    return CHOOSE_DIRECTION

def show_message_options(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    # Определяем, является ли пользователь дирекцией
    user = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)
    is_director = user and user.get('статус') == '0'

    keyboard = [
        [InlineKeyboardButton("...дирекции", callback_data='write_to_director')],
        [InlineKeyboardButton("...всем сотрудникам", callback_data='write_to_all_staff')],
        [InlineKeyboardButton("...всему направлению...", callback_data='write_to_department')],
        [InlineKeyboardButton("...вожатым команды...", callback_data='write_to_team_leaders')],
        [InlineKeyboardButton("...судьям турнира...", callback_data='write_to_tournament_judges')]
    ]

    # Добавляем кнопку "всем зондерам" только для дирекции
    if is_director:
        keyboard.insert(2, [InlineKeyboardButton("...всем зондерам", callback_data='write_to_zonders')])

    keyboard.append([InlineKeyboardButton("Назад", callback_data='back_to_previous_menu')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Выберите, кому отправить сообщение:", reply_markup=reply_markup)
    return CHOOSE_RECIPIENT

def show_team_leaders_menu(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    # Греческий алфавит
    teams = [
        "Альфа", "Бета", "Гамма", "Дельта", "Эпсилон", "Эта", "Тета",
        "Йота", "Каппа", "Лямбда", "Мю", "Ню", "Кси", "Омикрон", "Пи", "Ро",
        "Сигма", "Тау", "Ипсилон", "Фи", "Хи", "Пси", "Омега"
    ]

    # Создаем кнопки для каждой команды
    keyboard = [
        [InlineKeyboardButton(team, callback_data=f'team_{team}')] for team in teams
    ]
    keyboard.append([InlineKeyboardButton("Назад", callback_data='back_to_message_options')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Выберите команду:", reply_markup=reply_markup)
    return CHOOSE_TEAM

def show_tournament_judges_menu(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    # Список турниров
    tournaments = ["ФМТ", "ГУТ", "БХТ"]

    # Создаем кнопки для каждого турнира
    keyboard = [
        [InlineKeyboardButton(tournament, callback_data=f'tournament_{tournament}')] for tournament in tournaments
    ]
    keyboard.append([InlineKeyboardButton("Назад", callback_data='back_to_message_options')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Выберите турнир:", reply_markup=reply_markup)
    return CHOOSE_TOURNAMENT

def generate_unique_id() -> str:
    """
    Генерирует уникальный идентификатор для каждого сообщения.
    """
    return str(uuid.uuid4())

def generate_tags(text: str) -> str:
    """
    Генерирует теги из текста с помощью YAKE!.
    Возвращает строку с тегами, разделёнными пробелами.
    """
    # Инициализация YAKE!
    kw_extractor = yake.KeywordExtractor(lan="ru", n=5, dedupLim=0.5, windowsSize=15)

    # Извлечение ключевых слов
    keywords = kw_extractor.extract_keywords(text)

    # Сортировка по весу (от меньшего к большему) и выбор одного тега
    if keywords:
        sorted_keywords = sorted(keywords, key=lambda x: x[1])
        best_tag = sorted_keywords[0][0]  # Выбираем самый релевантный тег

        # Убираем символы, которые могут нарушить Markdown-разметку
        best_tag_cleaned = best_tag.replace('*', '').replace('_', '').replace('[', '').replace(']', '')

        # Заменяем пробелы на подчёркивания и формируем тег
        return f"#{best_tag_cleaned.replace(' ', '_')}"
    else:
        return ""

def director_announcement(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    return show_message_options(update, context)

def staff_write_message(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    return show_message_options(update, context)

def format_message_with_signature(message_text: str, sender_name: str, sender_surname: str, sender_status: str, recipient_type: str = None, **kwargs) -> str:
    """
    Формирует сообщение с подписью и тегами, без экранирования Markdown-разметки.
    """
    # Генерация тегов
    tags = generate_tags(message_text)

    # Определяем префикс в зависимости от типа получателя
    if recipient_type == 'director':
        prefix = "Дорогая дирекция!\n\n"
    elif recipient_type == 'all_staff':
        prefix = "Летняя Школа!\n\n"
    elif recipient_type == 'tournament_judges':
        prefix = f"Дорогие судьи {kwargs.get('tournament')}!\n\n"
    elif kwargs.get('direction'):
        prefix = f"Сотрудники {kwargs.get('direction')}!\n\n"
    elif kwargs.get('team'):
        prefix = f"Вожатые команды {kwargs.get('team')}!\n\n"
    else:
        prefix = ""

    # Определяем заголовок в зависимости от типа сообщения
    if recipient_type == 'equipment_request':  # Запрос техники
        header = "📢 ЗАПРОС ТЕХНИКИ 📢\n\n"
    elif sender_status == '0':  # Если отправитель — дирекция
        header = "❗️ ОБЪЯВЛЕНИЕ ❗️\n\n"
    else:  # Если отправитель — не дирекция
        header = "📨 НОВОЕ СООБЩЕНИЕ 📨\n\n"

    # Формируем итоговое сообщение
    formatted_message = (
        f"{header}"  # Заголовок
        f"{prefix}"  # Приписка после заголовка
        f"{message_text}\n\n"
        f"С уважением,\n"
        f"{sender_name} {sender_surname}"
    )

    return formatted_message

def format_schedule_message(schedule_data: dict, all_schedules: list) -> str:
    def safe_text(text: str) -> str:
        """Убираем все спецсимволы которые могут вызвать проблемы"""
        if not text:
            return ""
        return (
            str(text)
            .translate(str.maketrans('', '', '_*[]~`>#+=|{}<>'))
            .strip()
        )

    TOURNAMENTS = {
        'ФМТ': '📐',
        'ГУТ': '⚗️',
        'БХТ': '🧪'
    }

    EVENING_EVENTS = {
        'ВК': '\n• *ВК*\n{}',
        'Киноклуб': '\n• *Киноклуб*\n{}',
        'Самовар': '\n• *Самовар*\n{}'
    }

    # Блок дежурства
    current_date = get_current_date()  # Функция возвращает дату в формате таблицы (напр. "10.04")

    # Дежурство сегодня
    today_duty = safe_text(schedule_data.get('Дежурство', ''))

    # Дежурство завтра (ищем следующую дату)
    tomorrow_duty = ""
    try:
        # Преобразуем текущую дату в datetime
        current_day = datetime.strptime(current_date, "%d.%m")
        next_day = current_day + timedelta(days=1)
        next_date = next_day.strftime("%d.%m")

        # Ищем запись на следующий день
        tomorrow_schedule = next(
            (item for item in all_schedules
             if item.get('дата', '') == next_date),
            None
        )

        if tomorrow_schedule:
            tomorrow_duty = safe_text(tomorrow_schedule.get('Дежурство', ''))

    except Exception as e:
        logger.error(f"Ошибка поиска дежурства: {str(e)}")

    message = [f"📅 Сегодня {safe_text(schedule_data.get('день школы', ''))}-й день КЛШ!", ""]

    # Обработка ПИВ
    piv_value = schedule_data.get('ПИВ', '0')
    try:
        piv = int(piv_value)
        if piv == 1:
            message.extend([
                "🎓 *ПИВ-1*",
                "Состоится первый ПИВ!",
                "• Школьники и школьницы выбирают сквозные курсы и курсы 1 модуля",
                "• Приноси плакаты своих курсов",
                "• Время: 9:30–11:00",
                ""
            ])
        elif piv == 2:
            message.extend([
                "🎓 *ПИВ-2*",
                "Состоится второй ПИВ!",
                "• Школьники и школьницы выбирают только курсы 2 модуля",
                "• Приноси плакаты своих курсов",
                "• Время: 12:30–13:30",
                ""
            ])
        elif piv == 3:
            message.extend([
                "🎉 *ВИП*",
                "Состоится ВИП!",
                "• Школьники и школьницы показывают свои достижения на курсах",
                "• Они принесут плакаты!",
                "• Время: 11:00–12:30",
                ""
            ])
    except (ValueError, TypeError):
        pass

    # Турниры
    tournament_lines = []
    for key, emoji in TOURNAMENTS.items():
        value = safe_text(schedule_data.get(key, '0'))
        try:
            tournament_num = int(value)
            if tournament_num > 0:
                tournament_lines.append(f"• {key}-{tournament_num}")
        except ValueError:
            if value and value != "0":
                tournament_lines.append(f"• {value} {key}")

    if tournament_lines:
        message.extend([
            "🏆 *Пройдут следующие турниры:*",
            *tournament_lines,
            ""
        ])

    # Факультатив
    facultative = schedule_data.get('Факультатив', '0')
    try:
        fac_num = int(facultative)
        if fac_num > 0:
            message.extend([
                "📚 *Факультатив*",
                f"Состоится {fac_num}-е занятие факультатива!",
                ""
            ])
    except (ValueError, TypeError):
        pass

    # Вечерние мероприятия
    evening_events = []
    for key, template in EVENING_EVENTS.items():
        value = safe_text(schedule_data.get(key, ''))
        if value:
            evening_events.append(template.format(value))

    if evening_events:
        message.extend([
            "🕗 *Вечером:*",
            *evening_events,
            ""
        ])

    # Формируем сообщение о дежурстве
    if today_duty or tomorrow_duty:
        duty_message = []
        if today_duty:
            duty_message.append(f"Сегодня дежурят: {today_duty}")
        if tomorrow_duty:
            duty_message.append(f"К завтрашнему дежурству готовятся: {tomorrow_duty}")

        message.extend([
            "\n🫡 *Дежурство*",
            *duty_message,
            ""
        ])

    # Объявления
    announcements = safe_text(schedule_data.get('Объявления', ''))
    if announcements:
        message.extend([
            "❗️ *Объявления* ❗️",
            announcements,
            ""
        ])

    # Удаление последнего переноса
    if message and message[-1] == "":
        message.pop()

    return "\n".join(message).strip()

def send_copy_to_sender(update: Update, context: CallbackContext, message_text: str) -> None:
    """
    Отправляет копию сообщения отправителю с кнопками-ссылками и закрепляет его в диалоге.
    """
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)
    if not sender:
        return

    # Получаем уникальный идентификатор текущего сообщения
    unique_id = context.user_data.get('current_message_id')
    if not unique_id:
        return

    # Получаем данные для текущего сообщения
    message_data = context.user_data.get(unique_id, {})
    channel_message_id = message_data.get('channel_message_id')
    thread_id = message_data.get('thread_id')
    thread_url = f"https://t.me/c/{CHANNEL_LINK_PART}/{channel_message_id}?thread={thread_id}"

    # Формируем сообщение с подписью и тегами
    formatted_message = (
        f"📨 КОПИЯ СООБЩЕНИЯ 📨\n {generate_tags(message_text)}\n\n"
        f"{message_text}\n\n"
        f"С уважением,\n"
        f"{sender['имя']} {sender['фамилия']}"
    )

    # Создаем клавиатуру с кнопками-ссылками
    keyboard = [
        [
            InlineKeyboardButton("Ответы", url=thread_url),
            InlineKeyboardButton("Проблема решена!", callback_data=f'problem_solved_{unique_id}')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        # Отправляем сообщение отправителю
        sent_message = context.bot.send_message(
            chat_id=sender['id'],
            text=formatted_message,
            reply_markup=reply_markup
        )

        # Закрепляем сообщение в диалоге
        context.bot.pin_chat_message(chat_id=sender['id'], message_id=sent_message.message_id)

        # Сохраняем ID сообщения в данных текущего сообщения
        message_data['group_message_id'] = sent_message.message_id
        context.user_data[unique_id] = message_data

    except Exception as e:
        print(f"Ошибка отправки сообщения отправителю: {e}")

def send_plain_copy_to_sender(update: Update, context: CallbackContext, message_text: str) -> None:
    """
    Отправляет копию сообщения отправителю без кнопок, с тегами.
    """
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)
    if not sender:
        return  # Если отправитель не найден, ничего не делаем

    # Формируем текст сообщения для отправителя с тегами
    formatted_message = (
        f"📨 КОПИЯ СООБЩЕНИЯ 📨\n {generate_tags(message_text)}\n\n"
        f"{message_text}\n\n"
        f"С уважением,\n"
        f"{sender['имя']} {sender['фамилия']}"
    )

    # Отправляем сообщение отправителю без кнопок
    try:
        context.bot.send_message(chat_id=sender['id'], text=formatted_message)
    except Exception as e:
        print(f"Ошибка отправки сообщения отправителю: {e}")

def send_message_to_channel(context: CallbackContext, message_text: str, sender_name: str, sender_surname: str,
                          sender_status: str, recipient_type: str, **kwargs) -> None:
    """
    Отправляет копию сообщения в канал и сохраняет ID сообщения и thread_id.
    """
    formatted_message = format_message_with_signature(
        message_text, sender_name, sender_surname, sender_status, recipient_type, **kwargs
    )

    try:
        # Проверяем, есть ли thread_id
        thread_id = context.user_data.get('thread_id')
        reply_to_message_id = thread_id if thread_id else None

        # Отправляем сообщение в канал
        sent_message = context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=formatted_message,  # Отправляем текст как есть, без Markdown-разметки
            reply_to_message_id=reply_to_message_id  # Указываем thread_id, если он есть
        )

        # Генерируем уникальный идентификатор для этого сообщения
        unique_id = generate_unique_id()

        # Сохраняем данные для этого сообщения
        message_data = {
            'channel_message_id': sent_message.message_id,
            'thread_id': sent_message.message_id,  # Сохраняем thread_id
            'group_message_id': None  # Будет заполнено позже
        }
        context.user_data[unique_id] = message_data
        
        # Сохраняем уникальный идентификатор в context.user_data
        context.user_data['current_message_id'] = unique_id

    except Exception as e:
        print(f"Ошибка отправки сообщения в канал: {e}")

def send_plea_to_channel(context: CallbackContext, message_text: str, sender_name: str, sender_surname: str,
                          sender_status: str, recipient_type: str, **kwargs) -> None:
    """
    Отправляет копию сообщения в канал и сохраняет ID сообщения и thread_id.
    """
    formatted_message = format_message_with_signature(
        message_text, sender_name, sender_surname, sender_status, recipient_type, **kwargs
    )

    try:
        # Отправляем сообщение в канал
        sent_message = context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=formatted_message,  # Отправляем текст как есть, без Markdown-разметки
        )

        # Сохраняем ID сообщения и thread_id
        unique_id = generate_unique_id()
        message_data = {
            'channel_message_id': sent_message.message_id,
            'thread_id': sent_message.message_id,  # Используем message_id как thread_id
        }
        context.user_data[unique_id] = message_data

        # Сохраняем уникальный идентификатор в context.user_data
        context.user_data['current_message_id'] = unique_id

    except Exception as e:
        print(f"Ошибка отправки сообщения в канал: {e}")

def send_message_to_director(update: Update, context: CallbackContext) -> int:
    message_text = context.user_data.get('message_text')
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)

    if not sender:
        if update.callback_query:
            update.callback_query.edit_message_text("❌ Ошибка: отправитель не найден!")
        else:
            update.message.reply_text("❌ Ошибка: отправитель не найден!")
        return ConversationHandler.END

    # Получаем список ID дирекции (статус '0'), исключая отправителя
    receivers = [user['id'] for user in users_data
                 if user.get('статус') == '0' and user.get('id') and user['id'] != sender['id']]

    if not receivers:
        if update.callback_query:
            update.callback_query.edit_message_text("❌ Нет сотрудников в дирекции!")
        else:
            update.message.reply_text("❌ Нет сотрудников в дирекции!")
    else:
        for user_id in receivers:
            try:
                send_message_with_signature(
                    context, user_id, message_text, sender['имя'], sender['фамилия'], sender['статус'], recipient_type='director'
                )
            except Exception as e:
                print(f"Ошибка отправки сообщения {user_id}: {e}")

        # Отправляем подтверждение об успешной отправке
        if update.callback_query:
            update.callback_query.edit_message_text("✅ Сообщения отправлены!")
        else:
            update.message.reply_text("✅ Сообщения отправлены!")

def send_message_to_all_staff(update: Update, context: CallbackContext) -> int:
    message_text = context.user_data.get('message_text')
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)

    if not sender:
        if update.callback_query:
            update.callback_query.edit_message_text("❌ Ошибка: отправитель не найден!")
        else:
            update.message.reply_text("❌ Ошибка: отправитель не найден!")
        return ConversationHandler.END

    # Получаем список ID всех сотрудников, исключая отправителя
    receivers = [user['id'] for user in users_data
                 if user.get('id') and user['id'] != sender['id']]

    if not receivers:
        if update.callback_query:
            update.callback_query.edit_message_text("❌ Нет сотрудников для рассылки!")
        else:
            update.message.reply_text("❌ Нет сотрудников для рассылки!")
    else:
        for user_id in receivers:
            try:
                send_message_with_signature(
                    context, user_id, message_text, sender['имя'], sender['фамилия'], sender['статус'], recipient_type='all_staff'
                )
            except Exception as e:
                print(f"Ошибка отправки сообщения {user_id}: {e}")

        # Отправляем подтверждение об успешной отправке
        if update.callback_query:
            update.callback_query.edit_message_text("✅ Сообщения отправлены!")
        else:
            update.message.reply_text("✅ Сообщения отправлены!")

def send_message_to_direction(update: Update, context: CallbackContext) -> int:
    message_text = context.user_data.get('message_text')
    direction = context.user_data.get('selected_direction')
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)

    if not sender:
        if update.callback_query:
            update.callback_query.edit_message_text("❌ Ошибка: отправитель не найден!")
        else:
            update.message.reply_text("❌ Ошибка: отправитель не найден!")
        return ConversationHandler.END

    # Получаем список ID для рассылки, исключая отправителя
    receivers = [user['id'] for user in users_data
                 if user.get('направление') == direction and user['id'] != sender['id']]

    if not receivers:
        if update.callback_query:
            update.callback_query.edit_message_text("❌ Нет сотрудников в этом направлении!")
        else:
            update.message.reply_text("❌ Нет сотрудников в этом направлении!")
    else:
        for user_id in receivers:
            try:
                send_message_with_signature(
                    context, user_id, message_text, sender['имя'], sender['фамилия'], sender['статус'], direction
                )
            except Exception as e:
                print(f"Ошибка отправки сообщения {user_id}: {e}")

        # Отправляем подтверждение об успешной отправке
        if update.callback_query:
            update.callback_query.edit_message_text("✅ Сообщения отправлены!")
        else:
            update.message.reply_text("✅ Сообщения отправлены!")

def send_message_to_team(update: Update, context: CallbackContext) -> int:
    message_text = context.user_data.get('message_text')
    team = context.user_data.get('selected_team')
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)

    if not sender:
        if update.callback_query:
            update.callback_query.edit_message_text("❌ Ошибка: отправитель не найден!")
        else:
            update.message.reply_text("❌ Ошибка: отправитель не найден!")
        return ConversationHandler.END

    # Получаем список ID для рассылки, исключая отправителя
    receivers = [user['id'] for user in users_data
                 if user.get('команда') == team and user['id'] != sender['id']]

    if not receivers:
        if update.callback_query:
            update.callback_query.edit_message_text(f"❌ Нет вожатых в команде {team}!")
        else:
            update.message.reply_text(f"❌ Нет вожатых в команде {team}!")
    else:
        for user_id in receivers:
            try:
                send_message_with_signature(
                    context, user_id, message_text, sender['имя'], sender['фамилия'], sender['статус'], team=team
                )
            except Exception as e:
                print(f"Ошибка отправки сообщения {user_id}: {e}")

        # Отправляем подтверждение об успешной отправке
        if update.callback_query:
            update.callback_query.edit_message_text("✅ Сообщения отправлены!")
        else:
            update.message.reply_text("✅ Сообщения отправлены!")

def send_message_to_tournament_judges(update: Update, context: CallbackContext) -> int:
    message_text = context.user_data.get('message_text')
    tournament = context.user_data.get('selected_tournament')
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)

    if not sender:
        if update.callback_query:
            update.callback_query.edit_message_text("❌ Ошибка: отправитель не найден!")
        else:
            update.message.reply_text("❌ Ошибка: отправитель не найден!")
        return ConversationHandler.END

    # Определяем направления для выбранного турнира
    if tournament == 'ФМТ':
        directions = ['НТН']
    elif tournament == 'ГУТ':
        directions = ['НФН', 'НОН']
    elif tournament == 'БХТ':
        directions = ['НЕН']
    else:
        if update.callback_query:
            update.callback_query.edit_message_text("❌ Неизвестный турнир!")
        else:
            update.message.reply_text("❌ Неизвестный турнир!")
        return ConversationHandler.END

    # Получаем список ID судей для выбранного турнира, исключая отправителя
    receivers = [
        user['id'] for user in users_data
        if user.get('судья') == '1' and user.get('направление') in directions
        and user.get('id') and user['id'] != sender['id']
    ]

    if not receivers:
        if update.callback_query:
            update.callback_query.edit_message_text(f"❌ Нет судей для {tournament}!")
        else:
            update.message.reply_text(f"❌ Нет судей для {tournament}!")
    else:
        for user_id in receivers:
            try:
                send_message_with_signature(
                    context, user_id, message_text, sender['имя'], sender['фамилия'], sender['статус'], recipient_type='tournament_judges', tournament=tournament
                )
            except Exception as e:
                print(f"Ошибка отправки сообщения {user_id}: {e}")

        # Отправляем подтверждение об успешной отправке
        if update.callback_query:
            update.callback_query.edit_message_text("✅ Сообщения отправлены!")
        else:
            update.message.reply_text("✅ Сообщения отправлены!")

def send_message_with_button(update: Update, context: CallbackContext, recipient_type: str, **kwargs) -> None:
    message_text = context.user_data.get('message_text')
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)

    if not sender:
        if update.callback_query:
            update.callback_query.edit_message_text("❌ Ошибка: отправитель не найден!")
        else:
            update.message.reply_text("❌ Ошибка: отправитель не найден!")
        return

    # Отправляем сообщение в канал и получаем его ID и thread_id
    send_message_to_channel(context, message_text, sender['имя'], sender['фамилия'], sender['статус'], recipient_type, **kwargs)
    unique_id = context.user_data.get('current_message_id')
    message_data = context.user_data.get(unique_id, {})
    channel_message_id = message_data.get('channel_message_id')
    thread_id = message_data.get('thread_id')
    
    thread_url = f"https://t.me/c/{CHANNEL_LINK_PART}/{channel_message_id}?thread={thread_id}" # thread_url = f"https://t.me/c/{CHANNEL_LINK_PART}/{message_id}?thread={thread_id}"

    # Формируем сообщение с подписью и тегами
    formatted_message = format_message_with_signature(
        message_text, sender['имя'], sender['фамилия'], sender['статус'], recipient_type, **kwargs
    )

    # Добавляем кнопку "Подставить плечо" с ссылкой на тред
    keyboard = [[InlineKeyboardButton("Подставить плечо 💪", url=thread_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Определяем получателей, исключая отправителя
    if recipient_type == 'direction':
        receivers = [user['id'] for user in users_data
                     if user.get('направление') == kwargs.get('direction') and user['id'] != sender['id']]
    elif recipient_type == 'team':
        receivers = [user['id'] for user in users_data
                     if user.get('команда') == kwargs.get('team') and user['id'] != sender['id']]
    elif recipient_type == 'director':
        receivers = [user['id'] for user in users_data
                     if user.get('статус') == '0' and user['id'] != sender['id']]
    elif recipient_type == 'all_staff':
        receivers = [user['id'] for user in users_data
                     if user.get('id') and user['id'] != sender['id']]
    elif recipient_type == 'tournament_judges':
        receivers = [
            user['id'] for user in users_data
            if user.get('судья') == '1' and user.get('направление') in kwargs.get('directions', [])
            and user['id'] != sender['id']
        ]
    else:
        if update.callback_query:
            update.callback_query.edit_message_text("❌ Ошибка: тип получателя не определен!")
        else:
            update.message.reply_text("❌ Ошибка: тип получателя не определен!")
        return

    # Отправляем сообщение получателям
    for user_id in receivers:
        try:
            context.bot.send_message(chat_id=user_id, text=formatted_message, reply_markup=reply_markup)
        except Exception as e:
            print(f"Ошибка отправки сообщения {user_id}: {e}")

    # Отправляем копию сообщения отправителю
    send_copy_to_sender(update, context, message_text)

def send_message_with_signature(context: CallbackContext, chat_id: str, message_text: str, sender_name: str, sender_surname: str, sender_status: str, recipient_type: str = None, **kwargs) -> None:
    """
    Отправляет сообщение с подписью и, если нужно, с кнопкой "Подставить плечо".
    """
    # Формируем сообщение с подписью
    formatted_message = format_message_with_signature(
        message_text, sender_name, sender_surname, sender_status, recipient_type, **kwargs
    )

    # Отправляем сообщение
    context.bot.send_message(chat_id=chat_id, text=formatted_message, parse_mode='Markdown')

def handle_news(update: Update, context: CallbackContext) -> None:
    """
    Обрабатывает нажатие кнопки НОВОСТИ с учетом форматов дат
    """
    try:
        # Получаем объект сообщения
        if update.callback_query:
            query = update.callback_query
            message = query.message
            query.answer()  # Убираем часики у кнопки
        else:
            message = update.message

        # Загрузка и подготовка данных
        schedule_data = read_schedule_sheet(SCHEDULE_SHEET_URL)
        current_date = get_current_date()

        # Поиск по нормализованным датам
        today_schedule = None
        for item in schedule_data:
            if 'дата' in item and normalize_table_date(item['дата']) == current_date:
                today_schedule = item
                break

        # Формирование ответа
        if not today_schedule:
            response_text = "📭 На сегодня новостей нет!"
            logger.warning(f"Не найдено расписание для даты: {current_date}")
        else:
            response_text = format_schedule_message(today_schedule, schedule_data)
            logger.info(f"Успешно загружено расписание на {current_date}")

        # Отправка ответа
        if update.callback_query:
            context.bot.send_message(
                chat_id=message.chat_id,
                text=response_text,
                parse_mode='Markdown'
            )
        else:
            message.reply_text(response_text, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Ошибка в handle_news: {str(e)}", exc_info=True)
        error_msg = "⚠️ Не удалось загрузить расписание. Попробуйте позже."
        if update.callback_query:
            update.callback_query.answer(error_msg, show_alert=True)
        else:
            update.message.reply_text(error_msg)

def handle_recipient_choice(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    data = query.data

    if data == 'back_to_previous_menu':
        sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)
        if not sender:
            query.edit_message_text("❌ Ошибка: отправитель не найден!")
            return ConversationHandler.END

        if sender['статус'] == '0':
            return show_director_menu(update, context)
        else:
            return show_staff_menu(update, context)
    elif data == 'write_to_department':
        return show_directions_menu(update, context)
    elif data == 'write_to_team_leaders':
        return show_team_leaders_menu(update, context)
    elif data == 'write_to_tournament_judges':
        return show_tournament_judges_menu(update, context)
    elif data == 'write_to_director':
        context.user_data['recipient_type'] = 'director'
        query.edit_message_text(text="Введите послание:")
        return INPUT_MESSAGE
    elif data == 'write_to_all_staff':
        context.user_data['recipient_type'] = 'all_staff'
        query.edit_message_text(text="Введите послание:")
        return INPUT_MESSAGE
    else:
        context.user_data['recipient'] = data
        query.edit_message_text(text="Введите послание:")
        return INPUT_MESSAGE

def handle_wait_for_response(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    data = query.data

    # Получаем текст сообщения из context.user_data
    message_text = context.user_data.get('message_text')
    recipient_type = context.user_data.get('recipient_type')

    # Получаем отправителя
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)
    if not sender:
        query.edit_message_text("❌ Ошибка: отправитель не найден!")
        return ConversationHandler.END

    if data == 'wait_for_response_no':
        # Если выбран вариант "Нет", отправляем сообщение как обычно
        if recipient_type == 'direction':
            send_message_to_direction(update, context)
        elif recipient_type == 'team':
            send_message_to_team(update, context)
        elif recipient_type == 'director':
            send_message_to_director(update, context)
        elif recipient_type == 'all_staff':
            send_message_to_all_staff(update, context)
        elif recipient_type == 'tournament_judges':
            send_message_to_tournament_judges(update, context)
        else:
            query.edit_message_text("❌ Ошибка: тип получателя не определен!")
            return ConversationHandler.END

        # Отправляем копию отправителю без кнопок
        send_plain_copy_to_sender(update, context, message_text)

        # Возвращаем в меню
        if sender['статус'] == '0':  # Если отправитель — дирекция
            return show_director_menu(update, context)
        else:  # Если отправитель — сотрудник
            return show_staff_menu(update, context)

    elif data == 'wait_for_response_yes':
        # Если выбран вариант "Да", отправляем сообщение с кнопкой, копию отправителю и в канал
        if recipient_type == 'direction':
            send_message_with_button(update, context, recipient_type, direction=context.user_data.get('selected_direction'))
        elif recipient_type == 'team':
            send_message_with_button(update, context, recipient_type, team=context.user_data.get('selected_team'))
        elif recipient_type == 'director':
            send_message_with_button(update, context, recipient_type)
        elif recipient_type == 'all_staff':
            send_message_with_button(update, context, recipient_type)
        elif recipient_type == 'tournament_judges':
            send_message_with_button(update, context, recipient_type, tournament=context.user_data.get('selected_tournament'))
        else:
            query.edit_message_text("❌ Ошибка: тип получателя не определен!")
            return ConversationHandler.END

        # Возвращаем в меню
        if sender['статус'] == '0':  # Если отправитель — дирекция
            return show_director_menu(update, context)
        else:  # Если отправитель — сотрудник
            return show_staff_menu(update, context)
    else:
        query.edit_message_text("❌ Неизвестная команда.")
        return ConversationHandler.END

def handle_problem_solved_button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    print(f"[DEBUG] Callback data: {query.data}")  # Проверьте вывод в консоли

    # Извлекаем unique_id из callback_data
    if not query.data.startswith('problem_solved_'):
        return

    unique_id = query.data.split('_')[2]  # Формат: 'problem_solved_{unique_id}'
    handle_problem_solved(update, context, unique_id)

def handle_problem_solved(update: Update, context: CallbackContext, unique_id: str) -> None:
    """
    Обрабатывает нажатие кнопки "Проблема решена!" и удаляет сообщения из канала, группы и открепляет сообщение.
    """
    query = update.callback_query
    query.answer()

    # Получаем данные для этого сообщения
    message_data = context.user_data.get(unique_id, {})
    if not message_data:
        query.edit_message_text("❌ Ошибка: данные сообщения не найдены.")
        return

    # Удаляем сообщение из канала
    if 'channel_message_id' in message_data:
        try:
            context.bot.delete_message(chat_id=CHANNEL_ID, message_id=message_data['channel_message_id'])
        except Exception as e:
            print(f"Ошибка удаления сообщения из канала: {e}")

    # Удаляем сообщение из группы
    if 'group_message_id' in message_data:
        try:
            context.bot.delete_message(chat_id=GROUP_ID, message_id=message_data['group_message_id'])
        except Exception as e:
            print(f"Ошибка удаления сообщения из группы: {e}")

    # Открепляем сообщение в диалоге с ботом
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)
    if sender and 'group_message_id' in message_data:
        try:
            context.bot.unpin_chat_message(chat_id=sender['id'], message_id=message_data['group_message_id'])
            print(f"[DEBUG] Сообщение {message_data['group_message_id']} откреплено.")  # Отладочный вывод
        except Exception as e:
            print(f"Ошибка открепления сообщения: {e}")

    # Редактируем сообщение с кнопками, чтобы отобразить текст "Проблема решена"
    try:
        query.edit_message_text("✅ Проблема отмечена как решенная. Сообщения удалены и откреплены.")
    except Exception as e:
        print(f"Ошибка редактирования сообщения: {e}")

    # Удаляем данные для этого сообщения
    context.user_data.pop(unique_id, None)

def handle_code_input(update: Update, context: CallbackContext) -> int:
    input_code = update.message.text

    # Ищем пользователя по коду (1-ая колонка)
    user = next((u for u in users_data if str(u['код']) == input_code), None)

    if not user:
        update.message.reply_text("❌ Неверный код доступа!")
        show_main_menu(update, context)
        return ConversationHandler.END

    # Сохраняем код пользователя в context.user_data
    context.user_data['code'] = input_code

    status = user.get('статус')
    if status == '0':  # Дирекция
        return show_director_menu(update, context)
    elif status == '1':  # Сотрудники
        return show_staff_menu(update, context)
    else:
        update.message.reply_text("⚠️ Неизвестный статус пользователя!")
        show_main_menu(update, context)
        return ConversationHandler.END

def handle_input_message(update: Update, context: CallbackContext) -> int:
    # Сохраняем текст сообщения в context.user_data
    context.user_data['message_text'] = update.message.text

    # Создаем клавиатуру с кнопками "Да" и "Нет"
    keyboard = [
        [InlineKeyboardButton("Да", callback_data='wait_for_response_yes')],
        [InlineKeyboardButton("Нет", callback_data='wait_for_response_no')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Задаем вопрос "Ждете ли вы ответа?"
    update.message.reply_text("Ждете ли вы ответа?", reply_markup=reply_markup)

    # Переходим в состояние WAIT_FOR_RESPONSE
    return WAIT_FOR_RESPONSE

def handle_category(update: Update, context: CallbackContext) -> int:
    category = update.message.text
    if category == 'Завершить диалог':
        update.message.reply_text("Диалог завершён. До новых встреч!")
        return ConversationHandler.END
    elif category == 'Родители':
        return show_parents_menu(update, context)  # Возвращаем состояние PARENTS_ACTION
    elif category == 'Школьники':
        return show_students_menu(update, context)  # Возвращаем состояние STUDENTS_ACTION
    elif category == 'Сотрудники':
        try:
            # Загружаем таблицу при выборе "Сотрудники"
            global users_data
            users_data = read_google_sheet(TABULA)
            print("Данные успешно загружены!")
            update.message.reply_text("Укажите Ваш код доступа:")
            return CODE_INPUT  # Переходим в состояние ввода кода
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            update.message.reply_text("⚠️ Ошибка загрузки данных. Попробуйте позже.")
            return ConversationHandler.END
    return ConversationHandler.END

def handle_direction_choice(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    data = query.data

    if data == 'back_to_director':  # Обработка кнопки "Назад"
        # Получаем текущего пользователя
        sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)
        if not sender:
            query.edit_message_text("❌ Ошибка: отправитель не найден!")
            return ConversationHandler.END

        # Возвращаем в меню дирекции или сотрудников
        if sender['статус'] == '0':  # Дирекция
            return show_director_menu(update, context)
        else:  # Сотрудник
            return show_staff_menu(update, context)
    else:
        context.user_data['selected_direction'] = data
        context.user_data['recipient_type'] = 'direction'  # Тип получателя
        query.edit_message_text(text="Введите послание:")
        return INPUT_MESSAGE

def handle_team_choice(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    data = query.data

    if data.startswith('team_'):
        team = data.split('_')[1]
        context.user_data['selected_team'] = team
        context.user_data['recipient_type'] = 'team'  # Добавляем тип получателя
        query.edit_message_text(text=f"Введите сообщение для команды {team}:")
        return INPUT_MESSAGE
    elif data == 'back_to_message_options':
        return show_message_options(update, context)
    else:
        query.edit_message_text("❌ Неизвестная команда.")
        return ConversationHandler.END

def handle_tournament_choice(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    data = query.data

    if data.startswith('tournament_'):
        tournament = data.split('_')[1]
        context.user_data['selected_tournament'] = tournament  # Сохраняем выбранный турнир
        context.user_data['recipient_type'] = 'tournament_judges'  # Тип получателя — судьи турнира
        query.edit_message_text(text=f"Введите сообщение для судей {tournament}:")
        return INPUT_MESSAGE
    elif data == 'back_to_message_options':
        return show_message_options(update, context)
    else:
        query.edit_message_text("❌ Неизвестный турнир.")
        return ConversationHandler.END

def handle_request_equipment(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    # Запрашиваем у пользователя информацию о технике
    query.edit_message_text("Укажите, какая техника необходима, когда и куда ее принести:")

    # Переходим в состояние REQUEST_EQUIPMENT
    return REQUEST_EQUIPMENT

def handle_equipment_input(update: Update, context: CallbackContext) -> int:
    # Сохраняем текст сообщения в context.user_data
    equipment_request = update.message.text
    context.user_data['equipment_request'] = equipment_request

    # Получаем отправителя
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)
    if not sender:
        update.message.reply_text("❌ Ошибка: отправитель не найден!")
        return ConversationHandler.END

    # Отправляем запрос на технику в канал
    send_plea_to_channel(context, equipment_request, sender['имя'], sender['фамилия'], sender['статус'], recipient_type='equipment_request')

    # Получаем ID сообщения и thread_id из context.user_data
    unique_id = context.user_data.get('current_message_id')
    message_data = context.user_data.get(unique_id, {})
    channel_message_id = message_data.get('channel_message_id')
    thread_id = message_data.get('thread_id')

    if not channel_message_id or not thread_id:
        update.message.reply_text("❌ Ошибка: не удалось получить ID сообщения или треда.")
        return ConversationHandler.END

    # Формируем ссылку на тред
    thread_url = f"https://t.me/c/{CHANNEL_LINK_PART}/{channel_message_id}?thread={thread_id}"

    print(f"[DEBUG] Ссылка на тред: {thread_url}")  # Отладочный вывод

    # Получаем список технозондеров (у которых в 9-ой колонке стоит 1)
    tech_zonders = [user['id'] for user in users_data if user.get('технозондер') == '1']

    if not tech_zonders:
        update.message.reply_text("❌ Нет технозондеров для рассылки!")
    else:
        # Формируем сообщение с подписью
        formatted_message = (
            f"📢 ЗАПРОС ТЕХНИКИ 📢\n\n"
            f"{equipment_request}\n\n"
            f"С уважением,\n"
            f"{sender['имя']} {sender['фамилия']}"
        )

        # Создаем клавиатуру с кнопкой "Подставить техноплечо"
        keyboard = [
            [InlineKeyboardButton("Подставить техноплечо 🦾", url=thread_url)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Отправляем сообщение всем технозондерам
        for user_id in tech_zonders:
            try:
                context.bot.send_message(
                    chat_id=user_id,
                    text=formatted_message,
                    reply_markup=reply_markup
                )
            except Exception as e:
                print(f"Ошибка отправки сообщения {user_id}: {e}")

        # Уведомляем отправителя об успешной отправке
        update.message.reply_text("✅ Запрос на технику отправлен всем технозондерам!")

    # Возвращаемся в главное меню
    return show_staff_menu(update, context)

def handle_assign_duty(update: Update, context: CallbackContext) -> int:
    """Обрабатывает нажатие кнопки 'Выдать наряд'."""
    query = update.callback_query
    query.answer()

    # Отправляем сообщение с инструкцией через бота
    context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Введите имя и фамилию школьника:"
    )

    return INPUT_STUDENT_INFO

def handle_student_info_input(update: Update, context: CallbackContext) -> int:
    """
    Обрабатывает ввод пользователя и ищет школьников по имени и фамилии.
    Если найдено несколько совпадений, предлагает выбрать школьника.
    """
    user_input = update.message.text.strip()  # Получаем ввод пользователя

    # Разделяем ввод на слова
    parts = user_input.split()
    if len(parts) < 2:
        update.message.reply_text("❌ Пожалуйста, введите имя и фамилию школьника.")
        return INPUT_STUDENT_INFO

    # Загружаем данные из второй вкладки
    try:
        parents_data = read_google_sheet_sheet2(TABULA_kids)
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        update.message.reply_text("⚠️ Ошибка загрузки данных. Попробуйте позже.")
        return ConversationHandler.END

    # Формируем список строк для поиска (Фамилия Имя)
    search_list = [
        f"{parent['фамилия']} {parent['имя']}" for parent in parents_data
    ]

    # Ищем ближайшие совпадения с порогом 70
    matches = process.extract(user_input, search_list, limit=5)  # Ограничиваем количество совпадений

    # Фильтруем совпадения с порогом 70
    filtered_matches = [match for match, score in matches if score >= 70]

    if not filtered_matches:
        update.message.reply_text("❌ Не удалось найти школьника. Попробуйте еще раз.")
        return INPUT_STUDENT_INFO

    # Находим данные для всех совпадений
    matched_parents = [
        parent for parent in parents_data
        if f"{parent['фамилия']} {parent['имя']}" in filtered_matches
    ]

    # Если найдено только одно совпадение, сразу переходим к вводу наряда
    if len(matched_parents) == 1:
        context.user_data['selected_student'] = matched_parents[0]
        update.message.reply_text(
            f"✅ Наряд получит:\n\n"
            f"{matched_parents[0]['фамилия']} {matched_parents[0]['имя']} ({matched_parents[0]['команда']})"
        )
        # Отправляем отдельное сообщение с запросом на ввод текста наряда
        update.message.reply_text("Укажите причину наряда:")
        return INPUT_DUTY_TEXT

    # Если найдено несколько совпадений, предлагаем выбрать
    keyboard = [
        [InlineKeyboardButton(
            f"{parent['фамилия']} {parent['имя']} {parent['отчество']} ({parent['команда']})",
            callback_data=f"select_student_{idx}"
        )]
        for idx, parent in enumerate(matched_parents)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "Найдено несколько школьников. Выберите нужного:",
        reply_markup=reply_markup
    )

    # Сохраняем список совпадений в context
    context.user_data['matched_students'] = matched_parents

    return CHOOSE_STUDENT

def handle_student_choice(update: Update, context: CallbackContext) -> int:
    """
    Обрабатывает выбор школьника из списка.
    """
    query = update.callback_query
    query.answer()

    # Извлекаем индекс выбранного школьника
    selected_idx = int(query.data.split('_')[2])

    # Получаем список совпадений из context
    matched_students = context.user_data.get('matched_students')
    if not matched_students:
        query.edit_message_text("❌ Ошибка: данные школьников не найдены.")
        return ConversationHandler.END

    # Сохраняем выбранного школьника в context
    selected_student = matched_students[selected_idx]
    context.user_data['selected_student'] = selected_student

    # Уведомляем пользователя о выборе
    query.edit_message_text(
        f"✅ Наряд получит:\n\n"
        f"{selected_student['фамилия']} {selected_student['имя']} ({selected_student['команда']})\n"
    )

    # Отправляем отдельное сообщение с запросом на ввод текста наряда
    context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Укажите причину наряда:"
    )

    return INPUT_DUTY_TEXT

def handle_duty_text_input(update: Update, context: CallbackContext) -> int:
    """
    Обрабатывает ввод текста наряда и отправляет его.
    """
    duty_text = update.message.text.strip()  # Получаем текст наряда

    # Загружаем данные из таблицы TABULA
    try:
        users_data = read_google_sheet(TABULA)
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        update.message.reply_text("⚠️ Ошибка загрузки данных. Попробуйте позже.")
        return ConversationHandler.END

    # Получаем отправителя
    sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)
    if not sender:
        update.message.reply_text("❌ Ошибка: отправитель не найден!")
        return ConversationHandler.END

    # Получаем данные школьника из context
    selected_student = context.user_data.get('selected_student')
    if not selected_student:
        update.message.reply_text("❌ Ошибка: данные школьника не найдены.")
        return ConversationHandler.END

    # Формируем сообщение с нарядом
    message_text = (
        f"🚨 НАРЯД 🚨\n\n"
        f"КОМУ: {selected_student['имя']} {selected_student['фамилия']} ({selected_student['команда']})\n"
        f"ОТ КОГО: {sender['имя']} {sender['фамилия']} ({sender['команда']})\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{duty_text}"
    )

    # Получаем список пользователей, у которых в 10-й колонке стоит 1
    recipients = [user for user in users_data if user.get('псин') == '1']

    if not recipients:
        update.message.reply_text("❌ Нет назначенных сотрудников ПСИН.")
        return ConversationHandler.END

    # Отправляем сообщение каждому получателю
    for recipient in recipients:
        try:
            context.bot.send_message(
                chat_id=recipient['id'],
                text=message_text
            )
        except Exception as e:
            print(f"Ошибка отправки сообщения {recipient['id']}: {e}")

    # Уведомляем отправителя об успешной отправке
    update.message.reply_text("✅ Запрос отправлен всем сотрудникам ПСИН!")

    # Возвращаемся в главное меню
    return show_staff_menu(update, context)

def handle_parent_call(update: Update, context: CallbackContext) -> int:
    """
    Обрабатывает нажатие кнопки "Пусть ребенок мне позвонит!".
    Запрашивает имя ребенка.
    """
    query = update.callback_query
    query.answer()

    # Запрашиваем имя ребенка
    query.edit_message_text("Как зовут вашего ребенка?")

    return INPUT_CHILD_NAME

def handle_child_name_input(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text.strip()
    parts = user_input.split()

    if len(parts) < 2:
        update.message.reply_text("❌ Пожалуйста, введите имя и фамилию ребенка.")
        return INPUT_CHILD_NAME

    # Используем сохраненные данные из контекста
    kids_data = context.user_data.get('kids_data')
    if not kids_data:
        update.message.reply_text("⚠️ Ошибка: данные школьников не загружены.")
        return ConversationHandler.END

    # Поиск ребенка (аналогично предыдущей логике)
    search_list = [f"{kid['фамилия']} {kid['имя']}" for kid in kids_data]
    matches = process.extract(user_input, search_list, limit=5)
    filtered_matches = [match for match, score in matches if score >= 70]

    if not filtered_matches:
        update.message.reply_text("❌ Не удалось найти ребенка. Попробуйте еще раз.")
        return INPUT_CHILD_NAME

    matched_children = [
        kid for kid in kids_data
        if f"{kid['фамилия']} {kid['имя']}" in filtered_matches
    ]

    # Если найдено только одно совпадение, сразу переходим к вводу сообщения
    if len(matched_children) == 1:
        context.user_data['selected_child'] = matched_children[0]
        update.message.reply_text(
            f"✅ Вы выбрали:\n\n"
            f"{matched_children[0]['имя']} {matched_children[0]['фамилия']} ({matched_children[0]['команда']})"
        )
        # Отправляем отдельное сообщение с запросом на ввод текста наряда
        update.message.reply_text("Это сообщение будет направлено вожатым. Напишие, что нужно передать:")
        return INPUT_MESSAGE_FOR_CHILD

    # Если найдено несколько совпадений, предлагаем выбрать
    keyboard = [
        [InlineKeyboardButton(
            f"{child['фамилия']} {child['имя']} {child['отчество']} ({child['команда']})",
            callback_data=f"select_child_{idx}"
        )]
        for idx, child in enumerate(matched_children)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "Найдено несколько детей. Выберите нужного:",
        reply_markup=reply_markup
    )

    # Сохраняем список совпадений в context
    context.user_data['matched_children'] = matched_children

    return CHOOSE_CHILD

def handle_child_choice(update: Update, context: CallbackContext) -> int:
    """
    Обрабатывает выбор ребенка из списка.
    """
    query = update.callback_query
    query.answer()

    # Извлекаем индекс выбранного ребенка
    selected_idx = int(query.data.split('_')[2])

    # Получаем список совпадений из context
    matched_children = context.user_data.get('matched_children')
    if not matched_children:
        query.edit_message_text("❌ Ошибка: данные детей не найдены.")
        return ConversationHandler.END

    # Сохраняем выбранного ребенка в context
    selected_child = matched_children[selected_idx]
    context.user_data['selected_child'] = selected_child

    # Уведомляем пользователя о выборе
    query.edit_message_text(
        f"✅ Вы выбрали:\n\n"
        f"{selected_child['имя']} {selected_child['фамилия']} ({selected_child['команда']})"
    )

    # Отправляем отдельное сообщение с запросом на ввод текста наряда
    context.bot.send_message(
        chat_id=query.message.chat_id,
        text="Это сообщение будет направлено вожатым. Напишите, что нужно передать:"
    )
    return INPUT_MESSAGE_FOR_CHILD

def handle_message_for_child_input(update: Update, context: CallbackContext) -> int:
    """
    Обрабатывает ввод сообщения для ребенка и отправляет его вожатым.
    """
    message_text = update.message.text.strip()  # Получаем текст сообщения

    # Получаем данные ребенка из context
    selected_child = context.user_data.get('selected_child')
    if not selected_child:
        update.message.reply_text("❌ Ошибка: данные ребенка не найдены.")
        return ConversationHandler.END

    # Загружаем данные из таблицы TABULA (сотрудники)
    try:
        staff_data = read_google_sheet(TABULA)
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        update.message.reply_text("⚠️ Ошибка загрузки данных. Попробуйте позже.")
        return ConversationHandler.END

    # Получаем команду выбранного ребенка
    child_team = selected_child.get('команда')

    if not child_team:
        update.message.reply_text("❌ Ошибка: не удалось определить команду ребенка.")
        return ConversationHandler.END

    # Находим сотрудников с совпадающей командой
    matched_staff = [staff for staff in staff_data if staff.get('команда') == child_team]

    if not matched_staff:
        update.message.reply_text("❌ Не найдено вожатых для команды ребенка.")
        return ConversationHandler.END

    # Формируем сообщение для вожатых
    message_for_staff = (
        f"🙏 РОДИТЕЛИ ПЕРЕДАЮТ 🙏\n\n"
        f"{selected_child['имя']} {selected_child['фамилия']}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{message_text}"
    )

    # Отправляем сообщение каждому вожатому
    for staff in matched_staff:
        try:
            context.bot.send_message(
                chat_id=staff['id'],  # ID сотрудника
                text=message_for_staff
            )
        except Exception as e:
            print(f"Ошибка отправки сообщения {staff['id']}: {e}")

    # Уведомляем отправителя об успешной отправке
    update.message.reply_text("✅ Сообщение отправлено вожатым команды!")

    # Возвращаемся в главное меню
    return show_parents_menu(update, context)

# Обработка нажатий на inline‑кнопки.
def inline_button_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    # Пропускаем callback_data, которые начинаются с 'problem_solved_'
    if query.data.startswith('problem_solved_'):
        return ConversationHandler.END

    data = query.data

    if data == 'back_to_main':
        query.edit_message_text("Возвращаемся в главное меню.")
        show_main_menu_in_chat(context, query.message.chat_id)
        return ConversationHandler.END
    elif data == 'news':
        try:
            handle_news(update, context)
        except Exception as e:
            logger.error(f"News error: {str(e)}")
            query.edit_message_text("❌ Ошибка при загрузке новостей")
        return ConversationHandler.END
    elif data == 'assign_duty':
        return handle_assign_duty(update, context)  # Передаем query через update
    elif data == 'back_to_director':
        return show_director_menu(update, context)
    elif data == 'back_to_staff':
        return show_staff_menu(update, context)
    elif data == 'back_to_parents':
        return show_parents_menu(update, context)
    elif data == 'back_to_students':
        return show_students_menu(update, context)
    elif data == 'director_write_department':
        return show_directions_menu(update, context)
    elif data == 'director_announcement':
        return director_announcement(update, context)
    elif data == 'staff_write_message':
        return staff_write_message(update, context)
    elif data == 'request_equipment':  # Обработка кнопки "Запросить технику"
        return handle_request_equipment(update, context)
    elif data == 'assign_duty':  # Обработка кнопки "Выдать наряд"
        return handle_assign_duty(update, context)
    elif data == 'back_to_previous_menu':
        # Получаем текущего пользователя
        sender = next((u for u in users_data if str(u['код']) == context.user_data.get('code')), None)
        if not sender:
            query.edit_message_text("❌ Ошибка: отправитель не найден!")
            return ConversationHandler.END  # Завершаем диалог, если пользователь не найден

        # Возвращаем в меню соответствующей категории
        status = sender.get('статус')
        if status == '0':  # Дирекция
            return show_director_menu(update, context)
        elif status == '1':  # Сотрудник
            return show_staff_menu(update, context)
        elif status == '2':  # Родители
            return show_parents_menu(update, context)
        elif status == '3':  # Школьники
            return show_students_menu(update, context)
        else:
            query.edit_message_text("⚠️ Неизвестный статус пользователя!")
            return ConversationHandler.END  # Завершаем диалог, если статус неизвестен
    elif data in ['wait_for_response_yes', 'wait_for_response_no']:
        # Если данные относятся к новому функционалу, передаем их в handle_wait_for_response
        return handle_wait_for_response(update, context)
    elif data == 'problem_solved':
        # Обрабатываем нажатие кнопки "Проблема решена!"
        return handle_problem_solved(update, context)
    elif data == 'parent_call':  # Обработка кнопки "Пусть ребенок мне позвонит!"
        return handle_parent_call(update, context)
    else:
        query.edit_message_text(f"Вы выбрали опцию: {data}")
        return ConversationHandler.END  # Сбрасываем состояние после выполнения действия

def main() -> Updater:
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # 1. Первым регистрируем обработчик для кнопки "Проблема решена!"
    dp.add_handler(CallbackQueryHandler(handle_problem_solved_button, pattern=r'^problem_solved_'))

    # Настраиваем ConversationHandler для обработки состояний (например, ввода кодов доступа)
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(Filters.text & ~Filters.command, handle_category),
            CallbackQueryHandler(inline_button_handler)
        ],
        states={
            CODE_INPUT: [MessageHandler(Filters.text, handle_code_input)],
            DIRECTOR_ACTION: [CallbackQueryHandler(inline_button_handler)],
            STAFF_ACTION: [CallbackQueryHandler(inline_button_handler)],
            STUDENTS_ACTION: [CallbackQueryHandler(inline_button_handler)],  # Добавлено
            PARENTS_ACTION: [CallbackQueryHandler(inline_button_handler)],  # Добавлено
            CHOOSE_RECIPIENT: [CallbackQueryHandler(handle_recipient_choice)],
            INPUT_MESSAGE: [MessageHandler(Filters.text & ~Filters.command, handle_input_message)],
            WAIT_FOR_RESPONSE: [CallbackQueryHandler(handle_wait_for_response)],
            CHOOSE_DIRECTION: [CallbackQueryHandler(handle_direction_choice)],
            CHOOSE_TEAM: [CallbackQueryHandler(handle_team_choice)],
            CHOOSE_TOURNAMENT: [CallbackQueryHandler(handle_tournament_choice)],
            REQUEST_EQUIPMENT: [MessageHandler(Filters.text & ~Filters.command, handle_equipment_input)],
            INPUT_STUDENT_INFO: [MessageHandler(Filters.text & ~Filters.command, handle_student_info_input)],
            CHOOSE_STUDENT: [CallbackQueryHandler(handle_student_choice, pattern=r'^select_student_\d+$')],
            INPUT_DUTY_TEXT: [MessageHandler(Filters.text & ~Filters.command, handle_duty_text_input)],
            INPUT_CHILD_NAME: [MessageHandler(Filters.text & ~Filters.command, handle_child_name_input)],
            CHOOSE_CHILD: [CallbackQueryHandler(handle_child_choice, pattern=r'^select_child_\d+$')],
            INPUT_MESSAGE_FOR_CHILD: [MessageHandler(Filters.text & ~Filters.command, handle_message_for_child_input)],
        },
        fallbacks=[CommandHandler('start', start)]
    )

    dp.add_handler(conv_handler)

    # Добавляем обработчик для кнопки "Проблема решена!" с высоким приоритетом
    dp.add_handler(CallbackQueryHandler(handle_problem_solved_button, pattern='^problem_solved_'))

    dp.add_handler(CallbackQueryHandler(handle_news, pattern='^news$'))

    # Добавляем общий обработчик для остальных callback_data
    dp.add_handler(CallbackQueryHandler(inline_button_handler))

    # updater.start_polling()
    # updater.idle()

    # port = int(os.environ.get("PORT", 443))
    # hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "cyberbyson-pre-alpha.onrender.com")
    # updater.start_webhook(
         # listen="0.0.0.0",
         # port=port,
         # url_path=TOKEN,
         # webhook_url=f"https://{hostname}/{TOKEN}"
    # )
    # Регистрируем webhook в Telegram
    # updater.bot.set_webhook(f"https://{hostname}/{TOKEN}")
    # updater.idle()

    # выставляем webhook в Telegram (без порта в URL)
    hostname = os.environ["RENDER_EXTERNAL_HOSTNAME"]
    updater.bot.set_webhook(f"https://{hostname}/{TOKEN}")
    return updater

app = Flask(__name__)

@app.route("/")
def index():
    return "Сервис работает", 200

updater = main()
dp: Dispatcher = updater.dispatcher

@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook() -> str:
    # Пришёл апдейт от Telegram — передаём его в dispatcher
    data = request.get_json(force=True)
    update = Update.de_json(data, updater.bot)
    dp.process_update(update)
    return "OK"

# def run_server():
    # port = int(os.environ.get("PORT", 5000))  # Получаем порт из переменной окружения, по умолчанию 5000
    # Указываем прослушивание на всех интерфейсах (0.0.0.0)
    # pass # app.run(host="0.0.0.0", port=port, use_reloader=False)

@app.route("/health")
def health():
    return "OK", 200

threading.Thread(target=main, daemon=True).start()

if __name__ == "__main__":
    # Запускаем сервер в отдельном потоке, чтобы не блокировать основной процесс бота
    # server_thread = threading.Thread(target=main, daemon=True).start()
    # server_thread.daemon = True  # Делает поток демоном, чтобы он завершался вместе с основным процессом
    # server_thread.start()

    # Здесь запускается ваш основной код бота
    # print("Бот запущен!")
    # main()
     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 443)))
