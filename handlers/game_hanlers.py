import random

from aiogram import types, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from aiogram.types import ReplyKeyboardRemove
from keybords.keyboards_for_game import keyboards_game, ikb
from B_J.game_21 import START_TEXT, LIST_CARDS, get_card, calculation, check_bot


router = Router()


class GameState(StatesGroup):
    start_state = State()
    game_state = State()


@router.message(Command('start'))
async def start_cmd(message: types.Message):
    await message.answer('Для старта игры /game')


@router.message(StateFilter(None), Command('game'))
async def game_cmd(message: types.Message, state: FSMContext):
    await message.answer(START_TEXT, reply_markup=keyboards_game(["Играем", "Отмена"]))
    await state.set_state(GameState.start_state)
    # Добавляем в хранилище количество побед
    await state.update_data(wins_comp=0)
    await state.update_data(wins_player=0)
    await message.bot.delete_message(message.from_user.id, message_id=message.message_id)


@router.message(GameState.start_state, F.text.lower() == "играем")
async def start_game(message: types.Message, state: FSMContext):
    # Создаем колоду и перемешиваем
    list_cards = LIST_CARDS.copy()
    random.shuffle(list_cards)
    data_check = await state.get_data()
    # Проверяем или была игра и чистим чат если была
    if 'deck' in data_check:
        await message.bot.delete_messages(message.from_user.id, message_ids=[message.message_id-1, message.message_id-2])

    # Даем в руку по две карты для пользователя и компьютера
    hand_player = f"{get_card(list_cards)} {get_card(list_cards)}"
    hand_comp = f"{get_card(list_cards)} {get_card(list_cards)}"
    # Рассчитываем количество очков в руках и проверяем условия
    points_player = calculation(hand_player)
    points_comp = calculation(hand_comp)
    await state.update_data(deck=list_cards)
    if points_player > 21 and points_comp > 21:
        await message.answer(f'Вам не повезло, у вас и у компьютера сразу же перебор \nВаша рука: {hand_player} - ({points_player}) \nКомпьютера: {hand_comp} - ({points_comp})',
                             reply_markup=keyboards_game(["Играем", "Отмена"]))
    elif points_comp > 21:
        await message.answer(f'Противнику не повезло у него сразу же перебор \nВаша рука: {hand_player} - ({points_player}) \nКомпьютера: {hand_comp} - ({points_comp})', reply_markup=keyboards_game(["Играем", "Отмена"]))
        wins = ((await state.get_data())['wins_player']) + 1
        await state.update_data(wins_player=wins)
    elif points_player > 21:
        await message.answer(f'Вам не повезло, у вас сразу же перебор \nВаша рука: {hand_player} - ({points_player}) \nКомпьютера: {hand_comp} - ({points_comp})', reply_markup=keyboards_game(["Играем", "Отмена"]))
        wins = ((await state.get_data())['wins_comp']) + 1
        await state.update_data(wins_comp=wins)
    elif points_comp == 21 and points_player == 21:
        await message.answer(f'У вас с компьютером ничья, выпало сразу же по 21 \nВаша рука: {hand_player} - ({points_player}) \nКомпьютера: {hand_comp} - ({points_comp})', reply_markup=keyboards_game([
            "Играем", "Отмена"]))
    elif points_comp == 21:
        await message.answer(f'Победил компьютер, ему повезло и сразу же выпало 21 \nВаша рука: {hand_player} - ({points_player}) \nКомпьютера: {hand_comp} - ({points_comp})', reply_markup=keyboards_game([
            "Играем", "Отмена"]))
        wins = ((await state.get_data())['wins_comp']) + 1
        await state.update_data(wins_comp=wins)
    elif points_player == 21:
        await message.answer(f'Вы победили, вам повезло и сразу же выпало 21 \nВаша рука: {hand_player} - ({points_player}) \nКомпьютера: {hand_comp} - ({points_comp})', reply_markup=keyboards_game(["Играем", "Отмена"]))
        wins = ((await state.get_data())['wins_player']) + 1
        await state.update_data(wins_player=wins)
    else:
        # добавляем в хранилище полученные данные
        await state.update_data(points_comp=points_comp)
        await state.update_data(points_player=points_player)
        await state.update_data(hand_comp=hand_comp)
        await state.update_data(hand_player=hand_player)
        await message.bot.delete_messages(message.from_user.id, message_ids=[message.message_id])
        # Выводим руку человека и его очки
        await message.answer(f"В вашей руке {hand_player} - {points_player} очков", reply_markup=ikb(['Взять', 'Хватит'], ['+', '-']))
        await state.set_state(GameState.game_state)


