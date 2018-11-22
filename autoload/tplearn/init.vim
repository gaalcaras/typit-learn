function! tplearn#init#initTypitLearn() abort
  augroup typitlearn
    autocmd!
    autocmd VimEnter * call s:init()
  augroup END
endfunction

function! s:init()
  call _typitlearn_load_abbreviations()
  call s:init_mappings()
endfunction

function s:init_mappings()
  nnoremap <buffer> <plug>(tplearn_record) :TypitLearnRecord<cr>
  nnoremap <buffer> <plug>(tplearn_edit) :TypitLearnEdit<cr>
  nnoremap <buffer> <plug>(tplearn_reload) :TypitLearnReload<cr>

  nmap <silent><buffer> <leader>q <plug>(tplearn_record)
endfunction
