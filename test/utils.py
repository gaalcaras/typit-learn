# -*- coding: utf-8 -*-
"""
TypitLearn plugin for Neovim

File: testutils.py
Author: Gabriel Alcaras
License: GNU GPL v3
"""

from shutil import copyfile, rmtree
import os
import tempfile
import textwrap
import time

import pytest

from neovim import attach

def mktmp_abbrev():
    if os.path.exists(os.path.join('test', 'tmp_abbrev')):
        rmtree(os.path.join('test', 'tmp_abbrev'))

    os.makedirs(os.path.join('test', 'tmp_abbrev'))
    copyfile(os.path.join('test', 'abbrev', 'all.vim'),
             os.path.join('test', 'tmp_abbrev', 'all.vim'))

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
    mktmp_abbrev()

    return tmp

class NvimInstance(object):
    def __init__(self, attach_type='child'):
        self._tmp = gen_tmp_files()
        self.nvim = self._attach(attach_type)

        if self.nvim is None:
            return

    def _attach(self, attach_type):
        if attach_type == 'child':
            return attach('child', argv=["/bin/env", "nvim", "-u",
                                         "test/minvimrc", "--embed"])

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
        endfunction
        ''')

        self.nvim.command(cleanup_func)
        self.nvim.command('call BeforeEachTest("{}")'.format(self._tmp))

    def get_last_message(self):
        return self.nvim.command_output('messages').split('\n')[-1]

    def play_record(self, changes=None, feedkeys=None):
        time_delay = 0.1
        changes = [] if changes is None else changes
        self.nvim.command('TypitLearnRecord')
        time.sleep(time_delay)

        for numline, line in enumerate(changes):
            self.nvim.current.buffer[numline] = line

        time.sleep(time_delay)
        self.nvim.command('TypitLearnRecord')

        if feedkeys:
            for key in feedkeys:
                time.sleep(time_delay)
                self.nvim.input(key)

        time.sleep(time_delay)
        return self.nvim.eval('g:tplearn_abbrev')

class NvimTestBuffer(object):

    def __init__(self, content, number=1):
        self._content = content
        self.number = number

    def __getitem__(self, idx):
        return self._content[idx]
