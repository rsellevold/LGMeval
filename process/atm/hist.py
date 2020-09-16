import sys, os, glob
from mpi4py import MPI
import yaml
import xarray as xr
import numpy as np
import cftime
import Ngl

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



def mergehist(config,var,hfile,htype):
    outfolder = f"{config['run']['folder']}/{config['run']['name']}/atm/hist/{htype}"
    check_folder = os.path.exists(outfolder)
    if not(check_folder):
        os.system(f"mkdir -p {outfolder}")
    
    # Get all the files and open
    fnames_all = []
    for key,item in config["runs"].items():
        fnames = glob.glob(f"{config['runs'][key]['folder']}/{key}/atm/hist/*.{hfile}.*.nc")
        fnames_all.append(fnames)
    fnames_all = [item for sublist in fnames_all for item in sublist]

    f = xr.open_mfdataset(fnames_all, concat_dim="time")
    f = f.sortby("time")
    
    try:
        bnds = cftime.date2num(f.time_bnds.values, "days since 0001-01-01 00:00:00", calendar="noleap")
    except:
        None
    bnds = (bnds[:,0]+bnds[:,1])/2
    bnds = cftime.num2date(bnds, "days since 0001-01-01 00:00:00", calendar="noleap")
    bnds = xr.DataArray(bnds, name="time", dims=("time"))
    bnds.attrs["long_name"] = f.time.long_name
    #bnds.attrs["calendar"] = "noleap"
    f["time"] = bnds

    ndims = f[var].values.ndim
    if ndims==4:
        None
        #levels = np.array([1000.0, 950.0, 900.0, 850.0, 800.0, 700.0, 600.0, 500.0, 400.0, 300.0, 250.0, 200.0])
        #for level in levels:
        #    print(level)
        #    data = Ngl.vinth2p(f[var].values, f["hyam"].values[0,:], f["hybm"].values[0,:], level, f["PS"], 1, 1000.0, 1, False)
        #    data[data > 1e+10] = np.nan
        #    lvl = int(level)
        #    data = xr.DataArray(data, name=f"{var}{lvl}", dims=("time","lat","lon"), coords=[f.time, f.lat, f.lon], attrs=f[var].attrs)
        #    data.encoding["unlimited_dims"] = "time"
        #    data.to_netcdf(f"{outfolder}/{var}{lvl}.{config['run']['ystart']}-{config['run']['yend']}.nc")
        #    data.close()
    else:
        data = f[var]
        data = data.to_dataset()
        data.encoding["unlimited_dims"] = "time"
        data.to_netcdf(f"{outfolder}/{var}.{config['run']['ystart']}-{config['run']['yend']}.nc")
        data.close()
    f.close()


def main():
    # Initialize MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Get config
    with open("config.yml","r") as f:
        config = yaml.safe_load(f)
    
    hfiles = list(config["history"]["atm"].keys())
    for h in range(len(hfiles)):
        varlist = config["history"]["atm"][hfiles[h]]["varlist"]
        varlist = check_varlist(varlist,size)
        htype = config["history"]["atm"][hfiles[h]]["htype"]

        for i in range(int(len(varlist)/size)):
            if rank==0:
                data = [(i*size)+k for k in range(size)]
            else:
                data = None
            data = comm.scatter(data, root=0)
            var = varlist[data]
            print(var)
            if var is not None: mergehist(config, var, hfiles[h], htype)

main()
