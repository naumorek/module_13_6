'''
Задача "Ещё больше выбора":
Необходимо дополнить код предыдущей задачи, чтобы при нажатии на кнопку 'Рассчитать' присылалась Inline-клавиатруа.
Создайте клавиатуру InlineKeyboardMarkup с 2 кнопками InlineKeyboardButton:
С текстом 'Рассчитать норму калорий' и callback_data='calories'
С текстом 'Формулы расчёта' и callback_data='formulas'
Создайте новую функцию main_menu(message), которая:
Будет обёрнута в декоратор message_handler, срабатывающий при передаче текста 'Рассчитать'.
Сама функция будет присылать ранее созданное Inline меню и текст 'Выберите опцию:'
Создайте новую функцию get_formulas(call), которая:
Будет обёрнута в декоратор callback_query_handler, который будет реагировать на текст 'formulas'.
Будет присылать сообщение с формулой Миффлина-Сан Жеора.
Измените функцию set_age и декоратор для неё:
Декоратор смените на callback_query_handler, который будет реагировать на текст 'calories'.
Теперь функция принимает не message, а call. Доступ к сообщению будет следующим - call.message.
По итогу получится следующий алгоритм:
Вводится команда /start
На эту команду присылается обычное меню: 'Рассчитать' и 'Информация'.
В ответ на кнопку 'Рассчитать' присылается Inline меню: 'Рассчитать норму калорий' и 'Формулы расчёта'
По Inline кнопке 'Формулы расчёта' присылается сообщение с формулой.
По Inline кнопке 'Рассчитать норму калорий' начинает работать машина состояний по цепочке.

Примечания:
При отправке вашего кода на GitHub не забудьте убрать ключ для подключения к вашему боту!
'''


from aiogram import Bot,Dispatcher,executor,types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardMarkup,InlineKeyboardButton
import asyncio


api="7706788533:"
bot=Bot(token=api)
dp=Dispatcher(bot,storage=MemoryStorage())
kb1=ReplyKeyboardMarkup() #главное меню
kb2=InlineKeyboardMarkup() #выбор расчет калорий или вывод формулы



button_1=KeyboardButton(text="Расчитать")
button_2=KeyboardButton(text="info")

kb1.add(button_1)
kb1.add(button_2)

il_button_1=InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
il_button_2=InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')

kb2.row(il_button_1)
kb2.row(il_button_2)

class UserState(StatesGroup):
    growth=State()
    weight=State()
    age=State()
@dp.message_handler(commands= ["start"])
async def main_start(message):
    await message.answer('Привет! \nВыберите опцию:', reply_markup=kb1)

@dp.message_handler(text="Расчитать")
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kb2)

@dp.message_handler(text= "info")
async def get_info(message):
    await message.answer('Этот бот считает каллории для мужчин, со средней физической активностью')

@dp.callback_query_handler(text= "calories")
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    call.answer()
    await UserState.age.set()               #ждем передачи сообщения от пользователя -> Состояние age

@dp.message_handler(state=UserState.age) #как только прило сообщение, происходит событие  UserState.age
async def set_growth(message,state):

        try:
            a=float(message.text)
            await state.update_data(age=message.text)   #записываем в дата с ключом age значение age

            await message.answer('Введите свой рост:')
            await UserState.growth.set()
        except Exception:
            await message.answer('неверный формат возраста')
            await message.answer('Введите свой возраст еще раз:')
            await UserState.age.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message,state):
    try:
        a = float(message.text)
        await state.update_data(growth=message.text)
        await message.answer('Введите свой вес')
        await UserState.weight.set()
    except Exception:
        await message.answer('неверный формат роста')
        await message.answer('Введите свой рост еще раз:')
        await UserState.growth.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    try:
        a = float(message.text)
        await state.update_data(weight=message.text)
        data = await state.get_data()   # получаем dat'у из записанных значений
        k_call=(10*float(data['weight'])+6.25*float(data['growth'])-5*float(data['age'])+5)*1.55
        await message.answer(f'Ваша норма каллорий: {k_call}')
        await state.finish()  #завершаем состояние
    except Exception:
        await message.answer('неверный формат веса')
        await message.answer('Введите свой вес еще раз:')
        await UserState.weight.set()


@dp.callback_query_handler(text= 'formulas')
async def get_formulas(call):
    await call.message.answer('call=10*weight(kg)+6.25*growth(cm)-5*age(y)+5)*1.55')
    await call.answer()



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
