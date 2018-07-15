#!/bin/bash

tmpfile=$(mktemp "/tmp/tpltestXXXXXXXXXX")
cat test/test.txt > "$tmpfile"
cp -r test/abbrev test/tmp_abbrev

nvim +UpdateRemotePlugins +qall
NVIM_LISTEN_ADDRESS=/tmp/nvim_tplearn nvim -u test/minvimrc "$tmpfile"

rm "$tmpfile"
rm -r "test/tmp_abbrev"
