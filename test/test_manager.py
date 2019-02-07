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

def test_recording_two_instances():
    NVa = NvimInstance()
    NVb = NvimInstance()
    NVa.cleanup()
    NVb.cleanup()

    # Initialize everything, abbreviations are the same in both instances
    assert NVa.abb == NVb.abb

    # Record new typo in 1, abbreviations are now different
    NVa.play_record(['The quick brown fox jmps over the lazy yoloo'])
    assert NVa.abb != NVb.abb

    # Reload abbreviations in 2, abbrevs are the same again
    time.sleep(0.2)
    NVb.nvim.command('TypitLearnReload')
    assert NVa.abb == NVb.abb

    # Record new typo in 2, then in 1. Abbreviations in 1 should contain all
    # abbreviations from 2 + the new one.
    abb2 = NVb.play_record(['The quick brown fox jmps over the lzy dog'])
    assert NVb.abb['lazy'] == 'lzy'
    time.sleep(0.2)
    NVa.play_record(['The quick brown fox jmps ovar the lazy dog'])
    assert NVa.abb['lazy'] == 'lzy'
    assert NVa.abb['over'] == 'ovar'
    assert 'over' not in NVb.abb

    # Edit the abbrev file by removing the last abbrev, then record a new
    # abbreviation in 2: the deleted abbreviation should have been deleted
    # there as well.
    lines = []
    with open('./test/tmp_abbrev/all.vim', 'r') as tmp:
        lines = tmp.readlines()

    lines = lines[:-1]

    with open('./test/tmp_abbrev/all.vim', 'w') as tmp:
        tmp.writelines(lines)

    NVb.nvim.command('TypitLearnReload')
    assert 'yoloo' not in NVb.abb

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
