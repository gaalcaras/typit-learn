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
    assert MANAGER._check_abbreviations({'quick': 'WORD'}) == {}

    NV1.nvim.command('let g:tplearn_spellcheck = 1')

    assert 'quick' in MANAGER._check_abbreviations({'quick': 'WORD'}).values()
    assert MANAGER._check_abbreviations({'quickk': 'WORD'}) == {}

def test_replace_existing_typo_same_fix():
    assert MANAGER._rm_existing_fixes({'jmps': 'jumps'}) == {}
    assert MANAGER._rm_existing_fixes({'jmps': 'a'}) == {'jmps': 'a'}
    assert MANAGER._rm_existing_fixes({'xoxo': 'jump'}) == {'xoxo': 'jump'}

def test_replace_existing_typo():
    assert 'jmps' in MANAGER._check_abbreviations({'jmps': 'a'}).values()

def test_replace_existing_fix():
    assert 'jumps' in MANAGER._check_abbreviations({'jumps': 'a'}).values()
    assert MANAGER._check_abbreviations({'ahah': 'a'}) == {}

def test_prompt_answer_no():
    NV2.cleanup()
    NV2.nvim.current.buffer[1] = 'helloworld'

    abb = NV2.play_record(['The quick brown fox HELLO over the lazy dgo',
                           'helloworld3'], feedkeys=['N', 'N'])
    assert abb['jmps'] == 'jumps'
    assert 'helloworld' not in abb
    assert NV2.get_last_message() == '[TypitLearn] No fixes'

    NV2.cleanup()
    NV2.nvim.current.buffer[1] = 'helloworld'

    abb = NV2.play_record(['The quick brown fox HELLO over the lazy dgo',
                           'helloworld3'], feedkeys=['N', 'Y'])
    assert abb['jmps'] == 'jumps'
    assert abb['helloworld'] == 'helloworld3'
    assert NV2.get_last_message() == '[TypitLearn] Recorded "helloworld" => "helloworld3"'

def test_prompt_answer_abort():
    NV2.cleanup()
    NV2.nvim.current.buffer[1] = 'helloworld'

    abb = NV2.play_record(['The quick brown fox HELLO over the lazy dgo',
                           'helloworld4'],
                          feedkeys=['A'])
    assert abb['jmps'] == 'jumps'
    assert abb['helloworld'] == 'helloworld3'
    assert NV2.get_last_message() == '[TypitLearn] No fixes'
