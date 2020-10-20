from __future__ import absolute_import

import csv

from . import DealFormat
from .. import dto

class CSVFormat(DealFormat):
    @property
    def suffix(self):
        return '.csv'

    def parse_content(self, content):
        dealset = []
        for line in csv.reader(content):
            deal = dto.Deal()
            deal.number = int(line[16])
            dealers = {'N': dto.POSITION_NORTH,
                       'E': dto.POSITION_EAST,
                       'S': dto.POSITION_SOUTH,
                       'W': dto.POSITION_WEST}
            deal.dealer = dealers[line[17].split('/')[0]]
            for pair in ['NS', 'EW']:
                deal.vulnerable[pair] = line[17].split('/')[1] in [pair, 'All']
            for hand in range(0, 4):
                for suit in range(0, 4):
                    deal.hands[hand][suit] = list(line[hand*4+suit])
            dealset.append(deal)
        return dealset

    def output_content(self, out_file, dealset):
        writer = csv.writer(out_file, quoting=csv.QUOTE_ALL)
        for deal in dealset:
            line = []
            for hand in deal.hands:
                line += [''.join(suit) for suit in hand]
            line += [str(deal.number), '']
            line[17] = 'NESW'[deal.dealer] + '/'
            line[17] += ('All' if deal.vulnerable['EW'] else 'NS') \
                if deal.vulnerable['NS'] \
                   else ('EW' if deal.vulnerable['EW'] else '-')
            writer.writerow(line)
