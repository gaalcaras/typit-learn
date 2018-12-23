function! tplearn#init#initTypitLearn() abort
  augroup typitlearn
    autocmd!
    autocmd VimEnter * call s:init()
  augroup END
endfunction

function! s:init()
  let g:tplearn_spellcheck = get(g:, 'tplearn_spellcheck', 0)
  let g:tplearn_log = get(g:, 'tplearn_log', '')
  let g:tplearn_log_level = get(g:, 'tplearn_log_level', 'info')

  call _typitlearn_init()

  call s:init_mappings()
endfunction

function s:init_mappings()
  nnoremap <buffer> <plug>(tplearn_record) :TypitLearnRecord<cr>
  nnoremap <buffer> <plug>(tplearn_edit) :TypitLearnEdit<cr>
  nnoremap <buffer> <plug>(tplearn_reload) :TypitLearnReload<cr>

  nmap <silent><buffer> <leader>q <plug>(tplearn_record)
endfunction
