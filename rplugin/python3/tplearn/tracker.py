# -*- coding: utf-8 -*-
"""
TypitLearn plugin for Neovim

File: tracker.py
Author: Gabriel Alcaras
License: GNU GPL v3
"""

from tplearn import logger

class TypitLearnTracker(logger.LoggingMixin):

    """Track editing changes to create abbreviations from typos and their
    fixes"""

    def __init__(self, log=False):
        self.is_log_enabled = log
        self.abbrev = {}
        self._buffers = {}

        self.debug('Initialize TypitLearnTracker')

    def track_buffer_updates(self, buf, firstline, lastline, linedata):
        """Update 'buffers' based on last buffer changes.

        :buf: [Neovim Buffer] buffer where changes occured
        :firstline: [int] first line of changes
        :lastline: [int] last line of changes
        :linedata: [list] changed lines"""

        self.info('Update buffer %s (add lines %s to %s)',
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

        if (lastline - firstline > 1) or (not linedata):
            self.debug("Changes can't be handled by TypitLearn.")
            return

        new_line = linedata[0]
        old_line = self._buffers[buf.number][firstline]

        old_words = old_line.split(' ')
        new_words = new_line.split(' ')

        for i, word in enumerate(new_words):
            if (word != old_words[i]) or (old_words[i] in self.abbrev):
                self.abbrev.update({old_words[i]: word})

        self.info('abbrev: {}'.format(self.abbrev))

        return
