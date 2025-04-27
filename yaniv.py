import random
import time
from typing import List, Dict

from card import Card, Suit
from computer import Computer
from player import Player
from utils import GameState


class Yaniv:
    deck = []
    trash = []
    pickup_options: List[Card]
    num_comp_players: int = 3
    players_list: List[Player] = []
    yaniv_total: int
    cur_turn: int
    state: GameState
    ASSAF_PENALTY = 25


    def __init__(self, player_name: str, num_comp_players: int, yaniv_total=7, computer_difficulty: Dict[str, int] = None):
        self.yaniv_total = yaniv_total
        user = Player(player_name)
        self.players_list.append(user)

        if computer_difficulty is None:
            for i in range(num_comp_players):
                self.players_list.append(Computer(f'Computer {i + 1}', 2))
        else:
            for name in computer_difficulty:
                self.players_list.append(Computer(name, computer_difficulty[name]))

        # random.shuffle(self.players_list)

        self.new_round()
        self.state = GameState.ChooseAction


    def new_round(self, starting_turn: int = 0):
        self.deck.clear()
        self.trash.clear()
        rank_list = ['A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K']
        for rank in rank_list:
            for suit in [Suit.Diamonds, Suit.Hearts, Suit.Clubs, Suit.Spades]:
                self.deck.append(Card(suit, rank))

        self.deck.append(Card(Suit.Joker, 'X'))
        self.deck.append(Card(Suit.Joker, 'X'))
        random.shuffle(self.deck)

        for p in self.players_list:
            p.discard_hand()

        for i in range(5):
            for p in self.players_list:
                p.pickup_card(self.deck.pop())

        self.trash.append(self.deck.pop())
        self.pickup_options = [self.trash[-1]]

        print(f'New round! {self.players_list[starting_turn].name} goes first')
        self.cur_turn = starting_turn


    def next_player_turn(self):
        self.cur_turn += 1
        if self.cur_turn >= len(self.players_list):
            self.cur_turn = 0

        self.state = GameState.ChooseAction
        print(f'\nCurrent turn: {self.players_list[self.cur_turn].name}')


    def player_discard_pickup(self):
        player = self.players_list[self.cur_turn]

        discard_choice, pickup_choice = player.do_turn(self.pickup_options)

        if pickup_choice > len(self.pickup_options):
            # If the pickup choice is draw from the deck, remove the top card from the deck and add it to your hand

            if len(self.deck) == 0:
                self.deck = self.trash[:-1]
                self.trash = [self.trash[-1]]
                random.shuffle(self.deck)

            deck_card = self.deck.pop()

            if isinstance(player, Computer):
                print(f'{player.name} drew from the deck')
            else:
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
        if isinstance(discard_choice, list):
            # If multiple cards were discarded, only keep the first and second
            for d in discard_choice:
                player.discard_card(d)
                self.trash.append(d)
            discard_choice = [discard_choice[0], discard_choice[-1]]
        else:
            player.discard_card(discard_choice)
            self.trash.append(discard_choice)
            discard_choice = [discard_choice]

        if not isinstance(player, Computer):
            # Display the user's new hand and end the turn
            print(player)
        else:
            time.sleep(2)
        self.pickup_options = discard_choice
        self.next_player_turn()


    def call_yaniv(self):
        # If a player calls Yaniv, check if any other players have a smaller hand than them
        winner = self.players_list[self.cur_turn]
        print(f'{winner.name} called Yaniv with {winner.cards} Hand total is ', winner.calc_hand_value())

        # Go through each player and check if any have a smaller hand
        # If they do, the player that called Yaniv gets a penalty instead of 0 points
        winning_player_index = None
        i = 0
        for p in self.players_list:
            if p != self.players_list[self.cur_turn]:
                hand_value = p.calc_hand_value()
                print(f'{p.name} {p.cards} = {hand_value}')
                if hand_value < winner.calc_hand_value():
                    winner = p
                    winning_player_index = i
            i += 1

        print('')
        if winning_player_index is not None:
            print(f'{winner.name} called Assaf! {self.players_list[self.cur_turn].name} is penalized an additional {self.ASSAF_PENALTY} points')

        for p in self.players_list:
            if p == winner:
                continue
            if p == self.players_list[self.cur_turn]:
                p.add_points(self.ASSAF_PENALTY)
            else:
                p.add_points()

        print('\n     SCOREBOARD     ')
        print('====================')
        for p in self.players_list:
            print(p.name, p.points[-1])
        print('====================\n')

        # If a player goes over 100 points, they lose and are eliminated from the game
        for p in self.players_list[:]:
            if p.points[-1] > 100:
                print(f'{p.name} is eliminated')
                self.players_list.remove(p)

        # If all players have been eliminated, declare a winner
        if len(self.players_list) == 1:
            print(f'{self.players_list[0].name.upper()} WINS!')
            exit(0)
        else:
            winning_player_index = self.players_list.index(winner)
            self.new_round(winning_player_index)
            self.state = GameState.ChooseAction
        print('')


    def play(self):
        while True:
            if self.state == GameState.ChooseAction:
                self.state = self.players_list[self.cur_turn].choose_action(self.yaniv_total, self.pickup_options)
            elif self.state == GameState.DiscardPickup:
                self.player_discard_pickup()
            elif self.state == GameState.CallYaniv:
                self.call_yaniv()


if __name__ == '__main__':
    yaniv = Yaniv('Player', 3, 7)
    yaniv.play()
