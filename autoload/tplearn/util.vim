function! tplearn#util#message(msg)
  if mode() == 'i'
    set nosmd
  endif

  echohl ModeMsg
  echomsg "[TypitLearn] " . a:msg
  echohl None
endfunction

function! tplearn#util#clearmsg()
  echo
endfunction

function! tplearn#util#ciw(replacement)
  execute 'normal! xciw' . a:replacement
endfunction

function! tplearn#util#abbreviate(typo, fix)
  let l:command = 'iabbrev ' . a:typo . ' '

  if g:tplearn_undo
    let l:command = l:command . a:typo .
          \ ' <c-g>u<c-o>:call tplearn#util#ciw("' .
          \ a:fix . '")<cr>'
  else
    let l:command = l:command . a:fix
  endif

  silent! execute l:command
  let g:tplearn_abbrev[a:typo] = a:fix
endfunction

" The 'tp_record' event is only used for the test suite
function! tplearn#util#notify(value)
  call rpcnotify(0, 'tp_record', a:value)
endfunction
