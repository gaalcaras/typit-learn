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
