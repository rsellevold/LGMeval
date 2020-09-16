import os
from mpi4py import MPI
import yaml
from cdo import Cdo

cdo = Cdo()

# This function ensures that varlist is an integer scalar
# of the numbers of processes, by appending None.
def check_varlist(varlist,nproc):
    nv = int(len(varlist)/nproc)
    create_new = False
    if not(nv==len(varlist)/nproc):
        nv += 1
        create_new = True
    if create_new:
        rest = nv*nproc - len(varlist)
        for j in range(rest):
            varlist.append(None)
    return varlist



def mon2ann(fdir, var):
    outdir = f"{fdir[:-7]}/annavg"
    check_outdir = os.path.exists(outdir)
    if not(check_outdir):
        os.system(f"mkdir -p {outdir}")
    cdo.yearavg(input=f"{fdir}/{var}", output=f"{outdir}/{var}")



def main():
    # Initialize MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Get config
    with open("config.yml","r") as f:
        config = yaml.safe_load(f)

    fdir = f"{config['run']['folder']}/{config['run']['name']}/atm/hist/monavg"
    varlist = os.popen(f"ls {fdir}").read().split("\n")[:-1]
    varlist = check_varlist(varlist,size)

    for i in range(int(len(varlist)/size)):
        if rank==0:
            data = [(i*size)+k for k in range(size)]
        else:
            data = None
        data = comm.scatter(data, root=0)
        var = varlist[data]
        print(var)
        if var is not None: mon2ann(fdir, var)

main()
