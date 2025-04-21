from enum import Enum, auto
from typing import Union


class Suit(Enum):
    Diamonds = auto()
    Hearts = auto()
    Clubs = auto()
    Spades = auto()
    Joker = auto()


class Card:
    suit: Suit
    rank: Union[str, int]

    # X = Joker
    rank_val_dict = {'10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 1, 'X': 0}
    suit_symbols = {
        Suit.Diamonds: '♦',
        Suit.Hearts: '♥',
        Suit.Clubs: '♣',
        Suit.Spades: '♠',
    }

    def __init__(self, suit: Suit, rank: Union[str, int]):
        self.suit = suit
        self.rank = rank

    def value(self) -> int:
        if self.rank in self.rank_val_dict:
            return self.rank_val_dict[self.rank]

        return int(self.rank)

    def __str__(self) -> str:
        if self.suit is not Suit.Joker:
            return f'{self.rank} of {self.suit_symbols[self.suit]}'
        return '🤡🃏'

    def __repr__(self):
        return self.__str__()