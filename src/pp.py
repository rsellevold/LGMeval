import os, sys
from scipy.stats import linregress
import xarray as xr
import numpy as np

class pp:

    def __init__(self,diri,run,comp,ystart,yend):
        self.diri = diri
        self.run = run
        self.ystart = int(ystart)
        self.yend = int(yend)
        self.comp = comp
    

    def _trend_calc(self,data,tt):
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
        
        return tren, r, p

    def trend(self, varlist, htype, nyears="all"):
        print("Calculating trend for:")
        fdirin = f"{self.diri}/{self.run}/{self.comp}/hist/{htype}"
        fdirout = f"{self.diri}/{self.run}/{self.comp}/trend/{htype}"
        check = os.path.exists(fdirout)
        if not(check):
            os.system(f"mkdir -p {fdirout}")
        for var in varlist:
            print(var)
            f = xr.open_dataset(f"{fdirin}/{var}.{self.ystart}-{self.yend}.nc")
            tt = len(f.time.values)

            if type(nyears)==str and nyears=="all":
                tren, r, p = self._trend_calc(f[var].values, tt)
                ystart = self.ystart
                yend = self.yend
            elif type(nyears)==int:
                tren, r, p = self._trend_calc(f[var].values[-nyears:,...], nyears)
                ystart = self.yend-nyears
                yend = self.yend
            elif type(nyears)==list:
                tren, r, p = self._trend_calc(f[var].values[nyears[0]:nyears[1],...], tt[nyears[0],nyears[1]])
                ystart = nyears[0]
                yend = nyears[1]

            if tren.ndim == 2:
                tren = xr.DataArray(tren, name="trend", dims=("lat","lon"), coords=[f.lat, f.lon])
                r = xr.DataArray(r, name="r", dims=("lat","lon"), coords=[f.lat, f.lon])
                p = xr.DataArray(p, name="p", dims=("lat","lon"), coords=[f.lat, f.lon])
            elif tren.ndim == 3:
                tren = xr.DataArray(tren, name="trend", dims=("lev","lat","lon"), coords=[f.lev, f.lat, f.lon])
                r = xr.DataArray(r, name="r", dims=("lev","lat","lon"), coords=[f.lev, f.lat, f.lon])
                p = xr.DataArray(p, name="p", dims=("lev","lat","lon"), coords=[f.lev, f.lat, f.lon])

            fout = xr.Dataset({"trend": tren, "r":r, "p":p})
            fout.to_netcdf(f"{fdirout}/{var}.{ystart}-{yend}.nc")