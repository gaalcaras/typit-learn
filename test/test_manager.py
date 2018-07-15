# -*- coding: utf-8 -*-
"""
TypitLearn plugin for Neovim

File: test_manager.py.py
Author: Gabriel Alcaras
License: GNU GPL v3
"""

import time
import pytest

from test.utils import NvimInstance
from tplearn import manager #pylint: disable=import-error

NV = NvimInstance()
NV_SOCKET = NvimInstance('socket')
MANAGER = manager.TypitLearnManager(NV.nvim)

RETURN = NV.nvim.replace_termcodes('<return>')

def test_file_to_edit():
    assert MANAGER._get_file_to_edit() == './test/tmp_abbrev/all.vim'

def test_fix_typos():
    NV.cleanup()
    MANAGER.fix_typos({'jmps': 'jumps'})
    assert NV.nvim.buffers[1][4] == 'jumps (should become jumps)'
    assert NV.nvim.buffers[1][5] == 'jmpstest (should stay the same)'
    assert NV.nvim.buffers[1][6] == 'test jumps, test (should become jumps)'

def test_load_abbreviations():
    MANAGER.load_abbreviations()
    assert MANAGER._all_abbrev == {'teh': 'the', 'jmps': 'jumps',
                                   'helloworld': 'helloworld2'}

def test_changing_word():
    NV.cleanup()
    nvim = NV.nvim

    # New fix
    nvim.command('TypitLearnRecord')
    time.sleep(0.1)
    nvim.current.buffer[0] = 'The WORD brown fox jmps over the lazy dgo'
    nvim.command('TypitLearnRecord')
    time.sleep(0.1)
    abbrev = nvim.eval('g:tplearn_abbrev')
    assert abbrev['quick'] == 'WORD'

def test_replace_existing_typo_same_fix():
    NV.cleanup()
    nvim = NV.nvim

    # New fix
    nvim.command('TypitLearnRecord')
    time.sleep(0.1)
    nvim.current.buffer[0] = 'The quick brown fox jumps over the lazy dgo'
    nvim.command('TypitLearnRecord')
    time.sleep(0.1)
    abbrev = nvim.eval('g:tplearn_abbrev')
    assert abbrev['jmps'] == 'jumps'

def test_replace_existing_typo():
    if NV_SOCKET.nvim is None:
        pytest.skip('Could not find nvim socket instance')

    NV_SOCKET.cleanup()
    nvim = NV_SOCKET.nvim

    # New fix
    nvim.command('TypitLearnRecord')
    time.sleep(0.1)
    nvim.current.buffer[0] = 'The quick brown fox WORD over the lazy dgo'
    time.sleep(0.1)
    nvim.command('TypitLearnRecord')
    time.sleep(0.1)
    nvim.input('Y')
    time.sleep(0.1)
    abbrev = nvim.eval('g:tplearn_abbrev')
    assert abbrev['jmps'] == 'WORD'

def test_dont_replace_existing_typo():
    if NV_SOCKET.nvim is None:
        pytest.skip('Could not find nvim socket instance')

    NV_SOCKET.cleanup()
    nvim = NV_SOCKET.nvim

    # New fix
    nvim.command('TypitLearnRecord')
    time.sleep(0.1)
    nvim.current.buffer[0] = 'The quick brown fox HELLO over the lazy dgo'
    time.sleep(0.1)
    nvim.command('TypitLearnRecord')
    time.sleep(0.1)
    nvim.input('N')
    time.sleep(0.1)
    abbrev = nvim.eval('g:tplearn_abbrev')
    assert abbrev['jmps'] == 'WORD'

def test_abort_replace_existing_typo():
    if NV_SOCKET.nvim is None:
        pytest.skip('Could not find nvim socket instance')

    NV_SOCKET.cleanup()
    nvim = NV_SOCKET.nvim

    # New fix
    nvim.command('TypitLearnRecord')
    time.sleep(0.1)
    nvim.current.buffer[0] = 'The WORLD brown fox HELLO over the lazy dgo'
    time.sleep(0.1)
    nvim.command('TypitLearnRecord')
    time.sleep(0.1)
    nvim.input('A')
    time.sleep(0.1)
    abbrev = nvim.eval('g:tplearn_abbrev')
    assert abbrev['jmps'] == 'WORD'
    assert abbrev['quick'] == 'WORD'

def test_replace_existing_fix():
    if NV_SOCKET.nvim is None:
        pytest.skip('Could not find nvim socket instance')

    NV_SOCKET.cleanup()
    nvim = NV_SOCKET.nvim

    # New fix
    nvim.command('TypitLearnRecord')
    time.sleep(0.1)
    nvim.current.buffer[0] = 'The quick brown teh jmps over the lazy dgo'
    time.sleep(0.1)
    nvim.command('TypitLearnRecord')
    time.sleep(0.1)
    nvim.input('Y')
    time.sleep(0.1)
    abbrev = nvim.eval('g:tplearn_abbrev')
    assert abbrev['fox'] == 'teh'

def test_dont_replace_existing_fix():
    if NV_SOCKET.nvim is None:
        pytest.skip('Could not find nvim socket instance')

    NV_SOCKET.cleanup()
    nvim = NV_SOCKET.nvim

    # New fix
    nvim.command('TypitLearnRecord')
    time.sleep(0.1)
    nvim.current.buffer[0] = 'The quick teh fox jmps over the lazy dgo'
    time.sleep(0.1)
    nvim.command('TypitLearnRecord')
    time.sleep(0.1)
    nvim.input('N')
    time.sleep(0.1)
    abbrev = nvim.eval('g:tplearn_abbrev')
    assert ('brown' not in abbrev) is True

def test_abort_replace_existing_fix():
    if NV_SOCKET.nvim is None:
        pytest.skip('Could not find nvim socket instance')

    NV_SOCKET.cleanup()
    nvim = NV_SOCKET.nvim

    # New fix
    nvim.command('TypitLearnRecord')
    time.sleep(0.1)
    nvim.current.buffer[0] = 'The quick teh fox HELLO over the jmps dgo'
    time.sleep(0.1)
    nvim.command('TypitLearnRecord')
    time.sleep(0.1)
    nvim.input('A')
    time.sleep(0.1)
    abbrev = nvim.eval('g:tplearn_abbrev')
    assert ('brown' not in abbrev) is True
    assert ('lazy' not in abbrev) is True
