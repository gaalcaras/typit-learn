from shutil import copyfile, rmtree
import os
from test.utils import NvimInstance

def pytest_sessionstart(session):
    if os.path.exists(os.path.join('test', 'tmp_abbrev')):
        rmtree(os.path.join('test', 'tmp_abbrev'))

    os.makedirs(os.path.join('test', 'tmp_abbrev'))
    copyfile(os.path.join('test', 'abbrev', 'all.vim'),
             os.path.join('test', 'tmp_abbrev', 'all.vim'))

def pytest_sessionfinish(session, exitstatus):
    NV_SOCKET = NvimInstance('socket')

    if NV_SOCKET.nvim:
        try:
            NV_SOCKET.nvim.command('qall!')
        except:
            pass

    if os.path.exists(os.path.join('test', 'tmp_abbrev')):
        rmtree(os.path.join('test', 'tmp_abbrev'))
