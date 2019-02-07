# -*- coding: utf-8 -*-
"""
TypitLearn plugin for Neovim

File: testutils.py
Author: Gabriel Alcaras
License: GNU GPL v3
"""

import tempfile
import textwrap

import pytest

from neovim import attach

def mktemp_with_lines(lines):
    tmp_path = tempfile.mkstemp()[1]
    tmp = open(tmp_path, 'w')
    tmp.writelines(lines)
    tmp.close()

    return tmp_path

def gen_tmp_files():
    test_f = open('test/test.txt', 'r')
    test = test_f.readlines()
    test_f.close()

    tmp = mktemp_with_lines(test)

    return tmp

class NvimInstance(object):
    def __init__(self, attach_type='child'):
        self._tmp = gen_tmp_files()
        self.nvim = self._attach(attach_type)

        if self.nvim is None:
            return

        self.abb = Abbreviation(self.nvim)

    def _attach(self, attach_type):
        if attach_type == 'child':
            nvim = attach('child', argv=["/bin/env", "nvim", "-u",
                                         "test/minvimrc", "--embed"])
            nvim.ui_attach(100, 100)
            return nvim

        try:
            nvim = attach('socket', path='/tmp/nvim_tplearn')
        except FileNotFoundError:
            print('\nCould not find NVIM process. Did you start a NVIM '
                  'instance at /tmp/nvim_tplearn?')
            nvim = None

        return nvim

    def cleanup(self):
        if self.nvim is None:
            pytest.skip('Could not find nvim socket instance')

        cleanup_func = textwrap.dedent(''':function! BeforeEachTest(file)
            %bwipeout!
            execute "edit " . a:file
            let g:tplearn_abbrev = {}
            let g:tplearn_spellcheck = 0
            source test/minvimrc
        endfunction
        ''')

        self.nvim.command(cleanup_func)
        self.nvim.command('call BeforeEachTest("{}")'.format(self._tmp))

    def get_last_message(self):
        return self.nvim.command_output('messages').split('\n')[-1]

    def wait_for_event(self, event, value=None):
        no_match = True
        while no_match:
            cur_event = self.nvim.next_message()

            if not cur_event:
                continue

            if cur_event[1] == event:
                if value and not cur_event[2][0] == value:
                    continue

                no_match = False
                return cur_event

    def play_record(self, changes=None, feedkeys=None):
        changes = [] if changes is None else changes
        def sequence(feedkeys):
            self.nvim.command('TypitLearnRecord')
            yield self.wait_for_event('tp_record', 'start')

            for numline, line in enumerate(changes):
                self.nvim.current.buffer[numline] = line

            self.nvim.command('TypitLearnRecord')

            if feedkeys:
                for key in feedkeys:
                    yield self.wait_for_event('tp_record', 'ask')
                    self.nvim.input(key)

            yield self.wait_for_event('tp_record', 'stop')

        self.nvim.subscribe('tp_record')
        for _ in sequence(feedkeys):
            pass

        self.nvim.unsubscribe('tp_record')

class Abbreviation:
    def __init__(self, nvim):
        self.abb = nvim.eval('g:tplearn_abbrev')
        self.nvim = nvim

    def __getitem__(self, item):
        self.abb = self.nvim.eval('g:tplearn_abbrev')
        return self.abb[item]

    def __contains__(self, item):
        return item in self.abb

    def __repr__(self):
        return '<Abbreviation ' + repr(self.abb) + '>'

    def __eq__(self, other):
        self.abb = self.nvim.eval('g:tplearn_abbrev')
        other.abb = other.nvim.eval('g:tplearn_abbrev')

        return self.abb == other.abb

class NvimTestBuffer(object):

    def __init__(self, content, number=1):
        self._content = content
        self.number = number

    def __getitem__(self, idx):
        return self._content[idx]
