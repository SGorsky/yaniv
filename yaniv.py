import random
from enum import auto, Enum
from typing import List, Set

import utils
from card import Card, Suit
from computer import Computer
from player import Player


class GameState(Enum):
    PlayerTurn = auto()
    PlayerDiscardPickup = auto()
    PlayerYaniv = auto()
    ComputerTurn = auto()


class Yaniv:
    deck = []
    trash = []
    pickup_options: List[Card]
    num_ai_players: int = 3
    players_list: List[Player] = []
    yaniv_total: int
    cur_turn: int
    state: GameState


    def __init__(self, player_name: str, num_ai_players: int, yaniv_total=7, ai_difficulty: dict = None):
        self.yaniv_total = yaniv_total
        rank_list = ['A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K']
        for rank in rank_list:
            for suit in [Suit.Diamonds, Suit.Hearts, Suit.Clubs, Suit.Spades]:
                self.deck.append(Card(suit, rank))

        self.deck.append(Card(Suit.Joker, 'X'))
        random.shuffle(self.deck)

        user = Player(player_name)
        self.players_list.append(user)
        for i in range(num_ai_players):
            self.players_list.append(Computer(f'AI {i + 1}', i))
        # random.shuffle(self.players_list)

        for i in range(5):
            for p in self.players_list:
                p.pickup_card(self.deck.pop())

        self.trash.append(self.deck.pop())
        self.pickup_options = [self.trash[-1]]

        # for p in self.players_list:
        #     print(p, '\n')

        self.cur_turn = 0  # random.randint(0, len(self.players_list) - 1)
        if isinstance(self.players_list[self.cur_turn], Computer):
            self.state = GameState.ComputerTurn
        else:
            self.state = GameState.PlayerTurn


    def next_player_turn(self):
        self.cur_turn += 1
        if self.cur_turn >= len(self.players_list):
            self.cur_turn = 0

        if isinstance(self.players_list[self.cur_turn], Computer):
            self.state = GameState.ComputerTurn
        else:
            self.state = GameState.PlayerTurn
        print(f'Current turn: {self.players_list[self.cur_turn].name}')


    def player_turn(self):
        game_menu = '{player}\nCurrent Top of Discard Pile: {discard}\n\nWhat would you like to do?\n{menu}'
        menu_options = '[D] Discard card(s)\n[Q] Quit'
        yaniv_menu_options = '[D] Discard card(s)\n[C] Call Yaniv\n[Q] Quit'

        can_call_yaniv = self.players_list[self.cur_turn].calc_hand_value() <= self.yaniv_total
        print(game_menu.format(player=self.players_list[self.cur_turn], discard=self.trash[-1], menu=yaniv_menu_options if can_call_yaniv else menu_options))

        choice = utils.get_menu_choice({'D', 'C', 'Q'} if can_call_yaniv else {'D', 'Q'})
        if choice == 'D':
            self.state = GameState.PlayerDiscardPickup
        elif choice == 'C':
            self.state = GameState.PlayerYaniv
        elif choice == 'Q':
            print('Are you sure? Y/N')
            choice = utils.get_menu_choice({'Y', 'N'})
            if choice == 'Y':
                exit(0)


    def player_discard_pickup(self):
        player = self.players_list[self.cur_turn]

        discard_choice, pickup_choice = player.do_turn(self.pickup_options)

        if pickup_choice > len(self.pickup_options):
            # If the pickup choice is draw from the deck, remove the top card from the deck and add it to your hand
            deck_card = self.deck.pop()
            print(f'{player.name} drew a {deck_card} from the deck')

            player.pickup_card(deck_card)
        else:
            # If the pickup choice is drawing from the trash, remove that card from the pile and add it to your hand
            print(f'{player.name} picked up', self.pickup_options[pickup_choice - 1])
            player.pickup_card(self.pickup_options[pickup_choice - 1])

            if self.trash[-1] == self.pickup_options[pickup_choice - 1]:
                self.trash.pop()
            else:
                self.trash.remove(self.pickup_options[pickup_choice - 1])

        # Remove the discarded cards from the player's hand and add them to the trash
        if isinstance(discard_choice, List):
            # If multiple cards were discarded, only keep the first and second
            for d in discard_choice:
                player.discard_card(d)
                self.trash.append(d)
            discard_choice = [discard_choice[0], discard_choice[-1]]
        else:
            player.discard_card(discard_choice)
            self.trash.append(discard_choice)
            discard_choice = [discard_choice]

        # Display the new hand and end the turn
        print(player, '\n')
        self.pickup_options = discard_choice
        self.next_player_turn()


    def play(self):
        while True:
            if isinstance(self.players_list[self.cur_turn], Computer):
                pass
            else:
                if self.state == GameState.PlayerTurn:
                    self.player_turn()
                elif self.state == GameState.PlayerDiscardPickup:
                    self.player_discard_pickup()


if __name__ == '__main__':
    yaniv = Yaniv('Player', 3, 7)
    yaniv.play()
