import warnings

from . import DealFormat
from .. import dto

class RZDFormat(DealFormat):
    number_warning = '.rzd file format assumes consequent deal numbers from 1'

    @property
    def suffix(self):
        return '.rzd'

    def parse_deal(self, data, offset=0):
        deal = dto.Deal()
        for card, byte in enumerate(data):
            byte = ord(byte)
            for suit in range(3, -1, -1):
                deal.hands[(byte%4 - offset)%4][suit].append(self.cards[card])
                byte /= 4
        return deal.hands

    def parse_content(self, content):
        warnings.warn(self.number_warning)
        dealset = []
        header = None
        number = 1
        while True:
            data = content.read(13)
            if len(data) < 13:
                if len(data) != 0:
                    warnings.warn('.rzd data truncated: %s' % (data))
                break
            if header is None:
                header = data
                continue
            deal = dto.Deal()
            deal.number = number
            deal.dealer = deal.get_dealer(number)
            deal.vulnerable = deal.get_vulnerability(number)
            deal.hands = self.parse_deal(data)
            dealset.append(deal)
            number += 1
        return dealset

    def dump_deal(self, deal, offset=0):
        value = ''
        values = [None] * 52
        for i, hand in enumerate(deal.hands):
            for suit, cards in enumerate(hand):
                for card in cards:
                    try:
                        idx = self.cards.index(card)
                    except ValueError:
                        raise RuntimeError('invalid card: %s in board %d' % (card, deal.number))
                    values[idx*4+suit] = (i + offset)%4
        for i in range(0, 13):
            byte = 0
            for j in range(0, 4):
                if values[4*i+j] is None:
                    raise RuntimeError('missing card: %s%s in board %d' % ('SHDC'[j], self.cards[i], deal.number))
                byte *= 4
                byte += values[4*i+j]
            value += chr(byte)
        return value

    def output_content(self, out_file, dealset):
        warnings.warn(self.number_warning)
        board_count = len(dealset)
        out_file.write(chr(board_count%256))
        out_file.write(chr(board_count/256))
        out_file.write(' '*11)
        for deal in dealset:
            out_file.write(self.dump_deal(deal))
