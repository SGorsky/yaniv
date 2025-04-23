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


    def get_discard_options(self):
        discard_options = []

        # Check for multiple cards of the same rank and suit
        # Ignore Jokers when it comes to single/duplicate discards
        rank_count = {}
        suit_count = {}
        for c in self.cards:
            if c.suit != Suit.Joker:
                discard_options.append(c)
                rank_count[c.rank] = rank_count.get(c.rank, 0) + 1
            suit_count[c.suit] = suit_count.get(c.suit, 0) + 1

        # If there are multiple cards of the same rank, show them as a discard option
        for rank in rank_count:
            rank_matches = [c for c in self.cards if c.rank == rank]
            if rank_count == 1:
                continue
            elif rank_count[rank] == 2:
                discard_options.append(rank_matches)
            elif rank_count[rank] == 3:
                discard_options.append([rank_matches[0], rank_matches[1], rank_matches[2]])
                discard_options.append([rank_matches[1], rank_matches[0], rank_matches[2]])
                discard_options.append([rank_matches[0], rank_matches[2], rank_matches[1]])
            elif rank_count[rank] == 4:
                discard_options.append([rank_matches[0], rank_matches[1], rank_matches[2], rank_matches[3]])
                discard_options.append([rank_matches[0], rank_matches[1], rank_matches[3], rank_matches[2]])
                discard_options.append([rank_matches[0], rank_matches[2], rank_matches[3], rank_matches[1]])
                discard_options.append([rank_matches[1], rank_matches[0], rank_matches[3], rank_matches[2]])
                discard_options.append([rank_matches[1], rank_matches[0], rank_matches[2], rank_matches[3]])
                discard_options.append([rank_matches[2], rank_matches[0], rank_matches[1], rank_matches[3]])


        # For each suit that appears at least 3 times on its own or twice with at least one Joker,
        # see if a sequence can be made with those cards
        for suit in suit_count:
            if suit == Suit.Joker:
                continue
            if suit_count[suit] >= 3 or (suit_count[suit] >= 2 and suit.Joker in suit_count):
                # Get all cards of the same suit. Cards are in order
                matching_suit_cards = [c for c in self.cards if c.suit == suit]

                # Try to start a sequence with each card
                for i in range(len(matching_suit_cards) - 1):
                    possible_sequence = [matching_suit_cards[i]]
                    j = i
                    joker_count = suit_count[suit.Joker] if suit.Joker in suit_count else 0

                    while j < len(matching_suit_cards) - 1:
                        # Check the difference between the current card and the next
                        # If diff is 1, the cards are in sequential order
                        # If the diff is > 1, check if there are jokers that can be used in between
                        rank_diff = RANK_ORDER[matching_suit_cards[j + 1].rank] - RANK_ORDER[matching_suit_cards[j].rank]
                        if rank_diff == 1:
                            possible_sequence.append(matching_suit_cards[j + 1])
                        elif rank_diff <= 1 + joker_count:
                            joker_count -= rank_diff - 1
                            for k in range(rank_diff - 1):
                                possible_sequence.append(self.cards[k])
                            possible_sequence.append(matching_suit_cards[j + 1])
                        else:
                            break

                        # If the sequence has 3 or more cards, it's valid on its own and can be added as a possible discard option
                        if len(possible_sequence) >= 3:
                            discard_options.append(possible_sequence)

                        # If the sequence has 2 cards, use the Joker at the beginning/end if it is a valid option
                        # Ex: We cannot have [Joker, Ace, 2] as a possible discard since Ace is the lowest card, but we can have [Ace, 2, Joker]
                        elif len(possible_sequence) == 2 and Suit.Joker in suit_count:
                            if possible_sequence[0].rank != 'A':
                                discard_options.append([self.cards[0]] + possible_sequence)
                            if possible_sequence[-1].rank != 'K':
                                discard_options.append(possible_sequence + [self.cards[0]])
                            break

                        j += 1

        return discard_options


    def __str__(self) -> str:
        return f'{self.name}\nHand: {self.cards}\nValue: {self.calc_hand_value()}'


    def __repr__(self):
        return self.__str__()
