# -*- coding: utf-8 -*-
"""
TypitLearn plugin for Neovim

File: test_tracker.py
Author: Gabriel Alcaras
License: GNU GPL v3
"""

from collections import OrderedDict
from tplearn import tracker #pylint: disable=import-error
from test.utils import NvimTestBuffer

TRACKER = tracker.TypitLearnTracker()


def test_tracker_one_word_change():
    buf = NvimTestBuffer(['The quick brown fox jmps over the lazy dgo'])
    changes = [buf, 0, 1, buf[:]]
    TRACKER.track_buffer_updates(*changes)

    buf = NvimTestBuffer(['The quick brown fox jmps over the lazy dog'])
    changes = [buf, 0, 1, buf[:]]
    TRACKER.track_replaced_words(*changes)

    assert TRACKER.abbrev() == {'dgo': 'dog'}

def test_tracker_delete_word():
    buf = NvimTestBuffer(['The quick brown fox jmps over the lazy '])
    changes = [buf, 0, 1, buf[:]]
    TRACKER.track_replaced_words(*changes)

    assert TRACKER.abbrev() == {}

    buf = NvimTestBuffer(['The quick brown fox jmps over the lazy'])
    changes = [buf, 0, 1, buf[:]]
    TRACKER.track_replaced_words(*changes)

    assert TRACKER.abbrev() == {}

    buf = NvimTestBuffer(['The quick brown fox jmps over the lazy dog'])
    changes = [buf, 0, 1, buf[:]]
    TRACKER.track_replaced_words(*changes)

    assert TRACKER.abbrev() == {'dgo': 'dog'}

def test_tracker_same_word():
    buf = NvimTestBuffer(['The quick brown fox jmps over the lazy dgo'])
    changes = [buf, 0, 1, buf[:]]
    TRACKER.track_replaced_words(*changes)

    assert TRACKER.abbrev() == {}

    buf = NvimTestBuffer(['The quick brown fox jmps over the lazy dog'])
    changes = [buf, 0, 1, buf[:]]
    TRACKER.track_replaced_words(*changes)

    assert TRACKER.abbrev() == {'dgo': 'dog'}

def test_tracker_add_word():
    TRACKER.reset()

    buf = NvimTestBuffer(['The quick brown fox jmps over the lazy dgo'])
    changes = [buf, 0, 1, buf[:]]
    TRACKER.track_buffer_updates(*changes)

    changes = [buf, 0, 1, ['The quick brown fox jmps over the lazy dgo stuff']]
    TRACKER.track_replaced_words(*changes)
    assert TRACKER.abbrev() == {}

    TRACKER.reset()

def test_tracker_add_word_trailing_space():
    buf = NvimTestBuffer(['The quick brown fox jmps over the lazy dgo '])
    changes = [buf, 0, 1, buf[:]]
    TRACKER.track_buffer_updates(*changes)

    changes = [buf, 0, 1, ['The quick brown fox jmps over the lazy dgo stuff']]
    TRACKER.track_replaced_words(*changes)
    assert TRACKER.abbrev() == {}

def test_tracker_add_word_next_punctuation():
    buf = NvimTestBuffer(['The quick brown fox jmps. Over the lazy dgo!'])
    changes = [buf, 0, 1, buf[:]]
    TRACKER.track_buffer_updates(*changes)

    changes = [buf, 0, 1, ['The quick brown fox jumps. Over the lazy dog!']]
    TRACKER.track_replaced_words(*changes)
    assert TRACKER.abbrev() == {'jmps': 'jumps', 'dgo': 'dog'}

def test_tracker_add_word_with_dash():
    buf = NvimTestBuffer(['The quick brown fox jmps. Over the lazy-dgo!'])
    changes = [buf, 0, 1, buf[:]]
    TRACKER.track_buffer_updates(*changes)

    changes = [buf, 0, 1, ['The quick brown fox jumps. Over the lazy-dog!']]
    TRACKER.track_replaced_words(*changes)
    assert TRACKER.abbrev() == {'jmps': 'jumps', 'dgo': 'dog'}

def test_tracker_delete_lines():
    TRACKER.reset()
    buf = NvimTestBuffer(['The quick brown fox jmps over the lazy dgo stuff',
                          'This is another test',
                          'This is another test',
                          'This is another test'])
    changes = [buf, 0, 3, buf[:]]
    TRACKER.track_buffer_updates(*changes)

    changes = [buf, 2, 3, []] # Delete last line
    TRACKER.track_replaced_words(*changes)
    assert TRACKER.abbrev() == {}

    changes = [buf, 0, 2, []] # Delete two last lines
    TRACKER.track_replaced_words(*changes)
    assert TRACKER.abbrev() == {}

def test_tracker_yank_lines():
    TRACKER.reset()
    buf = NvimTestBuffer(['The quick brown fox jmps over the lazy dgo stuff',
                          'This is another test',
                          ''])

    changes = [buf, 0, 1, buf[:]]
    TRACKER.track_buffer_updates(*changes)

    # Yanking 1 line after the first one
    buf = NvimTestBuffer(['Yet again some dummy text'])
    changes = [buf, 1, 1, buf[:]]
    TRACKER.track_replaced_words(*changes)

    assert TRACKER.abbrev() == {}

    # Yanking 2 lines after the first one
    buf = NvimTestBuffer(['Hello world', 'Hello world'])
    changes = [buf, 1, 1, buf[:]]
    TRACKER.track_replaced_words(*changes)

    assert TRACKER.abbrev() == {}

def test_order_abbrev():
    TRACKER.reset()

    buf = NvimTestBuffer(['The quick brown fox jmps over the lazy dgo'])
    changes = [buf, 0, 1, buf[:]]
    TRACKER.track_buffer_updates(*changes)

    changes = [buf, 0, 1, ['The quick brown fox jmps over the lazy dag']]
    TRACKER.track_replaced_words(*changes)
    assert TRACKER.abbrev() == OrderedDict({'dgo': 'dag'})

    changes = [buf, 0, 1, ['The quick brown fox jumps over the lazy dag']]
    TRACKER.track_replaced_words(*changes)
    assert TRACKER.abbrev() == OrderedDict({'jmps': 'jumps',
                                            'dgo': 'dag'})

    changes = [buf, 0, 1, ['The quick brown fox jumps over the lazy dog']]
    TRACKER.track_replaced_words(*changes)
    assert TRACKER.abbrev() == OrderedDict({'dgo': 'dog',
                                            'jmps': 'jumps'})

    TRACKER.reset()
