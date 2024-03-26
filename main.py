import telebot
from telebot import types
import re

# Замените 'YOUR_API_TOKEN' на ваш собственный API токен
bot = telebot.TeleBot('7135892639:AAE81aR0pS20ieyUF8N_D4AbqGRt7OAM7KU')

# Глобальная переменная для хранения информации о студентах
students_data = []

# Глобальная переменная для хранения информации о последних отметках
last_attendance = {}


# Обработчик команды /start и начала процесса отметки
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Привет! Этот бот поможет вам отметить ваше отсутствие на паре.")
    handle_attendance(message)


# Функция для проверки ввода ФИО
def is_valid_name(name):
    name_pattern = r'^[А-ЯЁA-Z][а-яёa-z]+\s[А-ЯЁA-Z][а-яёa-z]+$'
    return re.match(name_pattern, name)


# Обработка отметки отсутствия
def handle_attendance(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup()
    group_buttons = [types.InlineKeyboardButton(text=group, callback_data=group) for group in ["Дв311", "1321", "1212", "П21", "3211"]]
    markup.add(*group_buttons)
    bot.send_message(chat_id, "Выберите вашу группу:", reply_markup=markup)


# Обработка нажатия кнопки с выбором группы
@bot.callback_query_handler(func=lambda call: True)
def process_group_callback(call):
    group = call.data
    chat_id = call.message.chat.id
    students_data.append({'group': group, 'chat_id': chat_id})
    bot.send_message(chat_id, "Введите ваше ФИО:")
    bot.register_next_step_handler(call.message, process_name)


# Обработка ввода ФИО
def process_name(message):
    chat_id = message.chat.id
    name = message.text.strip()
    if not is_valid_name(name):
        bot.send_message(chat_id, "Пожалуйста, введите ваше ФИО в формате Иванов Иван.")
        bot.register_next_step_handler(message, process_name)
        return
    group = next(item['group'] for item in students_data if item['chat_id'] == chat_id)
    last_attendance[chat_id] = {'group': group, 'name': name, 'username': message.from_user.username}
    bot.send_message(chat_id, "Введите причину вашего отсутствия:")
    bot.register_next_step_handler(message, process_reason)


# Обработка ввода причины отсутствия
def process_reason(message):
    chat_id = message.chat.id
    reason = message.text.strip()
    last_attendance[chat_id]['reason'] = reason
    bot.send_message(chat_id, "При необходимости загрузите фотографию документа:")
    bot.register_next_step_handler(message, process_photo)


# Обработка загрузки фотографии
def process_photo(message):
    chat_id = message.chat.id
    photo = None
    if message.photo:
        photo = message.photo[-1].file_id
    last_attendance[chat_id]['photo'] = photo
    send_attendance(chat_id)


# Отправка информации об отсутствии в общий чат
def send_attendance(chat_id):
    group = last_attendance[chat_id]['group']
    name = last_attendance[chat_id]['name']
    reason = last_attendance[chat_id]['reason']
    username = last_attendance[chat_id]['username']
    photo = last_attendance[chat_id]['photo']
    attendance_info = f"Группа: {group}\nФИО: {name}\nПричина: {reason}\n@{username}"
    if photo:
        bot.send_photo(-1002061475233, photo, caption=attendance_info)
    else:
        bot.send_message(-1002061475233, attendance_info)
    bot.send_message(chat_id, "Ваша отметка об отсутствии отправлена.")


# Обработчик команды для преподавателя получить последние 5 отметок
@bot.message_handler(commands=['last_attendance'])
def send_last_attendance(message):
    chat_id = message.chat.id
    args = message.text.strip().split()
    if len(args) != 2:
        bot.send_message(chat_id, "Пожалуйста, укажите группу после команды в формате /last_attendance Группа.")
        return
    group = args[1]
    last_attendance_for_group = [attendance for attendance in last_attendance.values() if attendance['group'] == group][-5:]
    if not last_attendance_for_group:
        bot.send_message(chat_id, f"Нет данных об отсутствии студентов в группе {group}.")
        return
    for attendance in last_attendance_for_group:
        attendance_info = f"Группа: {attendance['group']}\nФИО: {attendance['name']}\nПричина: {attendance['reason']}\n@{attendance['username']}"
        if attendance['photo']:
            bot.send_photo(chat_id, attendance['photo'], caption=attendance_info)
        else:
            bot.send_message(chat_id, attendance_info)


# Запуск бота
bot.polling()

