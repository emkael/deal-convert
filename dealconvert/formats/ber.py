import warnings

from . import DealFormat
from .. import dto

class BERFormat(DealFormat):
    number_warning = '.ber file format assumes consequent deal numbers from 1'

    @property
    def suffix(self):
        return '.ber'

    def parse_content(self, content):
        warnings.warn(self.number_warning)
        dealset = []
        number = 1
        while True:
            deal_str = content.read(52).strip()
            if len(deal_str) > 0:
                if len(deal_str) < 52:
                    warnings.warn('truncated .ber input: %s' % (deal_str))
                    break
                deal = dto.Deal()
                deal.number = number
                deal.dealer = deal.get_dealer(number)
                deal.vulnerable = deal.get_vulnerability(number)
                for suit in range(0, 4):
                    for card in range(0, 13):
                        try:
                            deal.hands[int(deal_str[suit*13 + card])-1][suit].append(self.cards[card])
                        except (IndexError, ValueError):
                            raise RuntimeError(
                                'invalid character in .ber file: %s' % (
                                    deal_str[suit*13 + card]))
                dealset.append(deal)
                number += 1
            else:
                break
        return dealset


    def output_content(self, out_file, dealset):
        warnings.warn(self.number_warning)
        for board in dealset:
            deal_str = [' '] * 52
            for i, hand in enumerate(board.hands):
                for j, suit in enumerate(hand):
                    for card in suit:
                        try:
                            deal_str[j*13 + self.cards.index(card)] = str(i + 1)
                        except ValueError:
                            raise RuntimeError(
                                'invalid card character: %s in board %d' % (card, board.number))
            if ' ' in deal_str:
                warnings.warn('not all cards present in board %d' % (
                    board.number))
            out_file.write(''.join(deal_str))
