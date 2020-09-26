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
ice_SH = f.ICEFRAC.sel(lat=slice(-90,0))
farea = cdo.gridarea(input=f, returnXDataset=True)
farea_SH = farea.sel(lat=slice(-90,0))

# Load observations
df = pd.read_csv("plot/atm/LGMspecial/SH_SISST.csv", sep=";")
obslon = [float(i.replace("−","-")) for i in list(df["Long."][:])]
obslat = [float(i.replace("−","-")) for i in list(df["Lat."][:])]
obs_SH_sep = [float(i) for i in list(df["E-LGM Sept. SI conc. (%)"][:])]
obs_SH_feb = [float(i) for i in list(df["E-LGM Feb. SI conc. (%)"][:])]

# Process
SHdims = ice_SH.values.shape
ice_SH_re = np.reshape(ice_SH.values, (int(SHdims[0]/12),12,SHdims[1],SHdims[2]))

# Calculate monthly timeseries
ice_SH_ts = np.sum(ice_SH_re * farea_SH.cell_area.values[np.newaxis,np.newaxis,...], axis=(2,3)) / 1e+12

# Add cyclic
ice_SH_re, lonSH = add_cyclic_point(ice_SH_re, coord=ice_SH.lon.values)

# Make plot
plotdir = f"{config['run']['plotdir']}/atm/ICEFRAC"
if not(os.path.exists(plotdir)):
  os.system(f"mkdir -p {plotdir}")

fig = plt.figure(figsize=(7.3,7.3))

ax1 = plt.subplot(2,2,1, projection=ccrs.SouthPolarStereo())
ax1.add_feature(cartopy.feature.LAND, facecolor="gray", edgecolor='black', linewidth=0.5, zorder=98)
ax1.set_title("September sea-ice extent", loc="left")
ax1.set_extent([-180,180,-90,-30], ccrs.PlateCarree())
ax1.contour(lonSH, ice_SH.lat.values, np.mean(ice_SH_re[-20:,8,:,:],axis=0), [0.15], colors="tab:blue", transform=ccrs.PlateCarree(), zorder=99)
gl = ax1.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0.5, color="black", linestyle="--", zorder=100)
gl.top_labels=False
gl.left_labels=False
gl.xlines = False
gl.xlabel_style = {'size': 0}
gl.ylabel_style = {'size': 0}
for i in ["top","bottom","left","right"]:
  ax1.spines[i].set_linewidth(0.2)
for o in range(len(obslon)):
  if np.isnan(obs_SH_sep[o]):
    None
  elif obs_SH_sep[o]<0.15:
    ax1.scatter(obslon[o], obslat[o], c="tab:blue", s=10, marker="x", transform=ccrs.PlateCarree(), zorder=99)
  elif obs_SH_sep[o]>=0.15:
    ax1.scatter(obslon[o], obslat[o], c="tab:blue", s=10, marker="o", transform=ccrs.PlateCarree(), zorder=99)

ax2 = plt.subplot(2,2,2, projection=ccrs.SouthPolarStereo())
ax2.add_feature(cartopy.feature.LAND, facecolor="gray", edgecolor='black', linewidth=0.5, zorder=98)
ax2.set_title("February sea-ice extent", loc="left")
ax2.set_extent([-180,180,-90,-30], ccrs.PlateCarree())
for o in range(len(obslon)):
  if np.isnan(obs_SH_feb[o]):
    None
  elif obs_SH_feb[o]<0.15:
    ax2.scatter(obslon[o], obslat[o], c="tab:red", s=10, marker="x", transform=ccrs.PlateCarree(), zorder=99)
  elif obs_SH_feb[o]>=0.15:
    ax2.scatter(obslon[o], obslat[o], c="tab:red", s=10, marker="o", transform=ccrs.PlateCarree(), zorder=99)
ax2.contour(lonSH, ice_SH.lat.values, np.mean(ice_SH_re[-20:,1,:,:],axis=0), [0.15], colors="tab:red", transform=ccrs.PlateCarree(), zorder=99)
gl = ax2.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0.5, color="black", linestyle="--", zorder=100)
gl.top_labels=False
gl.left_labels=False
gl.xlines = False
gl.xlabel_style = {'size': 0}
gl.ylabel_style = {'size': 0}

ax3 = plt.subplot(2,2,3)
ax3.set_title(r"Sea-ice area ($\times$10$^6$ km$^2$)", loc="left", y=1.01)
ax3.plot(np.arange(f.time.dt.year[0],f.time.dt.year[-1]+1,1), ice_SH_ts[:,1], color="tab:red", label="February")
ax3.plot(np.arange(f.time.dt.year[0],f.time.dt.year[-1]+1,1), ice_SH_ts[:,8], color="tab:blue", label="September")
ax3.plot(np.arange(f.time.dt.year[0],f.time.dt.year[-1]+1,1), ice_SH_ts[:,8]-ice_SH_ts[:,1], color="black", label="Diff")
ax3.legend(frameon=False)
ax3.minorticks_on()
ax3.tick_params("both", length=6, width=0.6, which="major", bottom=True, top=True, left=True, right=True)
ax3.tick_params("both", length=3, width=0.2, which="minor", bottom=True, top=True, left=True, right=True)
ax3.set_xlabel("Year")
ax3.set_xlim([f.time.dt.year[0],f.time.dt.year[-1]])
pos = ax3.get_position()
ax3.set_position([pos.x0, pos.y0, pos.width*2+0.07, pos.height])

plt.savefig(f"{config['run']['plotdir']}/atm/ICEFRAC/SH.{config['run']['ystart']}-{config['run']['yend']}.png", dpi=300)
