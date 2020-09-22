import os
import xarray as xr
import numpy as np
import yaml
from cdo import Cdo
import cartopy.crs as ccrs
import cartopy
from cartopy.util import add_cyclic_point
import matplotlib.pyplot as plt
import pandas as pd

cdo = Cdo()

# Get config gile
with open("config.yml","r") as f:
  config = yaml.safe_load(f)

# Load data
fname = f"{config['run']['folder']}/{config['run']['name']}/atm/hist/monavg/ICEFRAC.{config['run']['ystart']}-{config['run']['yend']}.nc"
f = xr.open_dataset(fname)
ice_NH = f.ICEFRAC.sel(lat=slice(0,90))
ice_SH = f.ICEFRAC.sel(lat=slice(-90,0))
farea = cdo.gridarea(input=f, returnXDataset=True)
farea_NH = farea.sel(lat=slice(0,90))
farea_SH = farea.sel(lat=slice(-90,0))

# Process
NHdims = ice_NH.values.shape
ice_NH_re = np.reshape(ice_NH.values, (int(NHdims[0]/12),12,NHdims[1],NHdims[2]))
SHdims = ice_SH.values.shape
ice_SH_re = np.reshape(ice_SH.values, (int(SHdims[0]/12),12,SHdims[1],SHdims[2]))

# Calculate monthly timeseries
ice_NH_ts = np.sum(ice_NH_re * farea_NH.cell_area.values[np.newaxis,np.newaxis,...], axis=(2,3)) / 1e+12
ice_SH_ts = np.sum(ice_SH_re * farea_SH.cell_area.values[np.newaxis,np.newaxis,...], axis=(2,3)) / 1e+12

# Add cyclic
ice_NH_re, lonNH = add_cyclic_point(ice_NH_re, coord=ice_NH.lon.values)
ice_SH_re, lonSH = add_cyclic_point(ice_SH_re, coord=ice_SH.lon.values)

# Make plot
plotdir = f"{config['run']['plotdir']}/atm/ICEFRAC"
if not(os.path.exists(plotdir)):
  os.system(f"mkdir -p {plotdir}")

fig = plt.figure(figsize=(7.3,7.3))

ax1 = plt.subplot(2,2,1, projection=ccrs.NorthPolarStereo())
ax1.add_feature(cartopy.feature.LAND, facecolor="gray", edgecolor='black', linewidth=0.5, zorder=98)
ax1.set_title("NH sea ice max/min", loc="left")
ax1.set_extent([-180,180,30,90], ccrs.PlateCarree())
ax1.contour(lonNH, ice_NH.lat.values, np.mean(ice_NH_re[-20:,2,:,:],axis=0), [0.15], colors="tab:blue", transform=ccrs.PlateCarree(), zorder=99)
ax1.contour(lonNH, ice_NH.lat.values, np.mean(ice_NH_re[-20:,8,:,:],axis=0), [0.15], colors="tab:red", transform=ccrs.PlateCarree(), zorder=99)
gl = ax1.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0.5, color="black", linestyle="--", zorder=100)
gl.top_labels=False
gl.left_labels=False
gl.xlines = False
gl.xlabel_style = {'size': 0}
gl.ylabel_style = {'size': 0}

ax2 = plt.subplot(2,2,2, projection=ccrs.SouthPolarStereo())
ax2.add_feature(cartopy.feature.LAND, facecolor="gray", edgecolor='black', linewidth=0.5, zorder=98)
ax2.set_title("SH sea ice max/min", loc="left")
ax2.set_extent([-180,180,-90,-30], ccrs.PlateCarree())
ax2.contour(lonSH, ice_SH.lat.values, np.mean(ice_SH_re[-20:,1,:,:],axis=0), [0.15], colors="tab:blue", transform=ccrs.PlateCarree(), zorder=99)
ax2.contour(lonSH, ice_SH.lat.values, np.mean(ice_SH_re[-20:,8,:,:],axis=0), [0.15], colors="tab:red", transform=ccrs.PlateCarree(), zorder=99)
gl = ax2.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0.5, color="black", linestyle="--", zorder=100)
gl.top_labels=False
gl.left_labels=False
gl.xlines = False
gl.xlabel_style = {'size': 0}
gl.ylabel_style = {'size': 0}

ax3 = plt.subplot(2,2,3)
ax3.set_title(r"NH sea ice area ($\times$10$^6$ km$^2$)", loc="left", y=1.01)
ax3.plot(np.arange(f.time.dt.year[0],f.time.dt.year[-1]+1,1), ice_NH_ts[:,2], color="tab:blue", label="March")
ax3.plot(np.arange(f.time.dt.year[0],f.time.dt.year[-1]+1,1), ice_NH_ts[:,8], color="tab:red", label="September")
ax3.plot(np.arange(f.time.dt.year[0],f.time.dt.year[-1]+1,1), ice_NH_ts[:,2]-ice_NH_ts[:,8], color="black", label="Diff")
ax3.legend(frameon=False)
ax3.minorticks_on()
ax3.tick_params("both", length=6, width=0.6, which="major", bottom=True, top=True, left=True, right=True)
ax3.tick_params("both", length=2, width=0.2, which="minor", bottom=True, top=True, left=True, right=True)
ax3.set_xlabel("Year")
ax3.set_xlim([f.time.dt.year[0],f.time.dt.year[-1]])

ax4 = plt.subplot(2,2,4)
ax4.set_title(r"SH sea ice area ($\times$10$^6$ km$^2$)", loc="left", y=1.01)
ax4.plot(np.arange(f.time.dt.year[0],f.time.dt.year[-1]+1,1), ice_SH_ts[:,1], color="tab:blue", label="February")
ax4.plot(np.arange(f.time.dt.year[0],f.time.dt.year[-1]+1,1), ice_SH_ts[:,8], color="tab:red", label="September")
ax4.plot(np.arange(f.time.dt.year[0],f.time.dt.year[-1]+1,1), ice_SH_ts[:,8]-ice_SH_ts[:,2], color="black", label="Diff")
ax4.legend(frameon=False)
ax4.minorticks_on()
ax4.tick_params("both", length=6, width=0.6, which="major", bottom=True, top=True, left=True, right=True)
ax4.tick_params("both", length=2, width=0.2, which="minor", bottom=True, top=True, left=True, right=True)
ax4.set_xlabel("Year")
ax4.set_xlim([f.time.dt.year[0],f.time.dt.year[-1]])

plt.savefig(f"{config['run']['plotdir']}/atm/ICEFRAC/{config['run']['ystart']}-{config['run']['yend']}.png", dpi=300)
