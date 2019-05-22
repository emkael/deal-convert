import warnings

from . import DealFormat
from .. import dto

class DGEFormat(DealFormat):
    number_warning = '.dge file format assumes consequent deal numbers from 1'
    suits = {
        chr(6): dto.SUIT_SPADES,
        chr(3): dto.SUIT_HEARTS,
        chr(4): dto.SUIT_DIAMONDS,
        chr(5): dto.SUIT_CLUBS
    }

    def suit_indicator(self, the_suit):
        for indicator, suit in self.suits.iteritems():
            if suit == the_suit:
                return indicator
        return None

    @property
    def suffix(self):
        return '.dge'

    def parse_content(self, content):
        warnings.warn(self.number_warning)
        dealset = []
        number = 1
        while True:
            deal_str = content.read(128).strip()
            if len(deal_str) > 0:
                if len(deal_str) < 68:
                    warnings.warn('truncated .dge input: %s' % (deal_str))
                    break
                else:
                    deal = dto.Deal()
                    deal.number = number
                    deal.dealer = deal.get_dealer(number)
                    deal.vulnerable = deal.get_vulnerability(number)
                    deal.hands = self.parse_hands(deal_str[0:68])
                    dealset.append(deal)
                    number += 1
            else:
                break
        return dealset

    def parse_hands(self, deal_str):
        deal = dto.Deal()
        hand = 0
        suit_count = -1
        suit = None
        for char in deal_str[0:68]:
            if char in self.suits:
                suit = self.suits[char]
                suit_count += 1
                if suit_count == 4:
                    suit_count = 0
                    hand += 1
            else:
                if suit is None:
                    raise RuntimeError('invalid .dge line: %s' % (deal_str))
                else:
                    deal.hands[hand][suit].append(char)
        return deal.hands

    def output_content(self, out_file, dealset):
        warnings.warn(self.number_warning)
        for deal in dealset:
            deal_str = self.single_deal_output(deal)
            deal_str += chr(0) * 60
            out_file.write(deal_str)

    def single_deal_output(self, deal):
        deal_str = ''
        for hand in deal.hands:
            for suit, cards in enumerate(hand):
                deal_str += self.suit_indicator(suit)
                deal_str += ''.join(cards)
        return deal_str
