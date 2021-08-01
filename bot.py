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
    #регистрация, обработка имени и фамилии
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
        item1 = types.KeyboardButton("❓ Тест")
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



#####################################################################################


def test_number(message):
    test_number = message.text
    bot.send_message(message.chat.id, test_number)
    connect = sqlite3.connect('KompoDB.db')
    cursor = connect.cursor()
    question_arr = cursor.execute('SELECT question FROM test_question WHERE test == ? ORDER BY question_number', (message.text)).fetchall()
    answer_arr = cursor.execute('SELECT right_answer FROM test_question WHERE test == ? ORDER BY question_number', (message.text)).fetchall()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1);
    keyboard.add(types.KeyboardButton("Начать"))

    msg = bot.send_message(message.chat.id, "На прохождение тестов дается бесконечное количество времени и попыток, но в зачёт идет только первое прохождение теста.  ", reply_markup=keyboard)
    number_question = 0
    score = 0
    #bot.register_next_step_handler(msg, test ,test_number, question_arr , answer_arr, number_question,score)
    #test(msg, question_arr , answer_arr, number_question,score)


def test(message, test_number, question_arr , answer_arr, number_question, score):
    if int(number_question)<len(question_arr):
        true_answer = answer_arr[number_question]
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3);
        keyboard.add(types.KeyboardButton("1"),types.KeyboardButton("2"),types.KeyboardButton("3"));
        bot.send_message(message.chat.id,"Вопрос " + str(number_question+1))
        message = bot.send_message(message.chat.id, question_arr[number_question], reply_markup=keyboard)
        bot.register_next_step_handler(message,answer,test_number, question_arr,answer_arr, number_question, score, true_answer)
    else:
        connect = sqlite3.connect('KompoDB.db')
        cursor = connect.cursor()
        people_id = message.from_user.id
        result = [people_id, test_number, score]
        cursor.execute("INSERT INTO users_result VALUES(?,?,?);", result)
        connect.commit()


        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, selective=False)
        item1 = types.KeyboardButton("❓ Тест")
        item2 = types.KeyboardButton("⚙️ Настройки")
        item3 = types.KeyboardButton("📚 Лекции")
        item4 = types.KeyboardButton("📞 Контакты")
        markup.add(item1, item3, item4, item2)
        msg = bot.send_message(message.chat.id, "Тест " +str(test_number) +" закончен \n Ваш балл: " + str(score), reply_markup=markup)
        #connect = sqlite3.connect('KompoDB.db')

def answer(message,test_number, question_arr,answer_arr, number_question, score, true_answer):

    mt = str(message.text)
    ta = str(true_answer[0])
    if message.text == "1":
        if mt == ta:
            score += 1
        number_question += 1
        test(message, test_number, question_arr , answer_arr, number_question, score)
    elif message.text == "2":
        if mt == ta:
            score += 1
        number_question += 1
        test(message, test_number, question_arr , answer_arr, number_question, score)
    elif message.text == "3":
        if mt == ta:
            score += 1
        number_question += 1
        test(message, test_number, question_arr , answer_arr, number_question, score)
    else:
        #обратотка не кнопки
        msg = bot.send_message(message.chat.id, "Введите вариант ответа 1, 2 или 3")
        bot.register_next_step_handler(msg,answer,test_number, question_arr,answer_arr, number_question, score, true_answer)



    #msg = bot.register_next_step_handler(user_answer,test,question_arr,answer_arr, number_question, score)
    #test(message, question_arr , answer_arr, number_question, score)


    #cursor = connect.cursor()
    #people_id =  message.from_user.id
    #result =[people_id, test_number, score]

    #cursor.execute("INSERT INTO users_result VALUES(?,?,?);", result)

@bot.callback_query_handler(func=lambda call: True)

