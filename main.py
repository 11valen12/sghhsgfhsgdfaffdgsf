import telebot
from telebot import types
import re

# Замените 'YOUR_API_TOKEN' на ваш собственный API токен
bot = telebot.TeleBot('7135892639:AAE81aR0pS20ieyUF8N_D4AbqGRt7OAM7KU')

# Глобальная переменная для хранения информации о студентах
students_data = {}


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
    students_data[chat_id] = {'group': group}
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
    students_data[chat_id]['name'] = name
    bot.send_message(chat_id, "Введите причину вашего отсутствия:")
    bot.register_next_step_handler(message, process_reason)


# Обработка ввода причины отсутствия
def process_reason(message):
    chat_id = message.chat.id
    reason = message.text.strip()
    students_data[chat_id]['reason'] = reason
    bot.send_message(chat_id, "При необходимости загрузите фотографию документа:")
    bot.register_next_step_handler(message, process_photo)


# Обработка загрузки фотографии
def process_photo(message):
    chat_id = message.chat.id
    photo = None
    if message.photo:
        photo = message.photo[-1].file_id
    students_data[chat_id]['photo'] = photo
    send_attendance(chat_id, message.from_user.username)


# Отправка информации об отсутствии в общий чат
def send_attendance(chat_id, username):
    group = students_data[chat_id]['group']
    name = students_data[chat_id]['name']
    reason = students_data[chat_id]['reason']
    photo = students_data[chat_id]['photo']
    attendance_info = f"Username: @{username}\nГруппа: {group}\nФИО: {name}\nПричина: {reason}"
    if photo:
        bot.send_photo(-1002061475233, photo, caption=attendance_info)
    else:
        attendance_info += "\nФотография документа не загружена."
        bot.send_message(-1002061475233, attendance_info)
    bot.send_message(chat_id, "Ваша отметка об отсутствии отправлена.")


# Запуск бота
bot.polling()
