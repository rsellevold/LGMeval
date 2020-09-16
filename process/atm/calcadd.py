import os
from mpi4py import MPI
import yaml
import xarray as xr

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



def calcadd(fdir, var, ystart, yend):
    if var=="ALBEDO":
        try:
            FSNS = xr.open_dataset(f"{fdir}/FSNS.{ystart}-{yend}.nc")
            FSDS = xr.open_dataset(f"{fdir}/FSDS.{ystart}-{yend}.nc")
            ALBEDO = 1 - (FSNS["FSNS"]/FSDS["FSDS"])
            ALBEDO.name = "ALBEDO"
            ALBEDO.to_dataset()
            ALBEDO.encoding["unlimited_dims"] = "time"
            ALBEDO.to_netcdf(f"{fdir}/ALBEDO.{ystart}-{yend}.nc")
            ALBEDO.close()
        except:
            None

    elif var=="PRECT":
        try:
            PRECC = xr.open_dataset(f"{fdir}/PRECC.{ystart}-{yend}.nc")
            PRECL = xr.open_dataset(f"{fdir}/PRECL.{ystart}-{yend}.nc")
            PRECT = PRECC["PRECC"] + PRECL["PRECL"]
            PRECT.name = "PRECT"
            PRECT.to_dataset()
            PRECT.encoding["unlimited_dims"] = "time"
            PRECT.to_netcdf(f"{fdir}/PRECT.{ystart}-{yend}.nc")
            PRECT.close()
        except:
            None

    elif var=="SNOW":
        try:
            PRECSC = xr.open_dataset(f"{fdir}/PRECSC.{ystart}-{yend}.nc")
            PRECSL = xr.open_dataset(f"{fdir}/PRECSL.{ystart}-{yend}.nc")
            SNOW = PRECSC["PRECSC"] + PRECSL["PRECSL"]
            SNOW.name = "SNOW"
            SNOW.to_dataset()
            SNOW.encoding["unlimited_dims"] = "time"
            SNOW.to_netcdf(f"{fdir}/SNOW.{ystart}-{yend}.nc")
            SNOW.close()
        except:
            None

    elif var=="RAIN":
        try:
            PRECT = xr.open_dataset(f"{fdir}/PRECT.{ystart}-{yend}.nc")
            SNOW = xr.open_dataset(f"{fdir}/SNOW.{ystart}-{yend}.nc")
            RAIN = PRECT["PRECT"] - SNOW["SNOW"]
            RAIN.name = "RAIN"
            RAIN.to_dataset()
            RAIN.encoding["unlimited_dims"] = "time"
            RAIN.to_netcdf(f"{fdir}/RAIN.{ystart}-{yend}.nc")
            RAIN.close()
        except:
            None

    elif var=="RADTOA":
        try:
            FSNT = xr.open_dataset(f"{fdir}/FSNT.{ystart}-{yend}.nc")
            FLNT = xr.open_dataset(f"{fdir}/FLNT.{ystart}-{yend}.nc")
            RADTOA = FSNT["FSNT"] - FLNT["FLNT"]
            RADTOA.name = "RADTOA"
            RADTOA.to_dataset()
            RADTOA.encoding["unlimited_dims"] = "time"
            RADTOA.to_netcdf(f"{fdir}/RADTOA.{ystart}-{yend}.nc")
            RADTOA.close()
        except:
            None


def main():
    # Initialize MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Get config
    with open("config.yml","r") as f:
        config = yaml.safe_load(f)

    fdir = f"{config['run']['folder']}/{config['run']['name']}/atm/hist/monavg"
    varlist = ["ALBEDO", "PRECT", "SNOW", "RAIN", "RADTOA"]
    varlist = check_varlist(varlist, size)
    ystart = config["run"]["ystart"]
    yend = config["run"]["yend"]

    for i in range(int(len(varlist)/size)):
        if rank==0:
            data = [(i*size)+k for k in range(size)]
        else:
            data = None
        data = comm.scatter(data, root=0)
        var = varlist[data]
        print(var)
        if var is not None: calcadd(fdir, var, ystart, yend)

main()
