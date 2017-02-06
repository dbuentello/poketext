#!/usr/bin/env python

# an example consumer of the poketext module, used by poke.ifies.com
import sys; sys.path += ['..']  # hack to let us import it as a module from the same directory

import json
import time

import poketext
import redis


r = redis.Redis()

class FilteredPrinter(object):
    def printer(self, data):
        if data['dithered_delta'] == '':
            return
        data.pop('frame')
        data.pop('screen')
        r.publish('pokemon.streams.frames', json.dumps(data))
        print data['timestamp'], '%5d'%len(data['dithered_delta'])

class DialogPusher(object):
    def handle(self, text, lines, timestamp):
        print timestamp, text
        r.publish('pokemon.streams.dialog', json.dumps({'time': timestamp, 'text': text, 'lines': lines}))


box_reader = poketext.BoxReader()
box_reader.add_dialog_handler(DialogPusher().handle)

proc = poketext.StreamProcessor()
proc.add_handler(poketext.ScreenCompressor(fname='frames/frames.%y%m%d-%H%M.raw.gz').handle)
proc.add_handler(poketext.StringDeltaCompressor('dithered').handle)
proc.add_handler(box_reader.handle)
proc.add_handler(FilteredPrinter().printer)
proc.add_handler(poketext.LogHandler('text', 'frames.log').handle)
proc.run()
