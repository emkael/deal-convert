from collections import OrderedDict
from urlparse import urlparse, parse_qsl
from urllib import urlencode
import re, warnings

from . import DealFormat
from .. import dto

class TXTFormat(DealFormat):

    _url_prefix = 'https://www.bridgebase.com/tools/handviewer.html'
    _hand_format = re.compile(r'([shdc])([akqjt2-9]*)', re.I)
    _hand_designations = {
        'n': dto.POSITION_NORTH,
        'e': dto.POSITION_EAST,
        's': dto.POSITION_SOUTH,
        'w': dto.POSITION_WEST
    }
    _suit_designations = {
        's': dto.SUIT_SPADES,
        'h': dto.SUIT_HEARTS,
        'd': dto.SUIT_DIAMONDS,
        'c': dto.SUIT_CLUBS
    }

    @property
    def suffix(self):
        return '.txt'

    def parse_content(self, content):
        deal_list = []
        deal_numbers = []
        renumber_deals = False
        event = ''
        lines = [line.strip() for line in content.readlines()]
        for line in lines:
            if line.startswith(self._url_prefix):
                deal = dto.Deal()
                url = urlparse(line)
                params = OrderedDict(parse_qsl(url.query))
                for hand in self._hand_designations.keys():
                    if hand not in params:
                        raise RuntimeError(
                            'URL %s is missing "%s" hand' % (
                                line, hand
                            )
                        )
                    suits = OrderedDict(
                        self._hand_format.findall(params[hand]))
                    for suit, cards in suits.iteritems():
                        cards = cards.upper()
                        deal.hands[
                            self._hand_designations[hand]
                        ][
                            self._suit_designations[suit]
                        ] = list(cards)
                if 'b' in params:
                    try:
                        deal.number = int(params['b'])
                    except:
                        warnings.warn(
                            'URL %s contains no deal number. ALL deals will be auto-number, maintaining their vulnerability if defined' % (line)
                        )
                        renumber_deals = True
                else:
                    warnings.warn(
                        'URL %s contains no deal number. ALL deals will be auto-number, maintaining their vulnerability if defined' % (line)
                    )
                    renumber_deals = True
                if deal.number:
                    if deal.number in deal_numbers:
                        warnings.warn(
                            'Duplicate deal number %d. ALL deals will be auto-number, maintaining their vulnerability if defined' % (deal.number)
                        )
                        renumber_deals = True
                    deal_numbers.append(deal.number)
                if 'v' in params:
                    deal.vulnerable['NS'] = params['v'].lower() in ['b', 'n']
                    deal.vulnerable['EW'] = params['v'].lower() in ['b', 'e']
                else:
                    deal.vulnerable = None
                if 'd' in params:
                    deal.dealer = self._hand_designations.get(
                        params['d'], None)
                deal.event = event
                event = ''
                deal_list.append(deal)
            else:
                event = line
        for idx, deal in enumerate(deal_list):
            if renumber_deals:
                deal.number = idx+1
            if not deal.vulnerable:
                deal.vulnerable = deal.get_vulnerability(deal.number)
            if not deal.dealer:
                deal.dealer = deal.get_dealer(deal.number)
        return deal_list

    def output_content(self, out_file, dealset):
        lines = []
        dealers = {}
        for designation, hand in self._hand_designations.iteritems():
            dealers[hand] = designation
        suits = {}
        for deal in dealset:
            if deal.event:
                lines.append(deal.event)
            params = {
                'b': deal.number,
                'd': dealers[deal.dealer],
                'v': ['0', 'n', 'e', 'b'][
                    deal.vulnerable['NS'] + 2 * deal.vulnerable['EW']
                ],
                'a': 'pppp'
            }
            for hand, designation in dealers.iteritems():
                params[designation] = ''
                for suit, idx in self._suit_designations.iteritems():
                    params[designation] += suit
                    params[designation] += ''.join(deal.hands[hand][idx]).lower()
            url = '%s?%s' % (
                self._url_prefix, urlencode(params))
            lines.append(url)
        for line in lines:
            out_file.write(line + '\r\n')
