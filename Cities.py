import pymysql.cursors
import logging
from aiogram import Bot, Dispatcher, executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.markdown import hlink, hbold
import urllib

def getGmapsUrl(city):
    name = 'Россия, ' + city['name']
    return urllib.parse.quote('www.google.com/maps/place/' + name)


def querydb(sql, params = []):
    connection = pymysql.connect(
        host='Kinwu.mysql.pythonanywhere-services.com',
        user='Kinwu',
        password='CAr-u9W-eVF-vG3',
        db='Kinwu$Cities',
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
    );

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            connection.commit()
            return cursor.fetchall()


def queryCityByLetter(letter, used):
    used = used.get(letter, [])

    # все параметры экранируются, чтобы защититься от sql-инъекций
    if (len(used)):
        format_strings = ','.join(['%s'] * len(used))
        params = tuple([letter + '%'] + used)
        list = querydb("SELECT id, name FROM db_locality WHERE name like %s AND level = 3 AND peoples > 20000 AND id NOT IN(%s) ORDER BY rand() LIMIT 1" % ('%s', format_strings), params)
    else:
        list = querydb("SELECT id, name FROM db_locality WHERE name like %s AND peoples > 20000 AND level = 3 ORDER BY rand() LIMIT 1", (letter + '%'))

    if len(list) > 0:
        return list[0]
    return None

def queryCityByName(name):
    res = querydb('SELECT id, name FROM db_locality WHERE level = 3 AND name = %s', (name));
    if len(res) == 0:
        return None

    return res[0]

def cityGetLastLetter(name):
    skipLetters = ('ь','ъ','ы','й','ц')
    for i in range(len(name)-1, 0, -1):
        if name[i] not in skipLetters:
            return name[i]

    return None

def queryLeaders():
    res = querydb('SELECT * FROM leaders ORDER BY score DESC LIMIT 10');
    return res

def saveUserScore(userData, score):
    res = querydb('SELECT * FROM leaders WHERE tg_id = %s LIMIT 1', (userData.id));

    newOwnRecord = False
    if len(res):
        if score > res[0]['score']:
            newOwnRecord = True;
            querydb('UPDATE leaders SET score = %s WHERE tg_id = %s', (score, userData.id))
    else:
        querydb('INSERT INTO leaders(tg_id, nickname, score) VALUES(%s, %s, %s)', (userData.id, userData.username or 'unnamed', score))

    return newOwnRecord



def saveIdInUsed(city, used):
    firstLetter = city['name'][0].upper()
    if firstLetter not in used:
        used[firstLetter] = []

    used[firstLetter].append(city['id'])

def checkCityAlreadyUsed(city, used):
    firstLetter = city['name'][0].upper()
    if firstLetter in used and city['id'] in used[firstLetter]:
        return True

    return False





#BOT

bot = Bot(token='6280639823:AAGvxgzd8uBskhV0RZ_rFaY6kUQa_JVz3Ec', proxy="http://proxy.server:3128")
logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
cb = CallbackData('filter', 'action')


# https://docs.aiogram.dev/en/latest/examples/finite_state_machine_example.html

@dp.message_handler(commands=['start', 'help'])
async def hello(message):
    keyboard = InlineKeyboardMarkup()
    buttons = [InlineKeyboardButton(text = 'Играть', callback_data=cb.new(action='play')),
              InlineKeyboardButton(text = 'Правила', callback_data=cb.new(action='rules')),
              InlineKeyboardButton(text = 'Лидеры', callback_data=cb.new(action='leaders'))]
    keyboard.add(*buttons)
    await message.answer('Приветствую!')
    await message.answer('Этот бот создан для игры в "Города".')
    await message.answer('Выберите интерисующую вас кнопку!', reply_markup=keyboard)


@dp.callback_query_handler(cb.filter())
async def do_button(call, callback_data, state):
    match callback_data['action']:

        case 'play':
            await call.message.answer('Начинаем!')
            await call.message.answer('Назовите город.')

        case 'rules':
            keyboard = InlineKeyboardMarkup()
            buttons = [InlineKeyboardButton(text = 'Играть', callback_data=cb.new(action='play'))]
            keyboard.add(*buttons)
            await call.message.answer('Правила игры простые.\nВы называете город, бот отвечая,\nназывает город начинающийся на последнюю букву\nназваного вами города(исключая ь, ъ , ы , й , ц , ё)\nВы называете город на последнюю букву города бота и так далее.' )
            await call.message.answer('Готовы попробовать?', reply_markup=keyboard)

        case 'leaders':
            leaders = queryLeaders()
            answer = 'Лидеры\n\n'

            states = ['🥇','🥈','🥉','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟']

            for index, leader in enumerate(leaders):

                if str(call.from_user.id) == leader['tg_id']:
                    nick = hbold(leader['nickname'])
                else:
                    nick = hlink(leader['nickname'], 'tg://user?id=' + str(leader['tg_id']))

                answer += '%s %s - %s\n' % (states[index], leader['score'], nick)

            await call.message.answer(answer, parse_mode="HTML")

        case 'stop':
            userData = await state.get_data()

            keyboard = InlineKeyboardMarkup()
            buttons = [InlineKeyboardButton(text = 'Лидеры', callback_data=cb.new(action='leaders'))]
            keyboard.add(*buttons)

            score = userData.get('score', 0);
            await call.message.answer('Ваш счет: ' + str(score))

            newOwnRecord = saveUserScore(call.from_user, score);

            if newOwnRecord:
                await call.message.answer('🥂 Вы побили свой прошлый рекорд!')

            await call.message.answer('Еще раз?\nПросто введите город', reply_markup=keyboard)


            await state.update_data({
                "score": 0,
                "nextLetter": None,
                "used": {}
            })



@dp.message_handler()
async def choose_city(message, state):

    keyboard = InlineKeyboardMarkup()
    buttons = [InlineKeyboardButton(text = 'Стоп', callback_data=cb.new(action='stop'))]
    keyboard.add(*buttons)

    userData = await state.get_data()

    needLetter = userData.get('nextLetter', None)
    used = userData.get('used', {})

    if needLetter != None and message.text[0].upper() != needLetter:
        await message.answer('Не принимается\nГород должен начинаться с буквы ' + needLetter)
        return

    playerCity = queryCityByName(message.text);


    if playerCity == None:
        await message.answer('Такого города в России нет!')
        return

    lastLetter = cityGetLastLetter(playerCity['name']).upper()

    if checkCityAlreadyUsed(playerCity, used):
        await message.answer('Этот город уже называли!')
        return


    botCity = queryCityByLetter(lastLetter, used)

    if botCity == None:
        await message.answer('Я проиграл!')
        return

    nextLetter = cityGetLastLetter(botCity['name']).upper();
    saveIdInUsed(playerCity, used)
    saveIdInUsed(botCity, used)


    linkedName = hlink(botCity['name'], getGmapsUrl(botCity))
    await message.answer("Я выбираю "+ linkedName, parse_mode='HTML')
    await message.answer("Вам на "+ nextLetter, reply_markup=keyboard)

    await state.update_data({
        "nextLetter": nextLetter,
        "used": used,
        "score": userData.get('score', 0) + 1
    })



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
