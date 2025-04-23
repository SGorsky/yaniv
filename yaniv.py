import random
from enum import auto, Enum
from typing import List, Set

from computer import Computer
from player import Player
from card import Card, Suit


class GameState(Enum):
    PlayerTurn = auto()
    PlayerDiscard = auto()
    PlayerPickup = auto()
    PlayerYaniv = auto()
    ComputerTurn = auto()


class Yaniv:
    deck = []
    trash = []
    pickup_options: []
    num_ai_players: int = 3
    players_list: List[Player] = []
    yaniv_total: int
    cur_turn: int
    state: GameState


    def __init__(self, num_ai_players: int, yaniv_total=7, ai_difficulty: dict = None):
        self.yaniv_total = yaniv_total
        rank_list = ['A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K']
        for rank in rank_list:
            for suit in [Suit.Diamonds, Suit.Hearts, Suit.Clubs, Suit.Spades]:
                self.deck.append(Card(suit, rank))

        self.deck.append(Card(Suit.Joker, 'X'))
        random.shuffle(self.deck)

        user = Player('Player Name')
        self.players_list.append(user)
        for i in range(num_ai_players):
            self.players_list.append(Computer(f'AI {i + 1}', i))

        for i in range(5):
            for p in self.players_list:
                p.pickup_card(self.deck.pop())

        self.trash.append(self.deck.pop())

        # for p in self.players_list:
        #     print(p, '\n')

        self.cur_turn = 0  # random.randint(0, len(self.players_list) - 1)
        if isinstance(self.players_list[self.cur_turn], Computer):
            self.state = GameState.ComputerTurn
        else:
            self.state = GameState.PlayerTurn


    @staticmethod
    def get_menu_choice(valid_choices: Set) -> str:
        while True:
            choice = input()
            if choice.upper().strip() in valid_choices:
                return choice.upper().strip()
            print('Invalid choice. Please enter one of', valid_choices)


    def player_turn(self):
        game_menu = '{player}\nCurrent Top of Discard Pile: {discard}\n\nWhat would you like to do?\n{menu}'
        menu_options = '[D] Discard card(s)\n[Q] Quit'
        yaniv_menu_options = '[D] Discard card(s)\n[C] Call Yaniv\n[Q] Quit'

        can_call_yaniv = self.players_list[self.cur_turn].calc_hand_value() > self.yaniv_total
        print(game_menu.format(player=self.players_list[self.cur_turn], discard=self.trash[-1], menu=yaniv_menu_options if can_call_yaniv else menu_options))

        choice = self.get_menu_choice({'D', 'C', 'Q'} if can_call_yaniv else {'D', 'Q'})
        if choice == 'D':
            self.state = GameState.PlayerDiscard
        elif choice == 'C':
            self.state = GameState.PlayerYaniv
        elif choice == 'Q':
            print('Are you sure? Y/N')
            choice = self.get_menu_choice({'Y', 'N'})
            if choice == 'Y':
                exit(0)


    def player_discard(self):
        discard_options = self.players_list[self.cur_turn].get_discard_options()
        print(self.players_list[0])
        print('Discard Options:', discard_options)
        # print('Pick-up Options:', pickup_options)


    def play(self):
        while True:
            if self.state == GameState.ComputerTurn:
                pass
            elif self.state == GameState.PlayerTurn:
                self.player_turn()
            elif self.state == GameState.PlayerDiscard:
                self.player_discard()


if __name__ == '__main__':
    yaniv = Yaniv(3, 7)
    yaniv.play()
