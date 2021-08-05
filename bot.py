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
##############################

def result(message):
    connect = sqlite3.connect('KompoDB.db')
    cursor = connect.cursor()
    cursor.execute(f"SELECT test_number, score FROM users_result WHERE user_id = {message.from_user.id} ORDER BY test_number")
    records = cursor.fetchall()
    records =[[]]
    lenght = len(records)
    nl = '\n'
    for i in range(16):
        cursor.execute(f"SELECT test_number, score FROM users_result WHERE user_id = {message.from_user.id} AND test_number = {i+1}")
        data = cursor.fetchall()
        if len(data) == 0:
            records.append([[i+1],["-"]])
        else:
            records.append(data)
    for i in range(16):
        row = records[i]
        if i == 0 :
            message = "Курс: Бережливое производство\nОФИС \n"
            message += f'Тест {i+1}: {row[1] if row[0] == i+1 else "-" }{nl}'
        elif (i>0 & i<=4) | i > 6:
            message += f'Тест {i+1}: {row[1] if row[0] == i+1 else "-" }{nl}'
        elif i == 5:
            message += "МП\n"
            message += f'Тест {i+1}: {row[1] if row[0] == i+1 else "-" }{nl}'


    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, selective=False)
    item1 = types.KeyboardButton("❓ Тест")
    item2 = types.KeyboardButton("⚙️ Настройки")
    item3 = types.KeyboardButton("📚 Лекции")
    item4 = types.KeyboardButton("📞 Контакты")
    markup.add(item1, item3, item4, item2)
    bot.send_message(message.chat.id, message, reply_markup=markup)


#####################################################################################

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
        connect = sqlite3.connect('KompoDB.db')
        cursor = connect.cursor()
        people_id = message.from_user.id
        cursor.execute(f"SELECT user_id FROM users_result WHERE user_id = {people_id} and test_number = {test_number}")
        data = cursor.fetchone()
        if data is None:
            #add values in users
            result = [people_id, test_number, score]
            cursor.execute("INSERT INTO users_result VALUES(?,?,?);", result)
            connect.commit()
        else:
           bot.send_message(message.chat.id, 'Вы уже проходили '+str(test_number)+'-й тест')
        # обработка на повторяящийся результат теста
        cursor.execute("INSERT INTO users_result VALUES(?,?,?);", result)
        connect.commit()

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, selective=False)
        item1 = types.KeyboardButton("❓ Тест")
        item2 = types.KeyboardButton("⚙️ Настройки")
        item3 = types.KeyboardButton("📚 Лекции")
        item4 = types.KeyboardButton("📞 Контакты")
        markup.add(item1, item3, item4, item2)
        msg = bot.send_message(message.chat.id, "Тест закончен \nВаш балл: " + str(score), reply_markup=markup)


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
        msg = bot.send_message(message.chat.id, "Введите вариант ответа 1, 2 или 3")
        bot.register_next_step_handler(msg,answer,test_number, question_arr,answer_arr, number_question, score, true_answer)

@bot.callback_query_handler(func=lambda call: True)

