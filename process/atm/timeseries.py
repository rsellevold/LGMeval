import os, sys
from mpi4py import MPI
import yaml
import xarray as xr
import numpy as np
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


def areastat(data, weights, arith):
    if data.ndim==3:
        if arith=="mean":
            data = np.nansum(data * weights[np.newaxis,...], axis=(1,2)) / np.sum(weights)
        elif arith=="sum":
            data = np.nansum(data * weights[np.newaxis,...], axis=(1,2))
    elif data.ndim==4:
        if arith=="mean":
            data = np.nansum(data * weights[np.newaxis,np.newaxis,...], axis=(2,3)) / np.sum(weights)
        elif arith=="sum":
            data = np.nansum(data * weights[np.newaxis,np.newaxis,...], axis=(2,3))
    return data


def ts(fdir, var, seas, region):
    outdir = f"{fdir[:-12]}/timeseries/{region}/{seas}"
    check_outdir = os.path.exists(outdir)
    if not(check_outdir):
        os.system(f"mkdir -p {outdir}")
    f = xr.open_dataset(f"{fdir}/{var}")
    keys = list(f.keys())
    if "time_bnds" in keys: keys.remove("time_bnds")
    key = keys[0]
    farea = cdo.gridarea(input=f, returnXDataset=True)

    if key=="ICEFRAC":
        arith="sum"
    else:
        arith="mean"

    if region=="global":
        data = areastat(f[key].values, farea.cell_area.values, arith=arith)
    elif region=="NH":
        data = areastat(f[key].sel(lat=slice(0,90)).values, farea.sel(lat=slice(0,90)).cell_area.values, arith=arith)
    elif region=="SH":
        data = areastat(f[key].sel(lat=slice(-90,0)).values, farea.sel(lat=slice(-90,0)).cell_area.values, arith=arith)
    elif region=="tropical":
        data = areastat(f[key].sel(lat=slice(-30,30)).values, farea.sel(lat=slice(-30,30)).cell_area.values, arith=arith)
    else:
        sys.exit("Undefined region")

    if data.ndim == 1:
        data = xr.DataArray(data, name=key, dims=("time"), coords=[f.time])
    elif data.ndim == 2:
        data = xr.DataArray(data, name=key, dims=("time","lev"), coords=[f.time, f.lev])

    data = data.to_dataset()
    data.encoding["unlimited_dims"] = "time"
    data.to_netcdf(f"{outdir}/{var}")

    data.close()
    farea.close()
    f.close()


def main():
    # Initialize MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Get config
    with open("config.yml","r") as f:
        config = yaml.safe_load(f)

    for seas in ["DJFavg", "MAMavg", "JJAavg", "SONavg", "annavg"]:
        if rank==0:
            print(seas)
        fdir = f"{config['run']['folder']}/{config['run']['name']}/atm/hist/{seas}"
        varlist = os.popen(f"ls {fdir}").read().split("\n")[:-1]
        varlist = check_varlist(varlist,size)

        for region in config["timeseries"]["regions"]:
            if rank==0:
                print(region)

            for i in range(int(len(varlist)/size)):
                if rank==0:
                    data = [(i*size)+k for k in range(size)]
                else:
                    data = None
                data = comm.scatter(data, root=0)
                var = varlist[data]
                print(var)
                if var is not None: ts(fdir, var, seas, region)

main()
