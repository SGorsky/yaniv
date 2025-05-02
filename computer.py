import random
from typing import List, Tuple, Union, Set, Optional

from card import Card, Suit
from player import Player
from utils import GameState


class Computer(Player):
    __deck: Set[Card]
    __deck_total: int
    __level: int
    __memory: dict
    __memory_chance: int
    __trash_memory: List[Card]

    # In a full deck, the average value of a randomly drawn card is ~6.3
    __AVG_RAND_CARD_VAL = 6.296296296


    # Level 1 = Random actions
    # Level 2 = Optimal actions (discard higher cards, sequences, doubles, triples, favor drawing lower cards)
    # Level 3 = Optimal actions but remembers what was discarded/picked up 30% of the time
    # Level 4 = Optimal actions but remembers what was discarded/picked up 60% of the time
    # Level 5 = Optimal actions but remembers what was discarded/picked up 100% of the time

    def __init__(self, name: str, level: int):
        super().__init__(name)
        self.__level = level

        if level >= 3:
            memory_chance_dict = {3: 0.3, 4: 0.6, 5: 1}
            self.__memory_chance = memory_chance_dict.get(level, 1)
            self.__deck = set()
            self.__deck_total = 340


    def initialize_memory(self, other_players: List[str]):
        if self.__level >= 3:
            self.__memory = {p: {'num_cards': 5, 'hand': [], 'recent_discard': None} for p in other_players if p != self.name}


    def reset(self):
        super().reset()

        if self.__level >= 3:
            self.__memory.clear()
            self.__deck.clear()
            self.__deck_total = 340

            rank_list = ['A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K']

            for suit in [Suit.Diamonds, Suit.Hearts, Suit.Clubs, Suit.Spades]:
                for rank in rank_list:
                    self.__deck.add(Card(suit, rank))
            self.__deck.add(Card(Suit.Joker, 'X1'))
            self.__deck.add(Card(Suit.Joker, 'X2'))


    def pickup_card(self, new_card: Card) -> None:
        super().pickup_card(new_card)
        self.observe(new_card)


    def observe(self, discard: Union[Card, List[Card]], pickup: Optional[Card] = None, player_name: str = None):
        if self.__level <= 2:
            return

        if isinstance(discard, Card):
            discard = [discard]

        for card in discard:
            if card in self.__deck:
                self.__deck.remove(card)
                self.__deck_total -= card.value()

        if player_name:
            self.__memory[player_name]['recent_discard'] = discard
            self.__memory[player_name]['num_cards'] -= len(discard) - 1

            for card in discard:
                if card in self.__memory[player_name]['hand']:
                    self.__memory[player_name]['hand'].remove(card)
            if pickup is not None:
                self.__memory[player_name]['hand'].append(pickup)


    def choose_action(self, yaniv_total, pickup_options) -> GameState:
        if self.calc_hand_value() <= yaniv_total:
            return GameState.CallYaniv
        else:
            return GameState.DiscardPickup


    def __get_new_discard_options(self, discard_options: List[Union[Card, List[Card]]], new_card: Card) -> List[List[Card]]:
        self.pickup_card(new_card)
        new_discard_options = self.get_discard_options()
        self.discard_card(new_card)

        for d in discard_options:
            try:
                new_discard_options.remove(d)
            except ValueError:
                pass

        new_discard_options.remove(new_card)
        return new_discard_options


    @staticmethod
    def __evaluate_discards(discard_options):
        # Go through the Computer's hand and find the discard value of each of the options
        # Find the biggest discard option
        discard_value = []
        max_discard = 0
        max_index = []
        for i in range(len(discard_options)):
            val = discard_options[i].value() if isinstance(discard_options[i], Card) else sum([c.value() for c in discard_options[i]])
            discard_value.append(val)

            if val == max_discard:
                max_index.append(i)
            elif val > max_discard:
                max_index = [i]
                max_discard = val

        return max_index, max_discard


    def do_turn(self, pickup_options: List[Union[Card]]) -> Tuple[Card, int]:
        # Get the discard options
        discard_options = self.get_discard_options()

        if self.__level == 1:
            # Level 1 Computer makes random discard and pickup choices
            discard_choice = discard_options[random.randint(0, len(discard_options) - 1)]
            pickup_choice = random.randint(1, len(pickup_options) + 1)
        else:
            max_index, max_discard = self.__evaluate_discards(discard_options)
            pickup_choice = None
            discard_choice = None

            # Check each possible pickup option
            new_discard_max = None
            for pickup_index in range(len(pickup_options)):
                # If the card is a joker, automatically pick it up. There is never a reason to not pick up a joker
                if pickup_options[pickup_index].suit == Suit.Joker:
                    pickup_choice = pickup_index
                    discard_choice = discard_options[max_index[0]]
                    break

                # Check if you get any new discard options by picking up this card
                new_discard_options = self.__get_new_discard_options(discard_options, pickup_options[pickup_index])
                for new_discard_set in new_discard_options:
                    val = sum([card.value() for card in new_discard_set])

                    if val <= max_discard:
                        # If the new option is less or equal to the current best discard, see if you can discard the current best option,
                        # then pickup the new card and drop the new set next turn
                        for i in max_index:
                            if isinstance(discard_options[i], list) and not any([card in discard_options[i] for card in new_discard_set]):
                                pickup_choice = pickup_index
                                break
                            elif isinstance(discard_options[i], Card) and discard_options[i] not in new_discard_set:
                                pickup_choice = pickup_index
                                break

                    # If picking up a new card gives you a new discard option that's better than your current best discard, you should pick up the card
                    # Pick a card that you can drop so that next turn you can drop this new better set
                    elif val > max_discard and (new_discard_max is None or val > new_discard_max):
                        # Create a new temporary discard options list
                        # Check each discard option for cards that are in the new discard set.
                        # Set that discard option to None
                        tmp_discard_options = [d for d in discard_options]
                        for j in range(len(discard_options)):
                            if isinstance(discard_options[j], Card):
                                if discard_options[j] in new_discard_set:
                                    tmp_discard_options[j] = Card(Suit.Joker, 'X1')
                            else:
                                if any(card in new_discard_set for card in discard_options[j]):
                                    tmp_discard_options[j] = Card(Suit.Joker, 'X1')

                        if any([x.suit != Suit.Joker for x in tmp_discard_options if isinstance(x, Card)]):
                            max_index, max_discard = self.__evaluate_discards(tmp_discard_options)
                            pickup_choice = pickup_index
                            new_discard_max = val

            if discard_choice is None:
                if len(max_index) == 1:
                    discard_choice = discard_options[max_index[0]]
                else:
                    # If there are multiple possible discard options that have the same discard value
                    # Get the discard options with jokers, the number of cards that are discarded and the smallest value card that's discarded
                    has_jokers = []
                    num_cards = []
                    min_val_card = []
                    for pickup_index in max_index[:]:
                        if isinstance(discard_options[pickup_index], list):
                            if any([c.suit == Suit.Joker for c in discard_options[pickup_index]]):
                                has_jokers.append(pickup_index)
                            num_cards.append(len(discard_options[pickup_index]))
                            min_val_card.append(discard_options[pickup_index][0])
                        else:
                            num_cards.append(1)
                            min_val_card.append(discard_options[pickup_index])

                    # If there are no jokers, all the options have the same number of cards and all have the same minimum card value
                    # the discard choices are the combinations of 3 of the same card. Pick the first one
                    if len(max_index) == 3 and len(has_jokers) == 0 and all(x == num_cards[0] for x in num_cards) and all(x.value() == min_val_card[0].value() for x in min_val_card):
                        discard_choice = discard_options[max_index[0]]

                    # If there are multiple drop options with the same drop value but one has a larger min card value,
                    # it's better to drop that than give the next player a lower card to pickup
                    elif not all(x.value() == min_val_card[0].value() for x in min_val_card):
                        min_card = max(min_val_card, key=lambda x: x.value())
                        discard_choice = discard_options[max_index[min_val_card.index(min_card)]]

                    # With all discard options having the same min values, multiple drop options that have the same value, just pick the first one
                    elif all(x == num_cards[0] for x in num_cards):
                        discard_choice = discard_options[max_index[0]]

            if pickup_choice is None:
                deck_avg_val = self.__AVG_RAND_CARD_VAL if self.__level == 2 else self.__deck_total / len(self.__deck)
                if pickup_options[0].value() < deck_avg_val:
                    pickup_choice = 0
                else:
                    pickup_choice = len(pickup_options)

        print(f'{self.name} discarded', discard_choice)
        return discard_choice, pickup_choice + 1
