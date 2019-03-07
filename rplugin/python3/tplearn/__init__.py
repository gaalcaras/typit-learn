# -*- coding: utf-8 -*-
"""
TypitLearn plugin for pynvim

File: __init__.py
Author: Gabriel Alcaras
License: GNU GPL v3
"""

import numpy as np
import pynvim

from tplearn import logger
from tplearn.manager import TypitLearnManager
from tplearn.tracker import TypitLearnTracker

@pynvim.plugin
class TypitLearn(logger.LoggingMixin):

    """Main plugin class to interact with pynvim"""

    def __init__(self, nvim):
        self.nvim = nvim

        self.manager = TypitLearnManager(self.nvim)
        self.tracker = TypitLearnTracker()

        self._record_first = True

    @pynvim.function('_typitlearn_init')
    def _init(self, *args):
        def init_functions():
            self._init_log()
            yield
            self.manager.load_abbreviations()
            yield

        for _ in init_functions():
            pass

    def _init_log(self, *args):
        try:
            log_file = self.nvim.eval('g:tplearn_log')
            log_level = self.nvim.eval('g:tplearn_log_level')
            nvim_id = self.nvim.channel_id
        except pynvim.NvimError:
            return

        if log_file and log_level:
            self._setup_log(log_file, log_level, nvim_id)

    @pynvim.rpc_export('nvim_buf_lines_event')
    def _on_buf_lines_event(self, *args):
        buf = args[0]
        firstline = args[2]
        # When lastline is -1, use last line number instead
        lastline = len(buf[:])-1 if args[3] == -1 else args[3]
        linedata = args[4]

        self.debug('Changed lines: {bufnum: %s, firstline: %s, lastline: %s, '
                   'linedata: %s',
                   buf.number, firstline, lastline, linedata)

        if self._record_first:
            self.tracker.track_buffer_updates(buf, firstline, lastline,
                                              linedata)
            self._record_first = False

        self.tracker.track_replaced_words(buf, firstline, lastline, linedata)
        self.manager.show_abbrevs(self.tracker.abbrev(), 'Recording:')

    @pynvim.rpc_export('nvim_buf_changedtick_event')
    def _on_buf_changedtick_event(self, *args):
        return

    @pynvim.rpc_export('nvim_buf_detach_event')
    def _on_nvim_buf_detach_event(self, *args):
        return

    @pynvim.command('TypitLearnRecord', nargs=0)
    def _toggle_record(self):
        if self.nvim.eval('g:tplearn_record') == 0:
            self._record_start()
            self.nvim.command('call tplearn#util#notify("start")')
            self.nvim.vars['tplearn_record'] = 1
        else:
            self._record_stop()
            self.nvim.command('call tplearn#util#notify("stop")')
            self.nvim.vars['tplearn_record'] = 0

    @pynvim.command('TypitLearnEdit', nargs=0)
    def _edit_abbrev_file(self):
        self.manager.edit_file()

    @pynvim.command('TypitLearnUndo', nargs=0)
    def _undo_last(self):
        self.manager.rm_last_abbrevs()

    @pynvim.command('TypitLearnReload', nargs=0)
    def _reload(self):
        self.manager.load_abbreviations()

    def _record_start(self):
        self.info('Start recording')
        self.nvim.request('nvim_buf_attach',
                          self.nvim.current.buffer.number,
                          True,
                          {})
        self.nvim.call('tplearn#util#message', 'Recording')

    def _record_stop(self):
        self.info('Stop recording')
        self.nvim.request('nvim_buf_detach', self.nvim.current.buffer.number)
        self._learn()

        self.tracker.reset()
        self._record_first = True

    def _learn(self):
        if not self.tracker.abbrev:
            return

        saved = self.manager.save_abbreviations(self.tracker.abbrev())
        self.manager.show_abbrevs(saved, 'Recorded:')
        self.manager.fix_typos(saved)
        self.manager.load_abbreviations()
