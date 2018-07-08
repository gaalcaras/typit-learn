# -*- coding: utf-8 -*-
"""
TypitLearn plugin for Neovim

File: testutils.py
Author: Gabriel Alcaras
License: GNU GPL v3
"""

import tempfile

from neovim import attach

nvim = attach('child', argv=["/bin/env", "nvim", "-u", "test/minvimrc",
                             "--embed"])

cleanup_func = ''':function BeforeEachTest(file)
    %bwipeout!
    execute "edit " . a:file
endfunction
'''

nvim.input(cleanup_func)

TESTFILE = open('test/test.txt', 'r')
TEST = TESTFILE.readlines()
TESTFILE.close()

def mktemp_with_file():
    tmp_path = tempfile.mkstemp()[1]
    tmp = open(tmp_path, 'w')
    tmp.writelines(TEST)
    tmp.close()

    return tmp_path

def cleanup():
    tmp = mktemp_with_file()

    command = 'call BeforeEachTest("{}")'.format(tmp)
    nvim.command(command)

class NvimTestBuffer(object):

    def __init__(self, content, number=1):
        self._content = content
        self.number = number

    def __getitem__(self, idx):
        return self._content[idx]
