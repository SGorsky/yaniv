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
    __rank_val_dict = {'10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 1, 'X1': 0, 'X2': 0}
    __suit_symbols = {
        Suit.Diamonds: '♦',
        Suit.Hearts: '♥',
        Suit.Clubs: '♣',
        Suit.Spades: '♠',
    }


    def __init__(self, suit: Suit, rank: Union[str, int]):
        self.suit = suit
        self.rank = rank


    def value(self) -> int:
        if self.rank in self.__rank_val_dict:
            return self.__rank_val_dict[self.rank]

        return int(self.rank)


    def __str__(self) -> str:
        if self.suit is not Suit.Joker:
            if self.suit in [Suit.Hearts, Suit.Diamonds]:
                return f'\033[91m{self.rank}{self.__suit_symbols[self.suit]}\033[0m'  # Red
            return f'{self.rank}{self.__suit_symbols[self.suit]}'
        return '🤡🃏'


    def __eq__(self, __value):
        if isinstance(__value, Card):
            return __value.suit == self.suit and __value.rank == self.rank
        return False


    def __hash__(self):
        return hash((self.rank, self.suit))


    def __repr__(self):
        return self.__str__()
