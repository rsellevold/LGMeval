import sys
import yaml

sys.path.append("/home/raymond/LGMeval")
import src.viz as viz
import maplotlib.pyplot as plt
import cartopy.crs as crs

###############
# Give definitions
###############
run = "LGM"
scratchdir = "/scratch-shared/raymond"
ystart = 338
yend = 403
ystart_use = 403-30+1
yend_use = 403
seasons = ["annavg","DJFavg","MAMavg","JJAavg","SONavg"]

with open("../src/vars/cam.yml","r") as f:
  varcon = yaml.safe_load(f)

################
# Plotting resources
################
for seas in seasons:
  fdir = f"{scratchdir}/{run}/atm/trend/{seas}"
  for var in varlist:
    fname = f"{fdir}/{var}.{ystart_use}-{yend_use}.nc"
    ds = xr.open_dataset(fname)

    fig = plt.figure(figsize=(7.3,7.3))
    ax = plt.subplot(1,1,1, projection=crs.PlateCarree())
    ax.contourf(ds.lon.values, ds.lat.values, ds["trend"].values)

    print(fname)
    sys.exit()
