# -*- coding: utf-8 -*-
# Copyright (c) 2003, Taro Ogawa.  All Rights Reserved.
# Copyright (c) 2013, Savoir-faire Linux inc.  All Rights Reserved.

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301 USA

from __future__ import unicode_literals

import itertools

from .base import Num2Word_Base
from .utils import get_digits, splitbyx

ZERO = ('zero', 'zerowy',)

ONES = {
    1: ('jeden', 'pierwszy'),
    2: ('dwa', 'drugi'),
    3: ('trzy','trzeci'),
    4: ('cztery','czwarty'),
    5: ('pięć', 'piąty'),
    6: ('sześć', 'szósty'),
    7: ('siedem', 'siódmy'),
    8: ('osiem', 'ósmy'),
    9: ('dziewięć', 'dziewiąty'),
}

TENS = {
    0: ('dziesięć', 'dziesiąty'),
    1: ('jedenaście', 'jedenasty'),
    2: ('dwanaście', 'dwunasty'),
    3: ('trzynaście', 'trzynasty'),
    4: ('czternaście', 'czternsty'),
    5: ('piętnaście', 'piętnasty'),
    6: ('szesnaście', 'szesnasty'),
    7: ('siedemnaście', 'sziedemnasty'),
    8: ('osiemnaście', 'osiemnasty'),
    9: ('dziewiętnaście', 'dziewiętnasty'),
}

TWENTIES = {
    2: ('dwadzieścia', 'dwudziesty'),
    3: ('trzydzieści', 'trzydziesty'),
    4: ('czterdzieści', 'czterdziesty'),
    5: ('pięćdziesiąt', 'pięćdziesiąty'),
    6: ('sześćdziesiąt', 'szceśdziesiąty'),
    7: ('siedemdziesiąt', 'siedemndziesiąty'),
    8: ('osiemdziesiąt', 'osiemndziesiąty'),
    9: ('dziewięćdzisiąt', 'dziewięćdziesiąty'),
}

HUNDREDS = {
    1: ('sto', 'setny'),
    2: ('dwieście', 'dwusetny'),
    3: ('trzysta', 'trzysetny'),
    4: ('czterysta', 'czterysetny'),
    5: ('pięćset', 'pięćsetny'),
    6: ('sześćset', 'sześćsetny'),
    7: ('siedemset', 'siedemsetny'),
    8: ('osiemset', 'osiemsetny'),
    9: ('dziewięćset', 'dziewięćsetny'),
}

THOUSANDS = {
    1: ('tysiąc', 'tysiące', 'tysięcy', 'tysięczny'),  # 10^3
}

prefixes = (   # 10^(6*x)
    "mi",      # 10^6
    "bi",      # 10^12
    "try",     # 10^18
    "kwadry",  # 10^24
    "kwinty",  # 10^30
    "seksty",  # 10^36
    "septy",   # 10^42
    "okty",    # 10^48
    "nony",    # 10^54
    "decy"     # 10^60
)
suffixes = ("lion", "liard")  # 10^x or 10^(x+3)

for idx, (p, s) in enumerate(itertools.product(prefixes, suffixes)):
    name = p + s
    THOUSANDS[idx+2] = (name, name + 'y', name + 'ów')


class Num2Word_PL(Num2Word_Base):
    CURRENCY_FORMS = {
        'PLN': (
            ('złoty', 'złote', 'złotych'), ('grosz', 'grosze', 'groszy')
        ),
        'EUR': (
            ('euro', 'euro', 'euro'), ('cent', 'centy', 'centów')
        ),
    }

    def setup(self):
        self.negword = "minus"
        self.pointword = "przecinek"

    def to_cardinal(self, number):
        n = str(number).replace(',', '.')
        if '.' in n:
            left, right = n.split('.')
            return u'%s %s %s' % (
                self._int2word(int(left)),
                self.pointword,
                self._int2word(int(right))
            )
        else:
            return self._int2word(int(n))

    def pluralize(self, n, forms):
        if n == 1:
            form = 0
        elif 5 > n % 10 > 1 and (n % 100 < 10 or n % 100 > 20):
            form = 1
        else:
            form = 2
        return forms[form]

    def to_ordinal(self, number):
        n = str(number).replace(',', '.')
        if '.' in n:
            left, right = n.split('.')
            return u'%s %s %s' % (
                self._int2word(int(left)),
                self.pointword,
                self._int2word(int(right))
            )
        else:
            return self._int2cardinal(int(n))

    def _int2word(self, n):
        if n == 0:
            return ZERO[0]

        words = []
        chunks = list(splitbyx(str(n), 3))
        i = len(chunks)
        for x in chunks:
            i -= 1

            if x == 0:
                continue

            n1, n2, n3 = get_digits(x)

            if n3 > 0:
                words.append(HUNDREDS[n3][0])

            if n2 > 1:
                words.append(TWENTIES[n2][0])

            if n2 == 1:
                words.append(TENS[n1][0])
            elif n1 > 0 and not (i > 0 and x == 1):
                words.append(ONES[n1][0])

            if i > 0:
                words.append(self.pluralize(x, THOUSANDS[i]))

        return ' '.join(words)
    
    def _int2cardinal(self, n):
        if n == 0:
            return ZERO[1]

        words = []
        chunks = list(splitbyx(str(n), 3))
        i = len(chunks)
        for j in range(len(chunks)):
            x = chunks[j]
            i -= 1

            is_last_non_zero_chunk = self._is_last_non_zero_chunk(j, chunks)
            is_last_chunk = j == len(chunks) - 1

            if x == 0:
                continue

            n1, n2, n3 = get_digits(x)

            if n3 > 0 and n2 == 0 and n1 == 0 and is_last_chunk:
                words.append(HUNDREDS[n3][1])
            elif n3 > 0:
                words.append(HUNDREDS[n3][0])

            if n2 > 1 and is_last_chunk:
                words.append(TWENTIES[n2][1])
            elif n2 > 1:
                words.append(TWENTIES[n2][0])

            cardinal_ind = None
            if is_last_chunk:
                cardinal_ind = 1
            else:
                cardinal_ind = 0

            if n2 == 1:
                words.append(TENS[n1][cardinal_ind])
            elif n1 > 0 and not (i > 0 and x == 1):
                words.append(ONES[n1][cardinal_ind])

            if i > 0 and is_last_non_zero_chunk:
                words.append(THOUSANDS[1][3])
            elif i > 0:
                words.append(self.pluralize(x, THOUSANDS[i]))

        return ' '.join(words)

    def _is_last_non_zero_chunk(self, ind, chunks):
        if ind == len(chunks) - 1:
            return True
        for i in range(ind + 1, len(chunks)):
            if chunks[i] > 0:
                return False
        return True

