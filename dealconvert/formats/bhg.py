import warnings

from . import DealFormat
from .. import dto

class BHGFormat(DealFormat):
    @property
    def suffix(self):
        return '.bhg'

    def parse_content(self, content):
        board_lines = [line.strip() for line in content.readlines()]
        deals = []
        for board_no, line in enumerate(board_lines):
            if board_no > 0:
                if len(line) != 52:
                    warnings.warn(
                        'malformed .bhg line #%d: %s' % (board_no, line))
                elif not line.isalpha():
                    warnings.warn(
                        'invalid characters in .bhg line #%d: %s' % (
                            board_no, line))
                else:
                    deal = dto.Deal()
                    deal.number = board_no
                    deal.vulnerable = deal.get_vulnerability(board_no)
                    deal.dealer = deal.get_dealer(board_no)
                    hands = [[
                        ord(c) - 65 if ord(c) < 96 else ord(c) - 71
                        for c in list(
                            line[13*i:13*(i+1)]
                        )] for i in range(0, 4)
                    ]
                    for hand, cards in enumerate(hands):
                        for card in cards:
                            suit = card / 13
                            card = self.cards[card % 13]
                            deal.hands[(hand + deal.dealer) % 4][suit].append(card)
                    deals.append(deal)
        return deals

    def output_content(self, out_file, dealset):
        lines = [''] * (max([board.number for board in dealset])+2)
        for deal in dealset:
            line = ''
            for hand in range(0, 4):
                for i, suit in enumerate(deal.hands[(hand + deal.dealer) % 4]):
                    try:
                        cards = [13*i + self.cards.index(card) for card in suit]
                        for card in cards:
                            line += chr((65 if card < 26 else 71)+card)
                    except ValueError:
                        raise RuntimeError(
                            'invalid suit %s in board #%d' % (
                                ''.join(suit), deal.number))
            lines[deal.number] = line
        out_file.write('\r\n'.join(lines))
