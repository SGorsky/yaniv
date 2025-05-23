import random
from itertools import combinations
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


    def initialize_memory(self, other_players: List[str]) -> None:
        if self.__level >= 3:
            self.__memory = {p: {'num_cards': 5, 'hand': [], 'discard': [], 'pickup': []} for p in other_players if p != self.name}


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


    def observe(self, discard: Union[Card, List[Card]], pickup: Optional[Union[Card, str]] = None, player_name: str = None) -> None:
        if self.__level <= 2:
            return

        if isinstance(discard, Card):
            discard = [discard]

        for card in discard:
            if card in self.__deck:
                self.__deck.remove(card)
                self.__deck_total -= card.value()

        if player_name:
            self.__memory[player_name]['discard'].append(discard)
            self.__memory[player_name]['num_cards'] -= len(discard) - 1

            for card in discard:
                if card in self.__memory[player_name]['hand']:
                    self.__memory[player_name]['hand'].remove(card)
            if pickup is not None:
                if isinstance(pickup, Card):
                    self.__memory[player_name]['hand'].append(pickup)
                self.__memory[player_name]['pickup'].append(pickup)


    def choose_action(self, yaniv_total: float, pickup_options: List[Card]) -> GameState:
        if self.calc_hand_value() <= yaniv_total:
            if self.__level == 3:
                if self.calc_hand_value() == 0:
                    return GameState.CallYaniv

                for p in self.__memory:
                    # If chance of assaf is more than 5% (can be changed), don't call yaniv
                    chance_of_assaf = self.calc_probability_less_than(self.__memory[p], self.calc_hand_value())
                    if chance_of_assaf > 0.05:
                        return GameState.DiscardPickup
            return GameState.CallYaniv
        else:
            return GameState.DiscardPickup


    def calc_probability_less_than(self, player_memory: dict, less_than_val: float) -> float:
        # The purpose of this method is to check if the opponent can call Yaniv or if they can call Assaf and the Computer can call Yaniv
        # The less_than_val variable is meant to describe either the maximum Yaniv value or the Computer's hand value
        hand_total = sum([c.value() for c in player_memory['hand']])

        # If an opponent's known hand total is greater than or equal less_than_val, there is a 0% chance their hand is smaller
        if hand_total >= less_than_val:
            return 0

        # If we know all the cards in an opponent's hand and the total hand value is smaller than the less_than_val, return 1
        if player_memory['num_cards'] == len(player_memory['hand']) and hand_total < self.calc_hand_value():
            return 1

        unknown_card_count = player_memory['num_cards'] - len(player_memory['hand'])
        jokers_in_deck = (Card(Suit.Joker, 'X1') in self.__deck) + (Card(Suit.Joker, 'X2') in self.__deck)

        # If there are 5 unknown cards, or it's impossible to have a hand with a value smaller than less_than_val (even with jokers) return 0
        # Ex: less_than_val = 4, the player is holding a 2♣, has two unknown cards, and it's not possible they could be holding a joker
        # there is no way their hand could be less than 4
        # Ex: less_than_val = 4, the player is holding a 2♣, has two unknown cards, and there are two possible joker in the deck
        # they could have an Ace and a Joker which would give them a hand value of 3 or have two other jokers
        if unknown_card_count == 5 or less_than_val <= hand_total + unknown_card_count - jokers_in_deck:
            return 0

        # Iterate through the different combinations of possible cards they could have and count how many ways the opponent's hand could be
        # smaller than the less_than_val. Return the % of possibilities where such a hand value exists
        valid_combos, total_combos = 0, 0
        for combo in combinations(self.__deck, unknown_card_count):
            combo_value = sum(card.value() for card in combo)
            if hand_total + combo_value < less_than_val:
                valid_combos += 1
            total_combos += 1

        return valid_combos / total_combos


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
    def __evaluate_discards(discard_options: List[Union[Card, List[Card]]]) -> Tuple[List[int], int]:
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


    def do_turn(self, pickup_options: List[Card], yaniv_total: float) -> Tuple[Union[Card, List[Card]], int]:
        # Get the discard options
        discard_options = self.get_discard_options()
        if self.__level == 3:
            for p in self.__memory:
                # If chance of assaf is more than 5% (can be changed), don't call yaniv
                chance_of_assaf = self.calc_probability_less_than(self.__memory[p], yaniv_total)
                if chance_of_assaf > 0.2:
                    #TODO Do something if there's a good chance another player can call Yaniv
                    pass

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

                    # If all discard options have the same min card values and the same number of cards, just pick the first one
                    elif all(x == num_cards[0] for x in num_cards):
                        discard_choice = discard_options[max_index[0]]

                    # If one of the options has a joker, don't pick that one
                    elif len(has_jokers) != 0:
                        for i in max_index:
                            if i not in has_jokers:
                                discard_choice = discard_options[i]
                                break

            if pickup_choice is None:
                deck_avg_val = self.__AVG_RAND_CARD_VAL if self.__level == 2 else self.__deck_total / len(self.__deck)
                # 5% chance to decrease chance deck_avg value to help encourage drawing from the deck to avoid infinite loops where no computers want to draw
                if random.random() <= 0.05:
                    deck_avg_val -= 1
                if pickup_options[0].value() < deck_avg_val:
                    pickup_choice = 0
                else:
                    pickup_choice = len(pickup_options)

        print(f'{self.name} discarded', discard_choice)
        return discard_choice, pickup_choice + 1
