import warnings

from . import DealFormat
from .. import dto

class BRIFormat(DealFormat):
    number_warning = '.bri file format assumes consequent deal numbers from 1'

    @property
    def suffix(self):
        return '.bri'

    def parse_content(self, content):
        warnings.warn(self.number_warning)
        dealset = []
        number = 1
        while True:
            deal_str = content.read(128).strip()
            if len(deal_str) > 0:
                if len(deal_str) < 78:
                    warning.warn('truncated .bri input: %s' % (deal_str))
                    break
                else:
                    deal_obj = dto.Deal()
                    deal_obj.number = number
                    deal_obj.dealer = deal_obj.get_dealer(number)
                    deal_obj.vulnerable = deal_obj.get_vulnerability(number)
                    deal_obj.hands = self.parse_hands(deal_str)
                    dealset.append(deal_obj)
                    number += 1
            else:
                break
        return dealset

    def parse_hands(self, deal_str):
        deal_obj = dto.Deal()
        try:
            deal = [int(deal_str[i*2:(i+1)*2], 10) for i in range(0, 39)]
            if max(deal) > 52:
                raise RuntimeError(
                    'invalid card in .bri file: %d' % (max(deal)))
            for hand in range(0, 3):
                for card in deal[13*hand:13*(hand+1)]:
                    card = card - 1
                    suit = card // 13
                    card = card % 13
                    deal_obj.hands[hand][suit].append(self.cards[card])
            deal_obj.fill_west()
        except ValueError:
            raise RuntimeError('invalid card in .bri file: %s' % (deal_str))
        return deal_obj.hands

    def output_content(self, out_file, dealset):
        warnings.warn(self.number_warning)
        for deal in dealset:
            deal_str = self.single_deal_output(deal)
            deal_str += ' ' * 32
            deal_str += chr(0) * 18
            out_file.write(deal_str)

    def single_deal_output(self, deal):
        deal_str = ''
        for hand in deal.hands[0:3]:
            for i, suit in enumerate(hand):
                for card in suit:
                    try:
                        deal_str += '%02d' % (self.cards.index(card) + 13*i + 1)
                    except ValueError:
                        raise RuntimeError(
                            'invalid card character: %s in board %d' % (card, deal.number))
        return deal_str
