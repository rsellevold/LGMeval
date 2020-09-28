import sys, os
sys.path.append("/home/raymond/LGMeval")

from mpi4py import MPI
import yaml
import xarray as xr
import src


def calcadd(fdir, var):
    if var=="ALBEDO":
        try:
            FSNS = xr.open_dataset(f"{fdir}/FSNS.nc")
            FSDS = xr.open_dataset(f"{fdir}/FSDS.nc")
            ALBEDO = 1 - (FSNS["FSNS"]/FSDS["FSDS"])
            ALBEDO.name = "ALBEDO"
            ALBEDO.to_dataset()
            ALBEDO.encoding["unlimited_dims"] = "time"
            ALBEDO.to_netcdf(f"{fdir}/ALBEDO.nc")
            ALBEDO.close()
        except:
            None

    elif var=="PRECT":
        try:
            PRECC = xr.open_dataset(f"{fdir}/PRECC.nc")
            PRECL = xr.open_dataset(f"{fdir}/PRECL.nc")
            PRECT = PRECC["PRECC"] + PRECL["PRECL"]
            PRECT.name = "PRECT"
            PRECT.to_dataset()
            PRECT.encoding["unlimited_dims"] = "time"
            PRECT.to_netcdf(f"{fdir}/PRECT.nc")
            PRECT.close()
        except:
            None

    elif var=="SNOW":
        try:
            PRECSC = xr.open_dataset(f"{fdir}/PRECSC.nc")
            PRECSL = xr.open_dataset(f"{fdir}/PRECSL.nc")
            SNOW = PRECSC["PRECSC"] + PRECSL["PRECSL"]
            SNOW.name = "SNOW"
            SNOW.to_dataset()
            SNOW.encoding["unlimited_dims"] = "time"
            SNOW.to_netcdf(f"{fdir}/SNOW.nc")
            SNOW.close()
        except:
            None

    elif var=="RAIN":
        try:
            PRECT = xr.open_dataset(f"{fdir}/PRECT.nc")
            SNOW = xr.open_dataset(f"{fdir}/SNOW.nc")
            RAIN = PRECT["PRECT"] - SNOW["SNOW"]
            RAIN.name = "RAIN"
            RAIN.to_dataset()
            RAIN.encoding["unlimited_dims"] = "time"
            RAIN.to_netcdf(f"{fdir}/RAIN.nc")
            RAIN.close()
        except:
            None

    elif var=="RADTOA":
        try:
            FSNT = xr.open_dataset(f"{fdir}/FSNT.nc")
            FLNT = xr.open_dataset(f"{fdir}/FLNT.nc")
            RADTOA = FSNT["FSNT"] - FLNT["FLNT"]
            RADTOA.name = "RADTOA"
            RADTOA.to_dataset()
            RADTOA.encoding["unlimited_dims"] = "time"
            RADTOA.to_netcdf(f"{fdir}/RADTOA.nc")
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
    varlist = src.mpimods.check_varlist(varlist, size)

    for i in range(int(len(varlist)/size)):
        if rank==0:
            data = [(i*size)+k for k in range(size)]
        else:
            data = None
        data = comm.scatter(data, root=0)
        var = varlist[data]
        print(var)
        if var is not None: calcadd(fdir, var)

main()
