# -*- coding: utf-8 -*-
"""
TypitLearn plugin for Neovim

File: test_tracker.py
Author: Gabriel Alcaras
License: GNU GPL v3
"""

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

    assert TRACKER.abbrev == {'dgo': 'dog'}
