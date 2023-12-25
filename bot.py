import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from db import BotDB
from telebot import types
from Classes.mailer import Mailer

token = '6707157821:AAEc8Wn5vnYaIeVOL57aPI0DdwesAJhJnFA'
bot = telebot.TeleBot(token)

db = BotDB(host='nuepp3ddzwtnggom.chr7pe7iynqr.eu-west-1.rds.amazonaws.com', user='rue24w7t1d3p9zsu', port='3306', password='ietyzegykne7nmfm', database='bthc70gibxdwa44k')
mailer = Mailer(server='imap.mail.ru', user_email='smyshiyaev@mail.ru', password='dncYy9DE5EGYEEw2DEBm')


# НАЧАЛО РАБОТЫ
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    status_user = db.user_status_exists(user_id)
    if status_user is True:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        start_work_bot = types.KeyboardButton("Приступим")
        markup.add(start_work_bot)
        bot.send_message(message.chat.id, 'С возвращением !!!', reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        start_work_bot = types.KeyboardButton("Начать работу")
        markup.add(start_work_bot)
        bot.send_message(message.chat.id, "Добро пожаловать!", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Начать работу")
def handle_registration(message):
    user_id = message.from_user.id
    user_status = db.user_status_exists(user_id)
    bot.send_message(message.chat.id,
                     f'Для начало работы вам нужно иметь подтвержденный статус (статус подтверждается в базе)\nВаши '
                     f'данные:\nId:{user_id}\nStatus:{user_status}'
                     '')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    send_user_db = types.KeyboardButton('Отправить на проверку')
    markup.add(send_user_db)
    bot.send_message(message.chat.id, 'Для начала работы нажмите на кнопку "Отправить на проверку"',
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Отправить на проверку')
def handle_send_check(message):
    user_id = message.from_user.id
    print(user_id)
    db.add_user(user_id)
    bot.send_message(message.chat.id, 'Вы записаны и отправлены на проверку')

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    send_user_db = types.KeyboardButton('Проверить статус')
    markup.add(send_user_db)
    bot.send_message(message.chat.id, 'Теперь вам не обходимо проверить ваш статус', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Проверить статус')
def handle_checked(message):
    user_id = message.from_user.id
    user_status = db.user_status_exists(user_id)
    print(f'статус юзера {user_status}\n id:{user_id}')
    if user_status is True:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        send_user_db = types.KeyboardButton('Приступим')
        markup.add(send_user_db)
        bot.send_message(message.chat.id, 'Ваш статус подтвержден можете приступать к работе', reply_markup=markup)

    else:
        bot.send_message(message.chat.id, 'К сожалению ваш статус не подтвержден')


@bot.message_handler(func=lambda message: message.text == 'Приступим')
def handle_work(message):
    user_id = message.from_user.id
    user_status = db.user_status_exists(user_id)
    if user_status is True:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        create_filter = types.KeyboardButton('Создать фильтр')
        update_filter = types.KeyboardButton('Редактировать фильтр')
        delete_filter = types.KeyboardButton('Удалить фильтр')
        accept_people = types.KeyboardButton('Принять сотрудника')

        markup.add(create_filter, update_filter, delete_filter, accept_people)
        bot.send_message(message.chat.id, 'Приступаем', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Ваш статус не подтвержден перезагрузите бота командой "/start"')


user_data = {}


@bot.message_handler(func=lambda message: message.text == 'Создать фильтр')
def handle_create_filter(message):
    bot.send_message(message.chat.id, 'Укажите email клиента: ')
    bot.register_next_step_handler(message, handle_email_input)


def handle_email_input(message):
    email = message.text
    user_data['email'] = email

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    folders = mailer.get_parent_folders()
    for folder in folders:
        markup.add(types.KeyboardButton(folder))

    bot.send_message(message.chat.id, 'Укажите родительскую папку: ', reply_markup=markup)

    bot.register_next_step_handler(message, handle_parent_folder_input)


def handle_parent_folder_input(message):
    parent_folder = message.text
    user_data['parent_folder'] = parent_folder

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    client_folder = mailer.get_client_folders(parent_folder)
    for folder in client_folder:
        markup.add(types.KeyboardButton(folder))

    bot.send_message(message.chat.id, 'Укажите конечную папку: ', reply_markup=markup)
    bot.register_next_step_handler(message, handle_final_folder_input)


def handle_final_folder_input(message):
    user_id = message.from_user.id
    final_folder = message.text
    user_data['final_folder'] = final_folder

    parent_folder = user_data['parent_folder']

    client_folder = user_data['final_folder']

    mailer.is_folder_exists(parent_folder=parent_folder, folder_name=client_folder)

    db.add_filter(user_id=user_id, email=user_data['email'], parent_folder=user_data['parent_folder'],
                  client_folder=user_data['final_folder'])

    bot.send_message(message.chat.id, f"Email: {user_data['email']}\n"
                                      f"Родительская папка: {user_data['parent_folder']}\n"
                                      f"Конечная папка: {user_data['final_folder']}")

    user_data.clear()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    restart_bot = types.KeyboardButton('Продолжить')

    markup.add(restart_bot)

    bot.send_message(message.chat.id, 'Нажмите "продолжить" что войти в параметры', reply_markup=markup)

    bot.register_next_step_handler(message, handle_work)


@bot.message_handler(func=lambda message: message.text == 'Принять сотрудника')
def handle_create_filter(message):
    db.update_user_status(1)
    bot.send_message(message.chat.id, "Все сотрудники одобрены")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)


# @bot.message_handler()
# def checked_message(message):
#     user_id = message.from_user.id
#     user_status = db.user_status_exists(user_id)
#     if user_status is True:
#         markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#         create_filter = types.KeyboardButton('Создать фильтр')
#         update_filter = types.KeyboardButton('Редактировать фильтр')
#         delete_filter = types.KeyboardButton('Удалить фильтр')
#
#         markup.add(create_filter, update_filter, delete_filter)
#         bot.send_message(message.chat.id, 'Приступаем', reply_markup=markup)
#     else:
#         bot.send_message(message.chat.id, 'Решил наебать систему ? Перезагрузите боты: "/start"')


bot.infinity_polling()
