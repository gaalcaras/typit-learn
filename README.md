# typit-learn

This plugin offers a **mode that records how you fix a typo**. The next time
you make that same typo, it will remember it and fix it automatically.

## What problem does typit-learn solve?

When looking for ways to make text editing more efficient, you often hear about
using abbreviations to automatically correct typos. Briam Moolenaar himself,
the creator of vim, has both [talked](https://youtu.be/p6K4iIMlouI?t=1010) and
[written](https://www.moolenaar.net/habits.html) about that specific piece of
advice.

But I could never make the habit stick. While "using abbreviations" seems
reasonably simple, lazy people like myself feel discouraged just contemplating
all the steps required to make this work consistently:

+ Obviously, I first have to **correct the typo**.
+ Then, I **create an abbreviation**, add it to a file and source the file in
  my `vimrc`.
+ Hey, maybe I made the typo elsewhere but missed it earlier. Better **search
  for that typo and replace it with its fix**.
+ Repeat the first three steps each time I make a typo.
+ Now I have to **maintain a whole file of abbreviations**. Maybe some of them
  introduce some conflicts over time, or perhaps I accidentally overwrite old
  abbreviations I forgot about.
+ Some months later, I find myself with a whole lot of abbreviations and have
  to deal with a lot of unwanted **expansions that I want to undo**, but
  I can't easily do that in vim.

So, yeah, it's doable. It's just not easy enough for me.

What I want is to **fix a typo once, and forget about it forever**. I want vim
to learn from my typos automagically. If I could do some cool
[scikit-learn](https://github.com/scikit-learn/scikit-learn),
machine learning stuff happen, I would. But that's way too much work, so I made
typit-learn instead.

## Features

+ **Typo recording mode**: type <kbd>\<leader>q</kbd>, fix as many typos as you
  want, type <kbd>\<leader>q</kbd> again. Done! All your typos (and their
  respective fixes) have been recorded.
+ **Undo abbreviation expansion**: you can use the regular vim undo commands to
  undo a fix if you want to. Can be disabled with `g:tplearn_undo`.
+ **Maintain a list of typos**: typit-learn will let you know if you
  risk erasing an existing abbreviation, or using a fix that's already known as
  a typo.
+ **Spellchecking**: typit-learn can check whether the typos you're trying to
  fix are actually valid words in your dictionary. Especially useful if a word
  is a typo in one language but is correct in another that you're less familiar
  with. Off by default, you can turn it on with `let g:tplearn_spellcheck = 1`.
+ **Fix all typos at once**: after you record a new typo, typit-learn will
  automatically fix any other occurrence of that typo in the current buffer.

## Installation

Use your favorite plugin manager. For example, with
[vim-plug](https://github.com/junegunn/vim-plug):

```vimrc
Plug 'gaalcaras/typit-learn', { 'do': ':UpdateRemotePlugins' }
```

## Configuration

Variables:

| Variable | Default | Description |
| ----|----|----|
| `g:tplearn_log` | ` ` | Path to log file. Logging disabled if empty. |
| `g:tplearn_log_level` | `info` | Logging level |
| `g:tplearn_dir` | `$HOME/.config/nvim/typitlearn` | Directory to store abbreviation files |
| `g:tplearn_undo` | `1` | Enable undoing typo completion. |
| `g:tplearn_spellcheck` | 0 | Turn on spellchecking on fixes |

Commands:

| Command | Plug | Default | Description |
| ----|----|----|----|
| `:TypitLearnRecord` | `<plug>(tplearn_record)` | <kbd>\<leader>q</kbd> | Toggle recording mode |
| `:TypitLearnEdit` | `<plug>(tplearn_edit)` | | Edit abbreviation file |
| `:TypitLearnReload` | `<plug>(tplearn_reload)` | | Reload all abbreviations |

## Testing

You can run `pytest` at the root of the directory. Some tests need an open
instance of nvim to pass (they'll be skipped otherwise), you can start it with:

```bash
./test/manual_test.sh
```

You can also install the pre commit hook by running the following command at
the root of the directory:

```bash
ln -s ../../test/pre_commit.sh .git/hooks/pre-commit
```
