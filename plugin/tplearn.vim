let g:tplearn_record = get(g:, 'tplearn_record', 0)
let g:tplearn_log = get(g:, 'tplearn_log', 0)
let g:tplearn_init = get(g:, 'tplearn_init', 0)

nnoremap <buffer> <plug>(tplearn_record) :TypitLearnRecord<cr>
nmap <silent><buffer> <leader>q <plug>(tplearn_record)

call tplearn#init#initTypitLearn()
