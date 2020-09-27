def check_varlist(varlist,nproc):
  nv = int(len(varlist)/nproc)
  create_new = False
  if not(nv==len(varlist)/nproc):
    nv += 1
    create_new = True
  if create_new:
    rest = nv*proc - len(varlist)
    for j in range(rest):
      varlist.append(None)
  return varlist