@router.callback_query(GameState.game_state, (F.data == "+") | (F.data == '-'))
async def game(callback: types.CallbackQuery, state: FSMContext):
    this_game = await state.get_data()
    points_comp = this_game['points_comp']
    points_player = this_game['points_player']
    hand_comp = this_game['hand_comp']
    hand_player = this_game['hand_player']
    deck = this_game['deck']
    # Если человек хочет добавляем ему карту и рассчитываем
    if callback.data == '+':
        hand_player += f" {get_card(deck)}"
        points_player = calculation(hand_player)
        await callback.message.edit_text(f'Ваша рука - {hand_player} - {str(points_player)} ',
                                         reply_markup=ikb(['Взять', 'Хватит'], ['+', '-']))
        await state.update_data(hand_player=hand_player)
        await state.update_data(points_player=points_player)
        if points_player == 21:
            await callback.message.edit_text(f'Вы победили \nВаша рука: {hand_player}  - ({points_player}) \nКомпьютера: {hand_comp} - ({points_comp})')
            wins = ((await state.get_data())['wins_player']) + 1
            await state.update_data(wins_player=wins)
            await callback.message.answer(f'Ещё одну?', reply_markup=keyboards_game(["Играем", "Отмена"]))
            await state.set_state(GameState.start_state)
            return
        elif points_player > 21:
            #--------------
            await callback.message.edit_text(f'Вы проиграли у вас перебор \nВаша рука: {hand_player} - ({points_player}) \nКомпьютера: {hand_comp} - ({points_comp})')
            wins = ((await state.get_data())['wins_comp']) + 1
            await state.update_data(wins_comp=wins)
            await callback.message.answer(f'Ещё одну?', reply_markup=keyboards_game(["Играем", "Отмена"]))
            await state.set_state(GameState.start_state)
            return
        # Проверяем или нужно боту ещё взять карту и проверям его
        hand_comp, points_comp = check_bot(17, deck, hand_comp)
        if points_comp == 21:
            await callback.message.edit_text(f'Победил компьютер, ему  выпало 21 \nВаша рука: {hand_player} - ({points_player}) \nКомпьютера: {hand_comp} - ({points_comp})')
            wins = ((await state.get_data())['wins_comp']) + 1
            await state.update_data(wins_comp=wins)
            await callback.message.answer(f'Ещё одну?', reply_markup=keyboards_game(["Играем", "Отмена"]))
            await state.set_state(GameState.start_state)
        elif points_comp > 21:
            await callback.message.edit_text(f'Противнику не повезло у него перебор \nВаша рука: {hand_player} - ({points_player}) \nКомпьютера: {hand_comp} - ({points_comp})')
            wins = ((await state.get_data())['wins_player']) + 1
            await state.update_data(wins_player=wins)
            await callback.message.answer(f'Ещё одну?', reply_markup=keyboards_game(["Играем", "Отмена"]))
            await state.set_state(GameState.start_state)
    # Если человек отказывается брать карту, передаем эту возможность компьютеру, чтобы он набирал пока ему не хватит
    elif callback.data == '-':
        while points_comp <= 17:
            hand_comp, points_comp = check_bot(17, deck, hand_comp)
        # Затем проверяем все возможные варианты
        if points_player > 21 and points_comp > 21:
            await callback.message.edit_text(f'Ничья, у вас и у компьютера перебор \nВаша рука: {hand_player} - ({points_player}) \nКомпьютера: {hand_comp} - ({points_comp})')
            await callback.message.answer(f'Ещё одну?', reply_markup=keyboards_game(["Играем", "Отмена"]))
            await state.set_state(GameState.start_state)
        elif points_comp > 21:
            await callback.message.edit_text(f'Противнику не повезло у него перебор \nВаша рука: {hand_player} - ({points_player}) \nКомпьютера: {hand_comp} - ({points_comp})')
            wins = ((await state.get_data())['wins_player']) + 1
            await state.update_data(wins_player=wins)
            await callback.message.answer(f'Ещё одну?', reply_markup=keyboards_game(["Играем", "Отмена"]))
            await state.set_state(GameState.start_state)
        elif points_player > 21:
            await callback.message.edit_text(f'Вам не повезло, у вас перебор \nВаша рука: {hand_player} - ({points_player}) \nКомпьютера: {hand_comp} - ({points_comp})')
            wins = ((await state.get_data())['wins_comp']) + 1
            await state.update_data(wins_comp=wins)
            await callback.message.answer(f'Ещё одну?', reply_markup=keyboards_game(["Играем", "Отмена"]))
            await state.set_state(GameState.start_state)
        elif points_comp == 21 and points_player == 21:
            await callback.message.edit_text(f'У вас с компьютером ничья, выпало сразу же по 21 \nВаша рука: {hand_player} - ({points_player}) \nКомпьютера: {hand_comp} - ({points_comp})')
            await callback.message.answer(f'Ещё одну?', reply_markup=keyboards_game(["Играем", "Отмена"]))
            await state.set_state(GameState.start_state)
        elif points_comp == 21:
            await callback.message.edit_text(f'Победил компьютер, ему повезло и выпало 21 \nВаша рука: {hand_player} - ({points_player}) \nКомпьютера: {hand_comp} - ({points_comp})')
            wins = ((await state.get_data())['wins_comp']) + 1
            await state.update_data(wins_comp=wins)
            await callback.message.answer(f'Ещё одну?', reply_markup=keyboards_game(["Играем", "Отмена"]))
            await state.set_state(GameState.start_state)
        elif points_player == 21:
            await callback.message.edit_text(f'Вы победили, вам повезло выпало 21 \nВаша рука: {hand_player} - ({points_player}) \nКомпьютера: {hand_comp} - ({points_comp})')
            wins = ((await state.get_data())['wins_player']) + 1
            await state.update_data(wins_player=wins)
            await callback.message.answer(f'Ещё одну?', reply_markup=keyboards_game(["Играем", "Отмена"]))
            await state.set_state(GameState.start_state)
        elif points_comp < 21 and points_player < 21:
            if points_comp == points_player:
                await callback.message.edit_text(f'У вас с компом ничья \nВаша рука: {hand_player} - ({points_player}) \nКомпьютера: {hand_comp} - ({points_comp})')
                await callback.message.answer(f'Ещё одну?', reply_markup=keyboards_game(["Играем", "Отмена"]))
                await state.set_state(GameState.start_state)
            elif points_comp > points_player:
                await callback.message.edit_text(f'Вы проиграли \nВаша рука: {hand_player} - ({points_player}) \nКомпьютера: {hand_comp} - ({points_comp})')
                wins = ((await state.get_data())['wins_comp']) + 1
                await state.update_data(wins_comp=wins)
                await callback.message.answer(f'Ещё одну?', reply_markup=keyboards_game(["Играем", "Отмена"]))
                await state.set_state(GameState.start_state)
            else:
                await callback.message.edit_text(f'Вы победили \nВаша рука: {hand_player} - ({points_player}) \nКомпьютера: {hand_comp} - ({points_comp})')
                wins = ((await state.get_data())['wins_player']) + 1
                await state.update_data(wins_player=wins)
                await callback.message.answer(f'Ещё одну?', reply_markup=keyboards_game(["Играем", "Отмена"]))
                await state.set_state(GameState.start_state)



#Отмена_________________________________________________________________________________________________
@router.message(StateFilter('*'), Command('cancel'))
@router.message(StateFilter('*'), F.text.lower() == 'отмена')
async def cancel_game(message: types.Message, state: FSMContext):
    now_state = await state.get_state()
    if now_state is None:
        return
    else:
        # В случае отмены выводим статистику побед, удаляем сообщения, и очищаем хранилище
        await message.answer('Игра закончилась!', reply_markup=ReplyKeyboardRemove())
        my_wins = await state.get_data()
        await message.answer(f'Побед компьютера: {str(my_wins["wins_comp"])} \nВаши: {str(my_wins["wins_player"])}')
        await message.bot.delete_messages(message.from_user.id, message_ids=[message.message_id + 1,
                                                                             message.message_id,
                                                                             message.message_id - 1,
                                                                             message.message_id - 2,
                                                                             message.message_id - 3,
                                                                             message.message_id - 4,



                                                                             ])
        await state.clear()