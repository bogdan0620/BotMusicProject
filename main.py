from aiogram import Bot, Dispatcher, executor, types
import buttons
import tokens
from states import *
from tokens import TOKEN
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove
import database
import csv_file

bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=['start'])
async def cmd_start(message):
    user_id = message.from_user.id
    checker = database.cheсk_user(user_id)
    await message.answer_sticker('CAACAgIAAxkBAAIFYmRjeHZS7w1EnHLodGf22k7GXGT3AAKTLQACrFEYS3DrE5B4jXmXLwQ')
    await dp.current_state(user=user_id).update_data(username=message.from_user.full_name)
    if checker:
        all_music = database.get_all_music()
        await bot.send_message(chat_id=message.from_user.id, text='Введите для поиска', reply_markup=buttons.main_menu_kb(all_music))
    else:
        await message.answer('Привет. Это бот для скачивания музыки 🎶\nВведите ваш возраст', reply_markup=buttons.age_kb())
        await GetAge.getting_age.set()


@dp.callback_query_handler()
async def callback_list(call):
    # Сохраним айди пользователя
    user_id = call.message.chat.id
    all_music = database.get_all_music()
    users = {1097387511: {'pr_count': 1}}
    # Если пользователь нажал на +
    # print(call.data)
    if call.data == 'next':
        actual_count = users[user_id]['pr_count']
        print(actual_count)

        users[user_id]['pr_count'] += 1
        print(actual_count)

        # Меняем значение кнопки
        await bot.edit_message_reply_markup(chat_id=user_id,
                                            message_id=call.message.message_id,
                                            reply_markup=buttons.main_menu_kb(all_music, 'next', users[user_id]['pr_count']))

    # decrement
    # Если пользователь нажал на -
    elif call.data == 'back':
        actual_count = users[user_id]['pr_count']
        print(actual_count)

        users[user_id]['pr_count'] -= 0
        print(actual_count)

        # Меняем значение кнопки
        await bot.edit_message_reply_markup(chat_id=user_id,
                                            message_id=call.message.message_id,
                                            reply_markup=buttons.main_menu_kb(all_music, 'back', users[user_id]['pr_count']))

    # back
    # Если пользователь нажал 'назад'
    # elif call.data == 'back':
    #     # Получаем меню
    #     products = database.get_pr_name_id()
    #     # меняем на меню
    #     await bot.edit_message_text('Выберите пункт меню',
    #                                 user_id,
    #                                 call.message.message_id,
    #                                 reply_markup=buttons.main_menu_kb(products))

    await bot.answer_callback_query(call.id, f'Номер трека: {call.data}')
    music = database.get_music_num(call.data)
    if music:
        for i in music:
            result1 = f'{i[1]}'
            result2 = f'{i[0]}. {i[3]} – {i[2]}'
        await bot.send_audio(call.from_user.id, audio=result1, caption=result2)

    await bot.answer_callback_query(call.id)


@dp.message_handler(state=GetAge.getting_age, content_types=['text'])
async def age_user(message, state=GetAge.getting_age):
    user_answer = message.text
    users_ages = [str(i) for i in range(10, 81)]

    if user_answer == "Зачем нужен возраст?":
        await message.answer('Возраст нужен для наилучшей персонализации музыки под определенный возраст (скоро)\n'
                             'Введите возраст', reply_markup=ReplyKeyboardRemove())

    elif user_answer in users_ages:
        age = message.text
        tg_id = message.from_user.id
        name = message.from_user.full_name
        database.add_user(tg_id, name, age)
        await message.answer('Введите для поиска', reply_markup=buttons.menu_kb())
        await state.finish()

    else:
        await message.answer('Введите корректный возраст\n(Ограничение от 10 до 80)')


@dp.message_handler(commands=['catalog'])
async def cmd_catalog(message):
    if message.from_user.id in tokens.TG:
        csv_file.get_csv_file()
        await message.answer_document(open('Catalog.csv', 'rb'))
        await message.answer('Введите для поиска', reply_markup=buttons.admin_kb())

    else:
        csv_file.get_csv_file()
        await message.answer_document(open('Catalog.csv', 'rb'))
        await message.answer('Введите для поиска', reply_markup=buttons.admin_kb())


@dp.message_handler(commands=['admin'])
async def cmd_admin(message):
    if message.from_user.id in tokens.TG:
        await message.answer('Вы вошли как администратор 🔓\nВведите для поиска', reply_markup=buttons.admin_kb())
    else:
        await message.answer('Вы не являетесь администратором 🔒\nВведите для поиска', reply_markup=buttons.menu_kb())


@dp.message_handler(lambda message: message.text == 'Добавить музыку 📨')
async def add_music(message):
    if message.from_user.id in tokens.TG:
        await message.answer('Отправьте файл музыки 💿', reply_markup=buttons.back_kb())
        await Music_admin.getting_file_music.set()
    else:
        await message.answer('Вы не являетесь администратором 🔒\nВведите для поиска', reply_markup=buttons.menu_kb())


