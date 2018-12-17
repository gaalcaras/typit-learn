# -*- coding: utf-8 -*-
"""
TypitLearn plugin for Neovim

File: test_manager.py.py
Author: Gabriel Alcaras
License: GNU GPL v3
"""

from test.utils import NvimInstance
from tplearn import manager #pylint: disable=import-error

NV1 = NvimInstance()
NV2 = NvimInstance('socket')
MANAGER = manager.TypitLearnManager(NV1.nvim)

def test_file_to_edit():
    assert MANAGER._get_file_to_edit() == './test/tmp_abbrev/all.vim'

def test_fix_typos():
    NV1.cleanup()
    MANAGER.fix_typos({'jmps': 'jumps'})
    assert NV1.nvim.buffers[1][4] == 'jumps (should become jumps)'
    assert NV1.nvim.buffers[1][5] == 'jmpstest (should stay the same)'
    assert NV1.nvim.buffers[1][6] == 'test jumps, test (should become jumps)'

def test_load_abbreviations():
    MANAGER.load_abbreviations()
    assert MANAGER._all_abbrev == {'teh': 'the', 'jmps': 'jumps',
                                   'helloworld': 'helloworld2'}
    assert MANAGER._tplearn_abbrev == {'teh': 'the', 'jmps': 'jumps'}

def test_changing_word():
    NV1.cleanup()

    abb = NV1.play_record(['The WORD brown fox jmps over the lazy dgo'])
    assert abb['quick'] == 'WORD'
    assert NV1.get_last_message() == '[TypitLearn] Recorded "quick" => "WORD"'

def test_fix_valid_word():
    NV1.cleanup()
    NV1.nvim.command('let g:tplearn_spellcheck = 1')

    abb = NV1.play_record(['The WORD brown fox jmps over the lazy dgo'])
    assert abb['quick'] == 'WORD'
    assert NV1.get_last_message() == '[TypitLearn] No fixes'

def test_replace_existing_typo_same_fix():
    NV1.cleanup()

    abb = NV1.play_record(['The quick brown fox jumps over the lazy dgo'])
    assert abb['jmps'] == 'jumps'
    assert NV1.get_last_message() == '[TypitLearn] No fixes'

def test_replace_existing_typo():
    NV2.cleanup()

    abb = NV2.play_record(['The quick brown fox WORD over the lazy dgo'],
                          feedkeys=['Y'])
    assert abb['jmps'] == 'WORD'
    assert NV2.get_last_message() == '[TypitLearn] Recorded "jmps" => "WORD"'

def test_dont_replace_existing_typo():
    NV2.cleanup()
    NV2.nvim.current.buffer[1] = 'helloworld'

    abb = NV2.play_record(['The quick brown fox HELLO over the lazy dgo',
                           'helloworld3'], feedkeys=['N', 'N'])
    assert abb['jmps'] == 'WORD'
    assert 'helloworld' not in abb
    assert NV2.get_last_message() == '[TypitLearn] No fixes'

def test_abort_replace_existing_typo():
    NV2.cleanup()
    NV2.nvim.current.buffer[1] = 'helloworld'

    abb = NV2.play_record(['The quick brown fox HELLO over the lazy dgo',
                           'helloworld3'],
                          feedkeys=['A'])
    assert abb['jmps'] == 'WORD'
    assert 'helloworld' not in abb
    assert NV2.get_last_message() == '[TypitLearn] No fixes'

def test_replace_existing_fix():
    NV2.cleanup()

    abb = NV2.play_record(['The quick brown teh jmps over the lazy dgo'],
                          feedkeys=['Y'])
    assert abb['fox'] == 'teh'
    assert NV2.get_last_message() == '[TypitLearn] Recorded "fox" => "teh"'

def test_dont_replace_existing_fix():
    NV2.cleanup()

    abb = NV2.play_record(['The quick teh fox jmps over the lazy dgo'],
                          feedkeys=['N'])
    assert 'brown' not in abb
    assert NV2.get_last_message() == '[TypitLearn] No fixes'

def test_abort_replace_existing_fix():
    NV2.cleanup()

    abb = NV2.play_record(['The quick teh fox HELLO over the jmps dgo'],
                          feedkeys=['A'])
    assert 'brown' not in abb
    assert 'lazy' not in abb

def test_fix_valid_word_prompt():
    NV2.cleanup()
    NV2.nvim.command('let g:tplearn_spellcheck = 1')

    abb = NV2.play_record(['The quick HELLO fox jmps over the WORLD dgo'],
                          feedkeys=['N', 'Y'])
    assert 'brown' not in abb
    assert abb['lazy'] == 'WORLD'
