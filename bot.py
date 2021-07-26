import telebot
import config
import sqlite3

from telebot import types

bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    sti = open('static/welcome.tgs', 'rb')
    bot.send_sticker(message.chat.id, sti)
    connect = sqlite3.connect('KompoDB.db')
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER,
        user_name TEXT,
        user_secondName TEXT,
        PRIMARY KEY(id)
    )""")
    connect.commit()
    #обработка имени и фамилии
    if message.text == '/start':
        bot.send_message(message.chat.id, "Добро пожаловать, {0.first_name}!\nЯ - <b>{1.first_name}</b>, бот созданный чтобы пройти курс по бережливому производству.".format(message.from_user, bot.get_me()), parse_mode='html')
        bot.send_message(message.from_user.id, "Введите ваше настоящее имя :");
        bot.register_next_step_handler(message, get_name); #следующий шаг – функция get_name
    else:
        bot.send_message(message.from_user.id, 'Напиши /start');

def get_name(message): #получаем имя
    name = message.text;
    bot.send_message(message.from_user.id, 'Введите вашу настоящую фамилию: ');
    bot.register_next_step_handler(message, get_surname, name);


def get_surname(message, name): #получаем фамилию
    surname = message.text;
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2); #наша клавиатура
    keyboard.add(types.KeyboardButton("Да"),types.KeyboardButton("Нет"));
    question = 'Вас зовут '+name+' '+surname+'?';
    #bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
    msg = bot.send_message(message.chat.id, question,reply_markup=keyboard)
    bot.register_next_step_handler(msg,user_answer,name,surname)

def user_answer(message,name,surname):
    if message.text == "Да":
        connect = sqlite3.connect('KompoDB.db')
        cursor = connect.cursor()
        people_id = message.from_user.id
        cursor.execute(f"SELECT id FROM users WHERE id = {people_id}")
        data = cursor.fetchone()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, selective=False)
        item1 = types.KeyboardButton("❔ Тест")
        item2 = types.KeyboardButton("⚙️ Настройки")
        item3 = types.KeyboardButton("📚 Лекции")
        item4 = types.KeyboardButton("📞 Контакты")
        markup.add(item1, item3, item4, item2)
        if data is None:
            #add values in users
            user = [people_id, name, surname]
            cursor.execute("INSERT INTO users VALUES(?,?,?);", user)
            connect.commit()
            bot.send_message(message.chat.id, 'Запомню : )', reply_markup=markup)
        else:
           bot.send_message(message.chat.id, 'На ваше телеграмм id зарегистрирован пользователь', reply_markup=markup)
    elif message.text =="Нет":
        bot.send_message(message.chat.id, 'Введите корректное имя: ')
        bot.register_next_step_handler(message, get_name);

def test(message):
    bot.send_message(message.chat.id, "Типа теста" + str(message))

@bot.callback_query_handler(func=lambda call: True)

def callback_worker(call):
    connect = sqlite3.connect('KompoDB.db')
    cursor = connect.cursor()
    if call.data == 'test1':
        for i in range(10):
            question_arr = cursor.execute('SELECT question FROM test_question WHERE question_number == ?', (i+1,)).fetchone()
            question = question_arr[0]
            markup = types.InlineKeyboardMarkup(row_width=3)
            key1 = types.InlineKeyboardButton("1", callback_data='1')
            key2 = types.InlineKeyboardButton("2", callback_data='2')
            key3 = types.InlineKeyboardButton("3", callback_data='3')
            markup.add(key1, key2, key3)
            bot.send_message(call.message.chat.id, "Вопрос " + str(i+1)+ ":\n" + question , reply_markup=markup)
            #answer_arr = cursor.execute('SELECT right_answer FROM test_question WHERE question_number == ?', (i+1,)).fetchone()
            #answer = answer_arr[0]
            #bot.register_next_step_handler(call.message.chat.id, answer)
            #if (call.data == str(answer)):
            #    bot.send_message(call.message.chat.id, "Правильный ответ")
            #else:
            #    bot.send_message(call.message.chat.id, "Неправильный ответ")
    elif call.data == 'phone':
        bot.send_message(call.message.chat.id, '+375339113030')
    elif call.data == 'student':
        markup = types.InlineKeyboardMarkup(row_width=2)
        key1 = types.InlineKeyboardButton("ТЕСТ", callback_data='testStudent')
        markup.add(key1)
        bot.send_message(call.message.chat.id, 'Готовы к прохождению теста?', reply_markup=markup)
    elif call.data == 'worker':
        markup = types.InlineKeyboardMarkup(row_width=2)
        key1 = types.InlineKeyboardButton("Офис", callback_data='office')
        key2 = types.InlineKeyboardButton("Машинное производство", callback_data='machineproduct')
        markup.add(key1, key2)
        bot.send_message(call.message.chat.id, 'Выберите рабочее место:', reply_markup=markup)
    elif call.data == 'machineproduct':
        markup = types.InlineKeyboardMarkup(row_width=2)
        key1 = types.InlineKeyboardButton("Метода1", callback_data='metoda11')
        key2 = types.InlineKeyboardButton("Тест1", callback_data='test11')
        key3 = types.InlineKeyboardButton("Метода2", callback_data='metoda12')
        key4 = types.InlineKeyboardButton("Тест2", callback_data='test12')
        markup.add(key1, key2, key3,key4)
        msg = bot.send_message(call.message.chat.id, 'Выберите тест для прохождения: ', reply_markup=markup)
        bot.register_next_step_handler(msg, test)
    elif call.data == 'testStudent':
        markup = types.InlineKeyboardMarkup(row_width=2)
        key1 = types.InlineKeyboardButton("Методичка Студента", callback_data='metoda1')
        key2 = types.InlineKeyboardButton("Тест Студента", callback_data='test1')
        markup.add(key1, key2)
        bot.send_message(call.message.chat.id, 'Выберите тест для прохождения: ', reply_markup=markup)
    elif call.data == 'office':
        markup = types.InlineKeyboardMarkup(row_width=2)
        key1 = types.InlineKeyboardButton("Методичка 1", callback_data='metoda1', url="https://drive.google.com/drive/folders/1SrpXFa2VA6w5z7PCr084Md4zEkXOpUQD?usp=sharing")
        key2 = types.InlineKeyboardButton("Тест 1", callback_data='test1')
        key3 = types.InlineKeyboardButton("Методичка 2", callback_data='metoda2', url="https://drive.google.com/drive/folders/1TA-wpMNR2_JUb8zl3E9Eg3SIG7QX_pGl?usp=sharing")
        key4 = types.InlineKeyboardButton("Тест 2", callback_data='test2')
        key5 = types.InlineKeyboardButton("Методичка 3", callback_data='metoda3', url="https://drive.google.com/drive/folders/1TVClZ4pPA3Z7t70vF1QXR_hMPpdEd1Dp?usp=sharing")
        key6 = types.InlineKeyboardButton("Тест 3", callback_data='test3')
        key7 = types.InlineKeyboardButton("Методичка 4", callback_data='metoda4', url="https://drive.google.com/drive/folders/1TZUzOpKV_SFo6UXPlwHZgAUh3Pt8gYyu?usp=sharing")
        key8 = types.InlineKeyboardButton("Тест 4", callback_data='test4')
        markup.add(key1, key2, key3, key4, key5, key6, key7, key8)
        bot.send_message(call.message.chat.id, 'Выберите тест для прохождения: ', reply_markup=markup)
    elif call.data == 'result':
        bot.send_message(call.message.chat.id, 'Курс: Бережливое производство\n Номер теста: \n 1: 9/10 \n 2: \n 3: \n Проходной балл: 100 \n Ваш балл: 9  ')
    elif call.data == 'test2':
        bot.send_message(call.message.chat.id, '😉 Тут скоро будет тест 2')
    elif call.data == 'metoda1':
        bot.send_message(call.message.chat.id, 'Методичка 1 '+ '\n' +
         'После упорной работы по внедрению системы 5S ,наблюдая улучшения, сотрудники начинают говорить: «Мы сделали это!» Они могут расслабиться, успокоиться на некоторое время (или, что еще хуже, вообще опустить руки). '+ '\n' +
         'Существуют силы, которые пытаются возвратить ситуацию к прежнему состоянию, поэтому руководству крайне важно создать систему, обеспечивающую непрерывность реализации пяти S.')
    elif call.data == 'metoda2':
        bot.send_message(call.message.chat.id, 'Методичка 2 '+ '\n' +
         'Надо, что бы люди относились к своим рабочим местам как к своему личному дому на берегу моря, где каждый квадратный сантиметр стоит целое состояние. Как только вы добьетесь этого сдвига в восприятии, каждый работник начнет смотреть на процесс совсем другими глазами '+ '\n' +
         '5S – это не уборка, это метод организации рабочего пространства. Это то, как вы видите свою работу.')

@bot.message_handler(content_types=['text'])
def lalala(message):
     if message.chat.type == 'private':
        if message.text == '❔ Тест':
            markup = types.InlineKeyboardMarkup(row_width=2)
            keyWorker = types.InlineKeyboardButton("👷‍♂️ Сотруднки КОМПО", callback_data='worker')
            keyStudend = types.InlineKeyboardButton("👨‍🎓 Студенты ", callback_data='student')
            keyResult = types.InlineKeyboardButton("😱 Результаты ", callback_data='result')
            markup.add(keyWorker, keyStudend,keyResult)
            bot.send_message(message.chat.id, 'На прохождение тестов дается бесконечное количество времени и попыток, но в зачот идет только первое прохождение тестов. Если Вы являетесь сотрудником Компо, то выберите соответствующую кнопку. Если Вы только начинаетв обучение, то выберите кнопку студент:', reply_markup=markup)
        elif message.text == '⚙️ Настройки':
            markup = types.InlineKeyboardMarkup(row_width=2)
            keyResName = types.InlineKeyboardButton("🙅‍♂️ Сбросить имя", callback_data='resName')
            keyTechHelp = types.InlineKeyboardButton("🆘 Тех. поддержка", callback_data='techHelp', url ="https://t.me/Ros_Mic")
            markup.add(keyResName, keyTechHelp)
            bot.send_message(message.chat.id, 'В настройках Вы можете изменить своё имя и написать в тех. поддержку', reply_markup=markup)
        elif message.text == '📚 Лекции':
            markup = types.InlineKeyboardMarkup(row_width=2)
            item1 = types.InlineKeyboardButton("📖 Лекции", callback_data='lecs', url="https://drive.google.com/drive/folders/1CTXTahfl6nSvhXh61aYB5mI1IyKDArT6?usp=sharing")
            markup.add(item1)
            bot.send_message(message.chat.id, 'Здесь Вы можете ознакомиться со всеми материалами', reply_markup=markup)

        elif message.text == '📞 Контакты':
            markup = types.InlineKeyboardMarkup(row_width=2)
            item1 = types.InlineKeyboardButton("🌐 Сайт", callback_data='website', url="https://kompo.by")
            item2 = types.InlineKeyboardButton("☎️ Телефон", callback_data='phone')
            item3 = types.InlineKeyboardButton("📷 Инстаграмм", callback_data='inst', url="https://www.instagram.com/kompo_by/")
            item4 = types.InlineKeyboardButton("💻 Facebook", callback_data='facebook', url="https://www.facebook.com/kompoequipment")

            markup.add(item1, item2, item3, item4)
            bot.send_message(message.chat.id, 'Здесь Вы можете свзаться с нами', reply_markup=markup)

bot.polling(none_stop=True)
