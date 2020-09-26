import os, sys
import yaml
import xarray as xr
import numpy as np


def plot_trend(fdir, var, seas, sig, plotdir):
    f = xr.open_dataset(f"{fdir}/{var}")

    data = f["trend"]
    p = f["p"]



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

    # Get config
    with open("config.yml","r") as f:
        config = yaml.safe_load(f)

    plotdir = config["run"]["plotdir"]
    sig = config["trend"]["significance"]
    for seas in ["DJFavg", "MAMavg", "JJAavg", "SONavg", "annavg"]:
        print(seas)
        fdir = f"{config['run']['folder']}/{config['run']['name']}/atm/trend/{seas}"
        varlist = os.popen(f"ls {fdir}").read().split("\n")[:-1]
        print(varlist)

        for i in range(len(varlist)):
            var = varlist[data]
            print(var)
            plot_trend(fdir, var, seas, sig, plotdir)

main()
