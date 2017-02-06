#!/usr/bin/env python
# -*- coding: utf-8 -*-
# アウエ

# an example consumer of the pokr module, used by poke.ifies.com
import sys; sys.path += ['..']  # hack to let us import it as a module from the same directory

import json
import time

import poketext
import redis
import dialog

r = redis.Redis()

from datetime import datetime, timedelta
diff = datetime.utcnow() - datetime(2016, 10, 9, 21, 0, 0)
manualtimestamp =  "%sd%sh%sm%ss" % (diff.days, (diff.seconds / 3600), ((diff.seconds / 60) % 60), (diff.seconds % 60))

class FilteredPrinter(object):
    def printer(self, data):
        if data['dithered_delta'] == '':
            return
        data.pop('frame')
        data.pop('screen')
        #r.publish('pokemon.streams.frames', json.dumps(data))
        #print data['timestamp'], '%5d'%len(data['dithered_delta'])
        #print "manualtimestamp, '%5d'%len(data['dithered_delta'])
        print "0d0h0m0s", '%5d'%len(data['dithered_delta'])

class DialogPusher(object):
    def __init__(self):
        #self.tracker = dialog.BattleState('blah wants to fight', '')
        self.tracker = dialog.BattleState('blah wants to fight')
    #def handle(self, text, lines, timestamp):
    def handle(self, text, lines):
        #print timestamp, text
	#print timestamp, unicode(str(self.tracker.annotate(text, lines)), 'utf-8')
	#print timestamp, str(self.tracker.annotate(text, lines).encode('utf-8'))
	print '0d0h0m0s', str(self.tracker.annotate(text, lines).encode('utf-8'))

	#print timestamp, text, lines
        #r.publish('pokemon.streams.dialog', json.dumps({'time': manualtimestamp, 'text': text, 'lines': lines}))
	# print str(self.tracker.annotate(text, lines).encode('utf-8'))
        #r.publish('pokemon.streams.dialog', json.dumps({'time': manualtimestamp, 'text': str(self.tracker.annotate(text, lines).encode('utf-8')), 'lines': lines}))
        r.publish('pokemon.streams.dialog', json.dumps({'time': manualtimestamp, 'text': self.tracker.annotate(text, lines).encode('utf-8'), 'lines': lines}))
	with open('gameoutput.txt', 'a') as file:
		file.write(manualtimestamp + " " + self.tracker.annotate(text, lines).encode('utf-8') + "\n")
        #r.publish('pokemon.streams.dialog', json.dumps({'text': text, 'lines': lines}))

box_reader = poketext.BoxReader()
box_reader.add_dialog_handler(DialogPusher().handle)

proc = poketext.StreamProcessor()
#proc.add_handler(poketext.ScreenCompressor(fname='frames/frames.%y%m%d-%H%M.raw.gz').handle)
proc.add_handler(poketext.StringDeltaCompressor('dithered').handle)
proc.add_handler(box_reader.handle)
proc.add_handler(FilteredPrinter().printer)
proc.add_handler(poketext.LogHandler('text', 'frames.log').handle)
proc.run()
