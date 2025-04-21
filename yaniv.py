import random

from Player import Player
from card import Card, Suit



def play():
    deck = []
    trash = []
    num_ai_players = 3
    players_list = []

    rank_list = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K', 'A']
    for rank in rank_list:
        for suit in [Suit.Diamonds, Suit.Hearts, Suit.Clubs, Suit.Spades]:
            deck.append(Card(suit, str(rank)))

    deck.append(Card(Suit.Joker, 'X'))

    random.shuffle(deck)

    user = Player('Player Name')
    players_list.append(user)
    for i in range(num_ai_players):
        players_list.append(Player(f'AI {i + 1}'))

    for i in range(5):
        for p in players_list:
            p.pickup_card(deck.pop())

    trash.append(deck.pop())

    for p in players_list:
        print(p, '\n')

    print('Top Card: ', trash[-1])


if __name__ == '__main__':
    play()