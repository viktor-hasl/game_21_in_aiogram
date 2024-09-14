import random


LIST_CARDS = ['Т♣️', 'Т♠️', 'Т♥️', 'Т♦️', 'K♣️', 'K♠️', 'K♥️', 'K♦️',
             'Д♣️', 'Д♠️', 'Д♥️', 'Д♦️', 'В♣️', 'В♠️', 'В♥️', 'В♦️',
             '10♣️', '10♠️', '10♥️', '10♦️', '9♣️', '9♠️', '9♥️', '9♦️',
             '8♣️', '8♠️', '8♥️', '8♦️', '7♣️', '7♠️', '7♥️', '7♦️', '6♣️', '6♠️', '6♥️', '6♦️']

START_TEXT = "Карточная игра 'Двадцать одно', игра проходит с колодой в 36 карт, игроку на руку выдается по две карты, каждая карта"\
             " имеет свое количество очков: \n"\
              "T - 11 \n"\
              "K - 4 \n"\
              "Д - 3 \n"\
              "В - 2 \n"\
              "Числовые равны значению их номиналу\n"\
              "Нужно собрать 21 очко , и не перебрав иначе сразу будет проигрыш, побеждает тот у кого будет ближе к 21\nИграем?"


# Функции для бота _______________________________________________________________________________________________________________

# Получение карты из колоды
def get_card(list_card):
    card = random.choice(list_card)
    # Ее удаление из колоды
    list_card.remove(card)
    return card

# Расчет очков в руке
def calculation(hand):
    hand_calc = hand.strip().split(' ')
    points = 0
    for i in hand_calc:
        card_nomen = i[:-2]
        if card_nomen == "Т":
            points += 11
        elif card_nomen == "K":
            points += 4
        elif card_nomen == "Д":
            points += 3
        elif card_nomen == "В":
            points += 2
        else:
            points += int(card_nomen)

    return points

# Проверяем бота, если надо даем ещё карту
def check_bot(point: int, deck: list, hand_comp: str):
    '''

    :param point: Тут указываем какая степень риска бота, когда он ещё может брать карту
    :param deck: Передается колода данной игры
    :param hand_comp: Передаем руку компьютера для дальнейшей манипуляции с ней
    :return: Выводит руку и количество очков в ней
    '''

    if calculation(hand_comp) <= point:
        hand_comp += f" {get_card(deck)}"
    return hand_comp, calculation(hand_comp)