def callback_worker(call):
    connect = sqlite3.connect('KompoDB.db')
    cursor = connect.cursor()
    for i in range(20):
        if call.data == 'test'+str(i):
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Тест выбран')
            test_number = str(i)
            connect = sqlite3.connect('KompoDB.db')
            cursor = connect.cursor()
            question_arr = cursor.execute('SELECT question FROM test_question WHERE test == ? ORDER BY question_number', (test_number,)).fetchall()
            answer_arr = cursor.execute('SELECT right_answer FROM test_question WHERE test == ? ORDER BY question_number', (test_number,)).fetchall()
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1);
            keyboard.add(types.KeyboardButton("Начать"))
            msg = bot.send_message(call.message.chat.id, "На прохождение тестов дается бесконечное количество времени и попыток, но в зачёт идет только первое прохождение теста.  ", reply_markup=keyboard)
            number_question = 0
            score = 0
            bot.register_next_step_handler(msg, test ,test_number, question_arr , answer_arr, number_question,score)
    if call.data == 'phone':
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
        key1 = types.InlineKeyboardButton("Часть 1", callback_data='metoda1', url="https://drive.google.com/drive/folders/1ddxdq0ubhu0YZ8v-skzF0sYny1NygM1e?usp=sharing")
        key2 = types.InlineKeyboardButton("Тест 1", callback_data='test5')
        key3 = types.InlineKeyboardButton("Часть 2", callback_data='metoda2', url="https://drive.google.com/drive/folders/11oN_GBF8ExWwOjMo1_itJZ0tVQCWDcCg?usp=sharing")
        key4 = types.InlineKeyboardButton("Тест 2", callback_data='test6')
        key5 = types.InlineKeyboardButton("Часть 3", callback_data='metoda3', url="https://drive.google.com/drive/folders/1xAsdkP3oV5HSrFhXy9uRObuPVqPj-a8L?usp=sharing")
        key6 = types.InlineKeyboardButton("Тест 3", callback_data='test7')
        key7 = types.InlineKeyboardButton("Часть 4", callback_data='metoda4', url="https://drive.google.com/drive/folders/117n-ogdgf3_2ebVPh3lwT9Vx2lR5-wFZ?usp=sharing")
        key8 = types.InlineKeyboardButton("Тест 4", callback_data='test8')
        key9 = types.InlineKeyboardButton("Часть 5", callback_data='metoda1', url="https://drive.google.com/drive/folders/1PcB62rcoaI9HUYS6jFX6IpNkbvid0zE4?usp=sharing")
        key10 = types.InlineKeyboardButton("Тест 5", callback_data='test9')
        key11 = types.InlineKeyboardButton("Часть 6", callback_data='metoda2', url="https://drive.google.com/drive/folders/17lTkORYkkU8NOUsjrvT_TG4fkAOqHEjq?usp=sharing")
        key12 = types.InlineKeyboardButton("Тест 6", callback_data='test10')
        key13 = types.InlineKeyboardButton("Часть 7", callback_data='metoda3', url="https://drive.google.com/drive/folders/1qSxK1gcpHR2DZeqkG1zvgoJMGzze4u98?usp=sharing")
        key14 = types.InlineKeyboardButton("Тест 7", callback_data='test11')
        key15 = types.InlineKeyboardButton("Часть 8", callback_data='metoda4', url="https://drive.google.com/drive/folders/1fBzSM51okuvkv4LFEnaPdLQvaJ6Hfh67?usp=sharing")
        key16 = types.InlineKeyboardButton("Тест 8", callback_data='test12')
        key17 = types.InlineKeyboardButton("Часть 9", callback_data='metoda1', url="https://drive.google.com/drive/folders/1ytZKhyGNIPhw8nyBiOWP1WOBufZWlcnU?usp=sharing")
        key18 = types.InlineKeyboardButton("Тест 9", callback_data='test13')
        key19 = types.InlineKeyboardButton("Часть 10", callback_data='metoda2', url="https://drive.google.com/drive/folders/1h7G0F0Nt13TS--lZ7oeIgGcKEJKjLe2b?usp=sharing")
        key20 = types.InlineKeyboardButton("Тест 10", callback_data='test14')
        key21 = types.InlineKeyboardButton("Часть 11", callback_data='metoda3', url="https://drive.google.com/drive/folders/1wppuUeQHgroWFsVt-4kaePeXdwaQCbE-?usp=sharing")
        key22 = types.InlineKeyboardButton("Тест 11", callback_data='test15')
        key23 = types.InlineKeyboardButton("Часть 12", callback_data='metoda4', url="https://drive.google.com/drive/folders/1PzIEUhtzVhiTIYOu53JoPgMQzYQjfiOj?usp=sharing")
        key24 = types.InlineKeyboardButton("Тест 12", callback_data='test16')
        key25 = types.InlineKeyboardButton("Часть 13", callback_data='metoda4', url="https://drive.google.com/drive/folders/1ss18g9-LvFVJPHbKib251hsazJ_V9_U2?usp=sharing")
        key26 = types.InlineKeyboardButton("Тест 13", callback_data='test17')
        markup.add(key1, key2, key3, key4, key5, key6, key7, key8, key9, key10,key11,key12,key13,key14,key15,key16,key17,key18,key19,key20,key21,key22,key23,key24,key25,key26)
        bot.send_message(call.message.chat.id, 'Выберите тест для прохождения: ', reply_markup=markup)
        #bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Тест выбран')
        #bot.register_next_step_handler(msg, test)
    elif call.data == 'testStudent':
        bot.send_message(call.message.chat.id, 'В скором времени будут добавлены тесты для студента')
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
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3);
        keyboard.add(types.KeyboardButton("Обновить"))
        message = bot.send_message(call.message.chat.id, 'Для обновления ваших результатов нажмите кнопку ниже', reply_markup = keyboard)
        bot.register_next_step_handler(message, result)
        #'Курс: Бережливое производство\n Номер теста: \n 1: 9/10 \n 2: \n 3: \n Проходной балл: 100 \n Ваш балл: 9 ')

