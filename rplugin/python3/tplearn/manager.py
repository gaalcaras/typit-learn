# -*- coding: utf-8 -*-
"""
TypitLearn plugin for Neovim

File: manager.py
Author: Gabriel Alcaras
License: GNU GPL v3
"""

import os
import platform
import time

from tplearn import logger

class TypitLearnManager(logger.LoggingMixin):

    """Manage files, buffers, etc."""

    def __init__(self, nvim, log=False):
        self.nvim = nvim
        self.is_log_enabled = log

        self.debug('Initialize TypitLearnManager')

    def _get_tpdir(self):
        home = self.nvim.eval('$HOME')

        if platform.system() == 'Windows':
            tpdir = os.path.join(home, 'vimfiles', 'typitlearn')

        if self.nvim.eval("has('nvim')") == 1:
            xdg_config = self.nvim.eval('$XDG_CONFIG_HOME') or os.path.join(home, '.config')
            tpdir = os.path.join(xdg_config, 'nvim', 'typitlearn')

        if not os.path.exists(tpdir):
            try:
                self.info('Create %s', tpdir)
                os.makedirs(tpdir)
            except OSError as error:
                self.error(error)
                raise

        return tpdir

    def _get_files_to_load(self):
        tpdir = self._get_tpdir()
        files = os.listdir(tpdir)

        if not files:
            self.debug('No files to load')
            return None

        to_load = []
        for filename in files:
            if 'all.vim' in filename:
                filepath = os.path.join(tpdir, filename)
                to_load.append(filepath)

        return to_load

    def load_abbreviations(self):
        """Source TypitLearn abbreviation files"""

        files = self._get_files_to_load()

        if files:
            for abbrev_file in files:
                self.info('Loading %s', abbrev_file)
                self.nvim.command('silent source {}'.format(abbrev_file))

    def _get_file_to_edit(self):
        tpdir = self._get_tpdir()
        tpfile = os.path.join(tpdir, 'all.vim')

        return tpfile

    def save_abbreviations(self, abbreviations=None):
        """Append abbreviations to files"""

        filepath = self._get_file_to_edit()
        content = ''

        for typo, fix in abbreviations.items():
            content += 'abbreviate {} {}\n'.format(typo, fix)

        with open(filepath, 'a+') as tpfile:
            self.info('Write %s abbreviations to %s',
                      len(abbreviations), filepath)
            tpfile.write(content)

    def fix_typos(self, abbreviations=None):
        """Search and replace all abbreviations"""

        for typo, fix in abbreviations.items():
            self.info('Replace %s by %s in buffer', typo, fix)
            self.nvim.command('%s/{}/{}/ge'.format(typo, fix))
            self.nvim.command('nohl')

    def show_abbrevs(self, abbreviations=None):
        """Display abbreviations in Neovim message"""

        if not abbreviations:
            return

        msg = ''
        for i, (typo, fix) in enumerate(abbreviations.items()):
            if i == 0:
                fmt = '"{}" => "{}"'
            else:
                fmt = ', "{}" => "{}"'

            msg += fmt.format(typo, fix)

        self.nvim.call('tplearn#util#message', msg)

    def clear_msg(self):
        """Clear Neovim message after 2 seconds"""

        time.sleep(2)
        self.nvim.call('tplearn#util#clearmsg')
