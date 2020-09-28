import os,sys
sys.path.append("/home/raymond/LGMeval")

from mpi4py import MPI
import yaml
import src


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
    varlist = src.mpimods.check_varlist(varlist,size)

    for i in range(int(len(varlist)/size)):
        if rank==0:
            data = [(i*size)+k for k in range(size)]
        else:
            data = None
        data = comm.scatter(data, root=0)
        var = varlist[data]
        print(var)
        if var is not None: src.preproc.annavg(fdir, var)

main()
