import random
from typing import List, Tuple

from player import Player
from card import Card
from utils import GameState


class Computer(Player):
    memory: List[Player]
    trash_memory: List[Card]
    level: int
    memory_chance: int

    # In a full deck, the average value of a randomly drawn card is ~6.3
    AVG_RAND_CARD_VAL = 6.296296296

    # Level 1 = Random actions
    # Level 2 = Optimal actions (discard higher cards, sequences, doubles, triples, favor drawing lower cards)
    # Level 3 = Optimal actions but remembers what was discarded/picked up 30% of the time
    # Level 4 = Optimal actions but remembers what was discarded/picked up 60% of the time
    # Level 5 = Optimal actions but remembers what was discarded/picked up 100% of the time

    def __init__(self, name: str, level: int, opponents: List[Player] = None):
        super().__init__(name)
        self.level = level

        if level > 2:
            self.memory = [p for p in opponents]

            memory_chance_dict = {3: 0.3, 4: 0.6, 5: 1}
            self.memory_chance = memory_chance_dict.get(level, 1)


    def choose_action(self, yaniv_total, pickup_options) -> GameState:
        if self.calc_hand_value() <= yaniv_total:
            return GameState.CallYaniv
        else:
            return GameState.DiscardPickup


    def do_turn(self, pickup_options: List[Card]) ->  Tuple[Card, int]:
        # Get the discard options
        discard_options = self.get_discard_options()

        if self.level == 1:
            # Level 1 AI makes random discard and pickup choices
            discard_choice = discard_options[random.randint(0, len(discard_options) - 1)]
            pickup_choice = random.randint(1, len(pickup_options) + 1)

        print(f'{self.name} discarded', discard_choice)
        return discard_choice, pickup_choice
