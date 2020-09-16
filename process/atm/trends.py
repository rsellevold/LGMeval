import os, sys
from mpi4py import MPI
import yaml
import xarray as xr
import numpy as np
from scipy.stats import linregress


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


def trend_calc(data, tt):
    if data.ndim == 3:
       ny = data.shape[1]
       nx = data.shape[2]
       tren = np.empty(shape=(ny,nx))
       r = np.empty(shape=(ny,nx))
       p = np.empty(shape=(ny,nx))
       for y in range(ny):
           for x in range(nx):
               tren[y,x], _, r[y,x], p[y,x], _ = linregress(np.arange(0,tt,1), data[:,y,x])

    elif data.ndim == 4:
        nk = data.shape[1]
        ny = data.shape[2]
        nx = data.shape[3]
        tren = np.empty(shape=(nk,ny,nx))
        r = np.empty(shape=(nk,ny,nx))
        p = np.empty(shape=(nk,ny,nx))
        for k in range(nk):
            for y in range(ny):
                for x in range(nx):
                    tren[k,y,x], _, r[k,y,x], p[k,y,x], _ = linregress(np.arange(0,tt,1), data[:,k,y,x])
        
    return (tren, r, p)



def trend(fdir, var, seas, nyears):
    outdir = f"{fdir[:-12]}/trend/{seas}"
    check_outdir = os.path.exists(outdir)
    if not(check_outdir):
        os.system(f"mkdir -p {outdir}")
    f = xr.open_dataset(f"{fdir}/{var}")
    keys = list(f.keys())
    if "time_bnds" in keys: keys.remove("time_bnds")
    key = keys[0]
    tt = len(f.time.values)

    if type(nyears)==str and nyears=="all":
        tren, r, p = trend_calc(f[key].values, tt)
    elif type(nyears)==int:
        tren, r, p = trend_calc(f[key].values[-nyears:,...], nyears)
    elif type(nyears)==tuple:
        tren, r, p = trend_calc(f[key].values[nyears[0]:nyears[1],...], tt[nyears[0],nyears[1]])

    if tren.ndim == 2:
        tren = xr.DataArray(tren, name="trend", dims=("lat","lon"), coords=[f.lat, f.lon])
        r = xr.DataArray(r, name="r", dims=("lat","lon"), coords=[f.lat, f.lon])
        p = xr.DataArray(p, name=p, dims=("lat","lon"), coords=[f.lat, f.lon])
    elif tren.ndim == 3:
        tren = xr.DataArray(tren, name="trend", dims=("lev","lat","lon"), coords=[f.lev, f.lat, f.lon])
        r = xr.DataArray(r, name="r", dims=("lev","lat","lon"), coords=[f.lev, f.lat, f.lon])
        p = xr.DataArray(p, name=p, dims=("lev","lat","lon"), coords=[f.lev, f.lat, f.lon])

    fout = xr.Dataset({"trend": tren, "r":r, "p":p})
    fout.attrs["nyears"] = nyears
    fout.to_netcdf(f"{outdir}/{var}")
    fout.close()
    f.close()


def main():
    # Initialize MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Get config
    with open("config.yml","r") as f:
        config = yaml.safe_load(f)

    nyears = config["trend"]["nyears"]
    for seas in ["DJFavg", "MAMavg", "JJAavg", "SONavg", "annavg"]:
        if rank==0:
            print(seas)
        fdir = f"{config['run']['folder']}/{config['run']['name']}/atm/hist/{seas}"
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
            if var is not None: trend(fdir, var, seas, nyears)

main()
