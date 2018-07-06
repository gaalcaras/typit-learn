# -*- coding: utf-8 -*-
"""
TypitLearn plugin for Neovim

File: testutils.py
Author: Gabriel Alcaras
License: GNU GPL v3
"""


class NvimTestBuffer(object):

    def __init__(self, content, number=1):
        self._content = content
        self.number = number

    def __getitem__(self, idx):
        return self._content[idx]
