#!/usr/bin/env python
# -*- coding: utf-8 -*-
# アウエ

import difflib
import re
import numpy

class TimestampRecognizer(object):
    '''
    Extract play time from stream.
    '''

    # these represent number of set pixels in each column
    col_to_char = {
       'DGGEEDEJGDD': '0',
       'BBDJJJJBBB': '1',
       'EHHGGEGHGEE': '2',
       'BEEEEEGJHEE': '3',
       'DEEEGEJJJBB': '4',
       'GHHEEEEHHDD': '5',
       'GJJEEEEHHDD': '6',
       'DDDEGGEGEDD': '7',
       'EJJEEEEJJEE': '8',
       'DHHEEEEJJGG': '9',
       'DDDDDDDDKK': 'd',
       'KKBBBBGE': 'h',
       'HHBBHGBBBGG': 'm',
       'DDEEEEEEBB': 's'
    }

    def __init__(self):
        self.timestamp = '0d0h0m0s'
        self.timestamp_s = 0

    def handle(self, data):
        x1, x2, y1, y2 = 232, 231+147, 9, 9 + 25
        timestamp = data['frame'][y1:y2, x1:x2]
        col_sum = (timestamp > 150).sum(axis=0)  # Sum bright pixels in each column
        col_str = (col_sum *.5 + ord('A')).astype(numpy.int8).tostring()  #
        strings = re.split(r'A*', col_str)  # Segment by black columns
        try:
            result = self.convert(strings)
            days, hours, minutes, seconds = map(int, re.split('[dhms]', result)[:-1])
            self.timestamp = result
            self.timestamp_s = ((days * 24 + hours) * 60 + minutes) * 60 + seconds
        except (ValueError, IndexError):
            pass    # invalid timestamp (ocr failed)
        finally:
            data['timestamp'] = self.timestamp
            data['timestamp_s'] = self.timestamp_s

    def convert(self, strings):
        col_to_char = self.col_to_char

        def match(x):
            if x in col_to_char:
                return col_to_char[x]
            close = difflib.get_close_matches(x, col_to_char, cutoff=.6)
            return col_to_char[close[0]]

        return ''.join(match(x) for x in strings if x)
