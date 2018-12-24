# -*- coding: utf-8 -*-
"""
TypitLearn plugin for Neovim

File: manager.py
Author: Gabriel Alcaras
License: GNU GPL v3
"""

import os
import copy
import platform

from tplearn import logger

class TypitLearnManager(logger.LoggingMixin):

    """Manage files, buffers, etc."""

    def __init__(self, nvim):
        self.nvim = nvim
        self._all_abbrev = {}
        self._tplearn_abbrev = {}

    def _get_tpdir(self):
        tpdir = self.nvim.eval('g:tplearn_dir')

        if tpdir == '':
            home = self.nvim.eval('$HOME')

            if platform.system() == 'Windows':
                tpdir = os.path.join(home, 'vimfiles', 'typitlearn')

            if self.nvim.eval("has('nvim')") == 1:
                xdg_config = self.nvim.eval('$XDG_CONFIG_HOME') or os.path.join(home, '.config')
                tpdir = os.path.join(xdg_config, 'nvim', 'typitlearn')

        tpdir = os.path.expanduser(tpdir)

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
            self.error('No files to load')
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
        self._all_abbrev = {}
        self._tplearn_abbrev = {}

        if files:
            for abbrev_file in files:
                self.info(f'Loading {abbrev_file!r}')
                self.nvim.command(f'silent source {abbrev_file}')

        abbrev_other = self._parse_nvim_abbrev('iabbrev')
        abbrev_tpl = self.nvim.eval('g:tplearn_abbrev')

        self._tplearn_abbrev.update(abbrev_tpl)
        self._all_abbrev.update(abbrev_other)
        self._all_abbrev.update(abbrev_tpl)

        self.debug(f'TPLearn abbrev: {self._tplearn_abbrev}')
        self.debug(f'Other abbrev: {abbrev_other!r}')

    def _get_file_to_edit(self):
        tpdir = self._get_tpdir()
        tpfile = os.path.join(tpdir, 'all.vim')

        return tpfile

    def _prompt(self, msg='', options=None, default=''):
        option = '\n'.join(['&' + o for o in options])
        default = options.index(default)+1

        command = 'let g:tplearn_prompt = confirm("{}", "{}", {})'
        command = command.format(msg, option, default)
        self.nvim.command(command)

        prompt = self.nvim.eval('g:tplearn_prompt')
        return options[prompt-1]

    def _rm_existing_fixes(self, abb=None):
        """Removes existing {typo: fix} items from abbreviation dict"""

        old_typos = self._all_abbrev.keys()
        filtered = {}

        for typo, fix in abb.items():
            if not (typo in old_typos and fix == self._all_abbrev[typo]):
                filtered.update({typo: fix})

        return filtered

    def _check_redundancies(self, typo=None, fix=None):
        """Check abbreviation for redundancies (already used typo, fix already
        exists as a typo).

        :typo: (str)
        :fix: (str)
        :returns: None if no redundancy, string with error message otherwise
        """

        if not typo or not fix:
            return None

        old_typos = self._all_abbrev.keys()

        if typo in old_typos:
            existing = self._all_abbrev[typo]
            message = '\\"{}\\" already expands to \\"{}\\". Expand to \\"{}\\" instead?'
            message = message.format(typo, existing, fix)
        elif fix in old_typos:
            existing = self._all_abbrev[fix]
            message = '\\"{}\\" expands to \\"{}\\". Use as a fix of \\"{}\\" instead?'
            message = message.format(fix, existing, typo)
        else:
            return None

        return message

    def _check_spelling(self, typo=None, fix=None):
        """Check if typo is valid word.

        :typo: (str)
        :fix: (str)
        :returns: None if no redundancy, string with error message otherwise
        """

        if not typo or not self.nvim.eval('g:tplearn_spellcheck'):
            self.debug('yolo')
            return None

        spchk = self.nvim.funcs.spellbadword(typo)

        if spchk[1] == 'bad':
            return None

        if spchk[1] == 'rare':
            diagnostic = 'valid (but rare)'
        elif spchk[1] == 'caps':
            diagnostic = 'valid (if capitalized)'
        elif spchk[1] == 'local':
            diagnostic = 'valid (although only locally)'
        else:
            diagnostic = 'valid'

        msg = f'{typo!r} is a {diagnostic} word in your dictionary. '
        msg += f'Still expand it to {fix!r}?'
        return msg

    def _check_abbreviations(self, abb=None):
        messages = {}
        for typo, fix in abb.items():
            redundancy = self._check_redundancies(typo, fix)
            spellcheck = self._check_spelling(typo, fix)

            if redundancy:
                messages.update({redundancy: typo})

            if spellcheck:
                messages.update({spellcheck: typo})

        self.debug(f'Checking abbreviations: {messages!r}')
        return messages

    def _process_abbreviations(self, abb=None):
        abb = self._rm_existing_fixes(abb)
        filtered = copy.deepcopy(abb)
        messages = self._check_abbreviations(abb)

        for message, typo in messages.items():
            prompt = self._prompt(message, ['Yes', 'No', 'Abort'], 'No')
            self.info(f'User answered {prompt!r}')

            if prompt == 'Abort':
                filtered = {}
                break
            elif prompt == 'No':
                filtered.pop(typo)
            else:
                continue

        return filtered

    def save_abbreviations(self, abbreviations=None):
        """Write abbreviations to files"""

        self.load_abbreviations()
        new_abbrev = self._process_abbreviations(abbreviations)
        self._tplearn_abbrev.update(new_abbrev)

        filepath = self._get_file_to_edit()
        function = 'call tplearn#util#abbreviate("{}", "{}")\n'
        content = ''

        for typo, fix in self._tplearn_abbrev.items():
            content += function.format(typo, fix)

        content = content.encode('utf-8', 'surrogateescape')
        content = content.decode('utf-8', 'replace')

        with open(filepath, 'w+') as tpfile:
            self.info('Write %s abbreviations to %s',
                      len(abbreviations), filepath)
            tpfile.write(content)

        return new_abbrev

    def _parse_nvim_abbrev(self, command):
        output = self.nvim.command_output(command)
        output = output.split('\n')
        output = [l for l in output if ('tplearn#' not in l) and (l != '')]
        output = [l.replace('*', '') for l in output]
        output = [s for l in output for s in l.split()]
        typos = [output[i] for i in range(1, len(output), 3)]
        fixes = [output[i] for i in range(2, len(output), 3)]

        return dict(zip(typos, fixes))

    def edit_file(self):
        """Open abbreviation file"""

        filepath = self._get_file_to_edit()
        self.nvim.command('vsplit {}'.format(filepath))

    def fix_typos(self, abbreviations=None):
        """Search and replace all abbreviations"""
        if not abbreviations:
            return

        for typo, fix in abbreviations.items():
            self.info('Replace %s by %s in buffer', typo, fix)
            self.nvim.command('%s/\<{}\>/{}/ge'.format(typo, fix))
            self.nvim.command('nohl')

    def show_abbrevs(self, abbreviations=None, text=None):
        """Display abbreviations in Neovim message"""

        if not abbreviations:
            self.nvim.call('tplearn#util#message', 'No fixes')
            return

        msg = ''
        for i, (typo, fix) in enumerate(abbreviations.items()):
            if i == 0:
                fmt = '"{}" => "{}"'
            else:
                fmt = ', "{}" => "{}"'

            msg += fmt.format(typo, fix)

        if text:
            msg = '{} {}'.format(text, msg)

        self.nvim.call('tplearn#util#message', msg)
