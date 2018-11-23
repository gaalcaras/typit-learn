from test.utils import NvimInstance

def pytest_sessionfinish(session, exitstatus):
    NV_SOCKET = NvimInstance('socket')

    if NV_SOCKET.nvim:
        try:
            NV_SOCKET.nvim.command('qall!')
        except:
            pass