def callback_worker(call):
    connect = sqlite3.connect('KompoDB.db')
    cursor = connect.cursor()
    if call.data == 'test':
        #Сделать обратотку номера теста
        number = bot.send_message(call.message.chat.id, "Напиши номер теста")
        bot.register_next_step_handler(number, test_number)

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
        key2 = types.InlineKeyboardButton("МП", callback_data='machineproduct')
        markup.add(key1, key2)
        bot.send_message(call.message.chat.id, 'Выберите рабочее место:', reply_markup=markup)
    elif call.data == 'machineproduct':
        markup = types.InlineKeyboardMarkup(row_width=2)
        key1 = types.InlineKeyboardButton("Часть 1", callback_data='metoda1', url="https://drive.google.com/drive/folders/1SrpXFa2VA6w5z7PCr084Md4zEkXOpUQD?usp=sharing")
        key2 = types.InlineKeyboardButton("Тест 1", callback_data='test1')
        key3 = types.InlineKeyboardButton("Часть 2", callback_data='metoda2', url="https://drive.google.com/drive/folders/1TA-wpMNR2_JUb8zl3E9Eg3SIG7QX_pGl?usp=sharing")
        key4 = types.InlineKeyboardButton("Тест 2", callback_data='test1')
        key5 = types.InlineKeyboardButton("Часть 3", callback_data='metoda3', url="https://drive.google.com/drive/folders/1TVClZ4pPA3Z7t70vF1QXR_hMPpdEd1Dp?usp=sharing")
        key6 = types.InlineKeyboardButton("Тест 3", callback_data='test1')
        key7 = types.InlineKeyboardButton("Часть 4", callback_data='metoda4', url="https://drive.google.com/drive/folders/1TZUzOpKV_SFo6UXPlwHZgAUh3Pt8gYyu?usp=sharing")
        key8 = types.InlineKeyboardButton("Тест 4", callback_data='test1')
        key9 = types.InlineKeyboardButton("Часть 5", callback_data='metoda1', url="https://drive.google.com/drive/folders/1SrpXFa2VA6w5z7PCr084Md4zEkXOpUQD?usp=sharing")
        key10 = types.InlineKeyboardButton("Тест 5", callback_data='test1')
        key11 = types.InlineKeyboardButton("Часть 6", callback_data='metoda2', url="https://drive.google.com/drive/folders/1TA-wpMNR2_JUb8zl3E9Eg3SIG7QX_pGl?usp=sharing")
        key12 = types.InlineKeyboardButton("Тест 6", callback_data='test2')
        key13 = types.InlineKeyboardButton("Часть 7", callback_data='metoda3', url="https://drive.google.com/drive/folders/1TVClZ4pPA3Z7t70vF1QXR_hMPpdEd1Dp?usp=sharing")
        key14 = types.InlineKeyboardButton("Тест 7", callback_data='test3')
        key15 = types.InlineKeyboardButton("Часть 8", callback_data='metoda4', url="https://drive.google.com/drive/folders/1TZUzOpKV_SFo6UXPlwHZgAUh3Pt8gYyu?usp=sharing")
        key16 = types.InlineKeyboardButton("Тест 8", callback_data='test4')
        key17 = types.InlineKeyboardButton("Часть 9", callback_data='metoda1', url="https://drive.google.com/drive/folders/1SrpXFa2VA6w5z7PCr084Md4zEkXOpUQD?usp=sharing")
        key18 = types.InlineKeyboardButton("Тест 9", callback_data='test1')
        key19 = types.InlineKeyboardButton("Часть 10", callback_data='metoda2', url="https://drive.google.com/drive/folders/1TA-wpMNR2_JUb8zl3E9Eg3SIG7QX_pGl?usp=sharing")
        key20 = types.InlineKeyboardButton("Тест 10", callback_data='test2')
        key21 = types.InlineKeyboardButton("Часть 11", callback_data='metoda3', url="https://drive.google.com/drive/folders/1TVClZ4pPA3Z7t70vF1QXR_hMPpdEd1Dp?usp=sharing")
        key22 = types.InlineKeyboardButton("Тест 11", callback_data='test3')
        key23 = types.InlineKeyboardButton("Часть 12", callback_data='metoda4', url="https://drive.google.com/drive/folders/1TZUzOpKV_SFo6UXPlwHZgAUh3Pt8gYyu?usp=sharing")
        key24 = types.InlineKeyboardButton("Тест 12", callback_data='test4')
        markup.add(key1, key2, key3, key4, key5, key6, key7, key8, key9, key10,key11,key12,key13,key14,key15,key16,key17,key18,key19,key20,key21,key22,key23,key24)
        msg = bot.send_message(call.message.chat.id, 'Выберите тест для прохождения: ', reply_markup=markup)
        bot.register_next_step_handler(msg, test_number)
        #bot.register_next_step_handler(msg, test)
    elif call.data == 'testStudent':
        markup = types.InlineKeyboardMarkup(row_width=2)
        key1 = types.InlineKeyboardButton("Методичка Студента", callback_data='metoda1')
        key2 = types.InlineKeyboardButton("Тест Студента", callback_data='test1')
        markup.add(key1, key2)
        bot.send_message(call.message.chat.id, 'Выберите тест для прохождения: ', reply_markup=markup)
    elif call.data == 'office':
        markup = types.InlineKeyboardMarkup(row_width=2)
        key1 = types.InlineKeyboardButton("Часть 1", callback_data='metoda1', url="https://drive.google.com/drive/folders/1SrpXFa2VA6w5z7PCr084Md4zEkXOpUQD?usp=sharing")
        key2 = types.InlineKeyboardButton("Тест 1", callback_data='test1')
        key3 = types.InlineKeyboardButton("Часть 2", callback_data='metoda2', url="https://drive.google.com/drive/folders/1TA-wpMNR2_JUb8zl3E9Eg3SIG7QX_pGl?usp=sharing")
        key4 = types.InlineKeyboardButton("Тест 2", callback_data='test2')
        key5 = types.InlineKeyboardButton("Часть 3", callback_data='metoda3', url="https://drive.google.com/drive/folders/1TVClZ4pPA3Z7t70vF1QXR_hMPpdEd1Dp?usp=sharing")
        key6 = types.InlineKeyboardButton("Тест 3", callback_data='test3')
        key7 = types.InlineKeyboardButton("Часть 4", callback_data='metoda4', url="https://drive.google.com/drive/folders/1TZUzOpKV_SFo6UXPlwHZgAUh3Pt8gYyu?usp=sharing")
        key8 = types.InlineKeyboardButton("Тест 4", callback_data='test4')
        markup.add(key1, key2, key3, key4, key5, key6, key7, key8)
        bot.send_message(call.message.chat.id, 'Выберите тест для прохождения: ', reply_markup=markup)
    elif call.data == 'result':
        bot.send_message(call.message.chat.id, 'Курс: Бережливое производство\n Номер теста: \n 1: 9/10 \n 2: \n 3: \n Проходной балл: 100 \n Ваш балл: 9  ')
    elif call.data == 'test2':
        bot.send_message(call.message.chat.id, '😉 Тут скоро будет тест 2')


@bot.message_handler(content_types=['text'])
def lalala(message):
     if message.chat.type == 'private':
        if message.text == '❓ Тест':
            markup = types.InlineKeyboardMarkup(row_width=2)
            keyWorker = types.InlineKeyboardButton("👷‍♂️ Сотруднки КОМПО", callback_data='worker')
            keyStudend = types.InlineKeyboardButton("👨‍🎓 Студенты ", callback_data='student')
            keyResult = types.InlineKeyboardButton("😱 Результаты ", callback_data='result')
            markup.add(keyWorker, keyStudend,keyResult)
            bot.send_message(message.chat.id, 'Если Вы являетесь сотрудником Компо, то выберите соответствующую кнопку. Если Вы только начинаетв обучение, то выберите кнопку студент:', reply_markup=markup)
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
