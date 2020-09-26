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



def mon2seas(fdir, var):
    tmpdir = f"{fdir[:-7]}/temp"
    check_tmpdir = os.path.exists(tmpdir)
    if not(check_tmpdir):
        os.system(f"mkdir -p {tmpdir}")
    infile = f"{fdir}/{var}"
    tmpfile = f"{tmpdir}/{var}.seasavg.nc"
    cdo.seasavg(input=infile, output=tmpfile)
    cdo.splitseas(input=tmpfile, output=f"{tmpdir}/{var}.seasavg.")
    for seas in ["DJF", "MAM", "JJA", "SON"]:
        outdir = f"{fdir[:-7]}/{seas}avg"
        check_outdir = os.path.exists(outdir)
        if not(check_outdir):
            os.system(f"mkdir -p {outdir}")
        os.system(f"mv {tmpdir}/{var}.seasavg.{seas}.nc {outdir}/{var}")
    os.system(f"rm {tmpdir}/{var}.seasavg.*")


def main():
    # Initialize MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Get config
    with open("config.yml","r") as f:
        config = yaml.safe_load(f)

    fdir = f"{config['run']['folder']}/{config['run']['name']}/ocn/hist/monavg"
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
        if var is not None: mon2seas(fdir, var)

main()
