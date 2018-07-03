#!/bin/bash

tmpfile=$(mktemp "/tmp/tpltestXXXXXXXXXX")
cat test/test.txt > "$tmpfile"

nvim +UpdateRemotePlugins +qall
nvim -u test/minvimrc "$tmpfile"

rm "$tmpfile"