@bot.message_handler(content_types=['text'])
def lalala(message):
     if message.chat.type == 'private':
        if message.text == '❓ Тест':
            markup = types.InlineKeyboardMarkup(row_width=2)
            keyWorker = types.InlineKeyboardButton("👷‍♂️ Сотруднки КОМПО", callback_data='worker')
            keyStudend = types.InlineKeyboardButton("👨‍🎓 Студенты ", callback_data='student')
            keyResult = types.InlineKeyboardButton("😱 Результаты ", callback_data='result')
            markup.add(keyWorker, keyStudend,keyResult)
            bot.send_message(message.chat.id, 'Если Вы являетесь сотрудником Компо, то выберите соответствующую кнопку. Если Вы только начинаете обучение, то выберите кнопку студент:', reply_markup=markup)
        elif message.text == '⚙️ Настройки':
            markup = types.InlineKeyboardMarkup(row_width=1)
            keyTechHelp = types.InlineKeyboardButton("🆘 Тех. поддержка", callback_data='techHelp', url ="https://t.me/Ros_Mic")
            markup.add(keyTechHelp)
            bot.send_message(message.chat.id, 'В настройках Вы можете изменить своё имя написав в тех. поддержку', reply_markup=markup)
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
            bot.send_message(message.chat.id, 'Здесь Вы можете связаться с нами:', reply_markup=markup)

        elif message.text == '/Update_Result':
            connect = sqlite3.connect('KompoDB.db')
            cursor = connect.cursor()
            bot.send_message(message.chat.id, 'Таблица результатов обновленна, переведите в базу данных для скачавания')
            cursor.executescript("""delete from total_result;
                            INSERT INTO total_result
                            select u.id as user_id,user_name, user_secondName,
                            result_test1.score as result_test1,
                            result_test2.score as result_test2,
                            result_test3.score as result_test3,
                            result_test4.score as result_test4,
                            result_test5.score as result_test5,
                            result_test6.score as result_test6,
                            result_test7.score as result_test7,
                            result_test8.score as result_test8,
                            result_test9.score as result_test9,
                            result_test10.score as result_test10,
                            result_test11.score as result_test11,
                            result_test12.score as result_test12,
                            result_test13.score as result_test13,
                            result_test14.score as result_test14,
                            result_test15.score as result_test15,
                            result_test16.score as result_test16,
                            result_test17.score as result_test17,
                            total_resultOffice.Total_Score as Total_ScoreOffice,
                            total_resultMP.Total_Score as Total_ScoreMP,
                            (total_resultOffice.Total_Score * 100 / 40)||'%' as ProgressOffice,
                            (total_resultMP.Total_Score * 100 / 130)||'%' as ProgressMP,
                            total_resultOffice.test_completed as TestCompletedOffice,
                            total_resultMP.test_completed as TestCompletedMP,
                            iif(total_resultOffice.test_completed=4, 1,0) as CompletedOfiiceCourse,
                            iif(total_resultMP.test_completed=13, 1,0) as CompletedMPCourse,
                            iif(total_resultOffice.Total_Score=40, 'Yes','NO') as CompletedOfiiceCourseSuccessfull,
                            iif(total_resultMP.Total_Score=130, 'Yes','NO') as CompletedMPCourseSuccessfull
                            from users u
                            left JOIN users_result result_test1
                            on u.id=result_test1.user_id
                            and result_test1.test_number = 1
                            left JOIN users_result result_test2
                            on u.id=result_test2.user_id
                            and result_test2.test_number = 2
                            left JOIN users_result result_test3
                            on u.id=result_test3.user_id
                            and result_test3.test_number = 3
                            left JOIN users_result result_test4
                            on u.id=result_test4.user_id
                            and result_test4.test_number = 4
                            left JOIN users_result result_test5
                            on u.id=result_test5.user_id
                            and result_test5.test_number = 5
                            left JOIN users_result result_test6
                            on u.id=result_test6.user_id
                            and result_test6.test_number = 6
                            left JOIN users_result result_test7
                            on u.id=result_test7.user_id
                            and result_test7.test_number = 7
                            left JOIN users_result result_test8
                            on u.id=result_test8.user_id
                            and result_test8.test_number = 8
                            left JOIN users_result result_test9
                            on u.id=result_test9.user_id
                            and result_test9.test_number = 9
                            left JOIN users_result result_test10
                            on u.id=result_test10.user_id
                            and result_test10.test_number = 10
                            left JOIN users_result result_test11
                            on u.id=result_test11.user_id
                            and result_test11.test_number = 11
                            left JOIN users_result result_test12
                            on u.id=result_test12.user_id
                            and result_test12.test_number = 12
                            left JOIN users_result result_test13
                            on u.id=result_test13.user_id
                            and result_test13.test_number = 13
                            left JOIN users_result result_test14
                            on u.id=result_test14.user_id
                            and result_test14.test_number = 14
                            left JOIN users_result result_test15
                            on u.id=result_test15.user_id
                            and result_test15.test_number = 15
                            left JOIN users_result result_test16
                            on u.id=result_test16.user_id
                            and result_test16.test_number = 16
                            left JOIN users_result result_test17
                            on u.id=result_test17.user_id
                            and result_test17.test_number = 17
                            left JOIN (
                            Select user_id, sum(score) as Total_Score,
                            sum(case when ifnull(score,0) > 0 then 1 else 0 END) as test_completed  from users_result
                            WHERE test_number<=4
                            GROUP by user_id
                            ) total_resultOffice
                            on u.id=total_resultOffice.user_id
                            left JOIN (
                            Select user_id, sum(score) as Total_Score,
                            sum(case when ifnull(score,0) > 0 then 1 else 0 END) as test_completed  from users_result
                            WHERE test_number>4 AND test_number<=17
                            GROUP by user_id
                            ) total_resultMP
                            on u.id=total_resultMP.user_id
                    """)
bot.polling(none_stop=True)
