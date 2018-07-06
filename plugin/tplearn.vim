let g:tplearn_record = get(g:, 'tplearn_record', 0)
let g:tplearn_log = get(g:, 'tplearn_log', 0)
let g:tplearn_init = get(g:, 'tplearn_init', 0)
let g:tplearn_undo = get(g:, 'tplearn_undo', 1)
let g:tplearn_dir = get(g:, 'tplearn_dir', '')

call tplearn#init#initTypitLearn()
