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

def test_load_abbreviations():
    cleanup()
    MANAGER.load_abbreviations()
    assert MANAGER._all_abbrev == {'teh': 'the', 'jmps': 'jumps',
                                   'helloworld': 'helloworld2'}
