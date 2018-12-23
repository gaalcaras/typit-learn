# -*- coding: utf-8 -*-
"""
TypitLearn plugin for Neovim

File: tracker.py
Author: Gabriel Alcaras
License: GNU GPL v3
"""

import re

from tplearn import logger

class TypitLearnTracker(logger.LoggingMixin):

    """Track editing changes to create abbreviations from typos and their
    fixes"""

    def __init__(self):
        self._abbrev = {}
        self._buffers = {}

    def track_buffer_updates(self, buf, firstline, lastline, linedata):
        """Update 'buffers' based on last buffer changes.

        :buf: [Neovim Buffer] buffer where changes occured
        :firstline: [int] first line of changes
        :lastline: [int] last line of changes
        :linedata: [list] changed lines"""

        self.debug('Update buffer %s (add lines %s to %s)',
                   buf.number, firstline, lastline)
        changed_lines = dict(zip(range(firstline, lastline+1), linedata))

        if buf.number not in self._buffers:
            self._buffers[buf.number] = {}

        self._buffers[buf.number].update(changed_lines)
        self.debug('Buffers : %s', self._buffers)

        return self._buffers

    def track_replaced_words(self, buf, firstline, lastline, linedata):
        """Keep track of replaced words based on last buffer changes.

        :buf: [Neovim Buffer] buffer where changes occured
        :firstline: [int] first line of changes
        :lastline: [int] last line of changes
        :linedata: [list] changed lines"""

        if (lastline - firstline != 1) or (not linedata) or (len(linedata) > 1):
            self.debug("Changes can't be handled by TypitLearn.")
            return

        new_line = linedata[0]
        old_line = self._buffers[buf.number][firstline]

        word_re = re.compile(r'[^\w]')
        old_words = [w for p in old_line.split(' ') for w in word_re.split(p)]
        new_words = [w for p in new_line.split(' ') for w in word_re.split(p)]

        for i, word in enumerate(old_words):
            if i > len(new_words)-1:
                break

            if (word != new_words[i]) or (word in self._abbrev):
                self._abbrev.update({word: new_words[i]})

        self.debug('abbrev: {}'.format(self._abbrev))

        return

    def abbrev(self):
        """Return filtered abbreviations"""

        abbrev = self._abbrev
        typos = [t for t, f in abbrev.items() if f in (t, '') or t == '']

        for typo in typos:
            abbrev.pop(typo)

        return abbrev

    def reset(self):
        """Reset stored abbreviations"""
        self._abbrev = {}
        self._buffers = {}
