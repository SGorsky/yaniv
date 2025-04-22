from typing import List

from card import Card, Suit

SUIT_ORDER = {Suit.Hearts: 1, Suit.Diamonds: 2, Suit.Clubs: 3, Suit.Spades: 4, Suit.Joker: 5}
RANK_ORDER = {'X': 0, 'A': 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 'J': 11, 'Q': 12, 'K': 13}


class Player:
    name: str
    points: List[int]
    cards: List[Card]


    def __init__(self, name: str):
        self.name = name
        self.points = []
        self.cards = []


    def pickup_card(self, new_card: Card):
        self.cards.append(new_card)
        self.cards.sort(key=lambda card: (RANK_ORDER[card.rank], SUIT_ORDER[card.suit]))


    def calc_hand_value(self) -> int:
        return sum([card.value() for card in self.cards])

    def __str__(self) -> str:
        return f'{self.name}\nHand: {self.cards}\nValue: {self.calc_hand_value()}'


    def __repr__(self):
        return self.__str__()
