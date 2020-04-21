from collections import OrderedDict
import re

from . import DealFormat
from .. import dto

class LINFormat(DealFormat):

    _qx_format = re.compile(r'^[oc](\d+)$')
    _ah_format = re.compile(r'^[A-Za-z ]* (\d+)$')
    _md_hand_format = re.compile(r'^S(.*)H(.*)D(.*)C(.*)$')
    _suit_cards = 'AKQJT98765432'

    @property
    def suffix(self):
        return '.lin'

    def parse_content(self, content):
        deals = OrderedDict()
        event = ''
        lines = [line.strip() for line in content.readlines()]
        for line in lines:
            chunks = line.split('|')
            fields = {}
            while len(chunks) > 1:
                field_name = chunks.pop(0)
                field_value = chunks.pop(0)
                if field_name not in fields:
                    fields[field_name] = []
                fields[field_name].append(field_value)
            if 'vg' in fields:
                event = fields['vg'][0].split(',')[0]
            if 'md' in fields:
                deal_number = None
                for field in ['qx', 'ah']:
                    if field in fields:
                        match = getattr(
                            self, '_%s_format' % (field)).match(
                                fields[field][0])
                        if match:
                            deal_number = int(match.group(1))
                            break
                if deal_number is not None:
                    layout = self._parse_md_field(fields['md'][0])
                    if layout:
                        if deal_number in deals:
                            if deals[deal_number] != layout:
                                raise RuntimeError('multiple boards #%d with different layouts' % (deal_number))
                        deals[deal_number] = layout
                    else:
                        print 'layout not parsed: ' + fields['md'][0]
        dealset = []
        for number, layout in deals.iteritems():
            deal = dto.Deal()
            deal.event = event
            deal.number = number
            deal.hands = layout
            deal.dealer = deal.get_dealer(deal.number)
            deal.vulnerable = deal.get_vulnerability(deal.number)
            dealset.append(deal)
        return dealset

    def _parse_md_field(self, value):
        try:
            hands = value[1:].split(',')
            layout = [[], [], [], []]
            for i, hand in enumerate(hands):
                layout[(i+2)%4] = self._parse_md_hand(hand) # hands always start from S
            for j, single_hand in enumerate(layout):
                if not sum([len(suit) for suit in single_hand]): # fill 4th hand if necessary
                    for k, suit in enumerate(single_hand):
                        layout[j][k] = ''.join([
                            c for c in self._suit_cards
                            if c not in ''.join([layout[h][k] for h in range(0, 4) if h != j])
                        ])
            for j, single_hand in enumerate(layout):
                for k, suit in enumerate(single_hand):
                    layout[j][k] = list(suit)
            return layout
        except:
            return None

    def _parse_md_hand(self, hand):
        match = self._md_hand_format.match(hand)
        if match:
            return [''.join(sorted(
                list(match.group(i)),
                key=lambda c: self._suit_cards.index(c)))
                    for i in range(1, 5)]
        return ['', '', '', '']

    def output_content(self, out_file, dealset):
        event_name = ([deal.event for deal in dealset if deal.event] or [''])[0]
        first_deal = min([deal.number for deal in dealset])
        last_deal = max([deal.number for deal in dealset])
        lines = [
            'vg|%s,SEGMENT 1,I,%d,%d,HOME,0,AWAY,0|' % (event_name, first_deal, last_deal),
            'rs|,,,,,,,,,,,|',
            'pn|,,,,,,,|pg||'
        ]
        for deal in dealset:
            dealer = (deal.dealer + 3) % 4 or 4
            layout = ''
            for i in range(0, 4):
                for s, suit in enumerate(deal.hands[(i+2) % 4]):
                    layout += 'SHDC'[s]
                    layout += ''.join(suit)
                if i < 3:
                    layout += ','
            vulnerability = ('b' if deal.vulnerable['EW'] else 'n') \
                if deal.vulnerable['NS'] \
                   else ('e' if deal.vulnerable['EW'] else '0')
            for room in ['o', 'c']:
                lines.append(
                    'qx|%s%d|pn|,,,,,,,|md|%d%s|sv|%s|pg||' % (
                        room, deal.number,
                        dealer, layout,
                        vulnerability
                    )
                )
        for line in lines:
            out_file.write(line + '\r\n')
