function! tplearn#init#initTypitLearn() abort
  augroup typitlearn
    autocmd!
    autocmd VimEnter * call s:init()
  augroup END
endfunction

function! s:init()
  call _typitlearn_load_abbreviations()
endfunction
