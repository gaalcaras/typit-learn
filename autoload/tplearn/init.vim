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
  nmap <silent><buffer> <leader>qq <plug>(tplearn_record)

  nnoremap <buffer> <plug>(tplearn_edit) :TypitLearnEdit<cr>
  nmap <silent><buffer> <leader>qe <plug>(tplearn_edit)

  nnoremap <buffer> <plug>(tplearn_reload) :TypitLearnReload<cr>
  nmap <silent><buffer> <leader>qr <plug>(tplearn_reload)
endfunction