@dp.message_handler(content_types=['audio', 'text'], state=Music_admin.getting_file_music)
async def add_file_music(message, state=Music_admin.getting_file_music):
    if message.text == '◀️ Назад':
        await message.answer('Введите для поиска', reply_markup=buttons.admin_kb())
        await state.finish()
        return
    user_file = message.audio.file_id
    print(user_file)
    await state.update_data(file_id=user_file)
    await message.answer('Введите название 📝', reply_markup=buttons.back_kb())
    await Music_admin.getting_name_music.set()


@dp.message_handler(content_types=['text'], state=Music_admin.getting_name_music)
async def add_name_music(message, state=Music_admin.getting_name_music):
    if message.text == '◀️ Назад':
        await message.answer('Отправьте файл музыки 💿', reply_markup=buttons.back_kb())
        await Music_admin.getting_file_music.set()
        return
    name_file = message.text
    await state.update_data(name=name_file)
    await message.answer('Введите исполнителя 📝', reply_markup=buttons.back_kb())
    await Music_admin.getting_singer_music.set()


@dp.message_handler(content_types=['text'], state=Music_admin.getting_singer_music)
async def add_singer_music(message, state=Music_admin.getting_singer_music):
    if message.text == '◀️ Назад':
        await message.answer('Введите название 📝', reply_markup=buttons.back_kb())
        await Music_admin.getting_name_music.set()
        return
    singer_file = message.text
    all_info = await state.get_data()
    tg_file_id = all_info.get('file_id')
    name = all_info.get('name')
    singer = singer_file
    database.add_music(tg_file_id, name, singer)
    await message.answer('Трек успешно добавлен в базу ✅')
    await state.finish()
    await message.answer('Выберите действие ⬇️', reply_markup=buttons.admin_kb())


@dp.message_handler(lambda message: message.text == 'Список пользователей')
async def list_users(message):
    if message.from_user.id in tokens.TG:
        csv_file.get_csv_users()
        await message.answer_document(open('users.csv', 'rb'))

    else:
        await message.answer('Вы не являетесь администратором 🔒т\nВведите для поиска', reply_markup=buttons.menu_kb())


@dp.message_handler(lambda message: message.text == 'Список возрастов пользователей')
async def list_users_age(message):
    if message.from_user.id in tokens.TG:
        user = database.get_users()
        if user:
            users = ''
            for i in user:
                users += f'{i[0]}. Возраст: {i[3]}\n'
            await message.answer(users, reply_markup=buttons.admin_kb())
        else:
            await message.answer('База пуста 📂', reply_markup=buttons.admin_kb())
    else:
        await message.answer('Вы не являетесь администратором 🔒т\nВведите для поиска', reply_markup=buttons.menu_kb())


@dp.message_handler(lambda message: message.text == 'Как искать?')
async def how_to_search(message):
    await message.answer('Для поиска введите название трека или имя исполнителя, также поиск работает по порядковому номеру трека\n'
                         'Узнать порядковый номер трека можно из каталога /catalog', reply_markup=buttons.menu_kb())


@dp.message_handler(content_types=['text'])
async def search_out(message):
    user = database.get_all_music()
    for i in user:
        l = i[0]
    num_music = [str(i) for i in range(1, l)]
    if message.text in num_music:
        m = int(message.text)
        user = database.get_music_num(m)
        if user:
            result1 = '⤵️ Вот что есть в базе:\n\n'
            for i in user:
                result1 += f'{i[0]}. Название: {i[2]}\nИсполнитель: {i[3]}\n'
                result2 = f'{i[1]}'
            await message.answer_audio(result2)
            await message.answer(result1, reply_markup=buttons.menu_kb())
        else:
            await message.answer('Ничего не найдено 📂', reply_markup=buttons.menu_kb())

    else:
        m = message.text
        user = database.get_music_name(m)
        if user:
            result1 = '⤵️ Вот что еще есть в базе:\n\n'
            for i in user:
                result1 += f'{i[0]}. Название: {i[2]}\nИсполнитель: {i[3]}\n'
                result2 = f'{i[1]}'
            await message.answer_audio(result2)
            await message.answer(result1, reply_markup=buttons.menu_kb())

        else:
            user = database.get_music_singer(m)
            if user:
                result1 = '⤵️ Вот что еще есть в базе:\n\n'
                for i in user:
                    result1 += f'{i[0]}. Название: {i[2]}\nИсполнитель: {i[3]}\n'
                    result2 = f'{i[1]}'
                await message.answer_audio(result2)
                await message.answer(result1, reply_markup=buttons.menu_kb())

            else:
                await message.answer('Ничего не найдено 📂', reply_markup=buttons.menu_kb())


@dp.message_handler()
async def answer_not(message):
    await message.answer('Введите для поиска', reply_markup=buttons.menu_kb())\


@dp.message_handler(content_types=types.ContentType.ANY)
async def unknown_message(message):
    await message.answer('Введите для поиска', reply_markup=buttons.menu_kb())



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
