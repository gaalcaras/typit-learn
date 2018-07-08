# -*- coding: utf-8 -*-
"""
TypitLearn plugin for Neovim

File: test_manager.py.py
Author: Gabriel Alcaras
License: GNU GPL v3
"""

from test.utils import nvim, cleanup
from tplearn import manager #pylint: disable=import-error

MANAGER = manager.TypitLearnManager(nvim)

def test_file_to_edit():
    assert MANAGER._get_file_to_edit() == './test/abbrev/all.vim'

def test_fix_typos():
    cleanup()
    MANAGER.fix_typos({'jmps': 'jumps'})
    assert nvim.buffers[1][4] == 'jumps (should become jumps)'
    assert nvim.buffers[1][5] == 'jmpstest (should stay the same)'
    assert nvim.buffers[1][6] == 'test jumps, test (should become jumps)'

def test_load_abbreviations():
    MANAGER.load_abbreviations()
    assert MANAGER._all_abbrev == {'teh': 'the', 'jmps': 'jumps',
                                   'helloworld': 'helloworld2'}
