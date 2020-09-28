import sys,os,glob

import xarray as xr
import cftime
from cdo import Cdo

cdo = Cdo()


def _checkdir(folder):
  check = os.path.exists(folder)
  if not(check):
    os.system(f"mkdir -p {folder}")


def annavg(fdir, var):
  # Computes the annual means
  outdir = f"{fdir[:-7]}/annavg"
  _checkdir(outdir)
  cdo.yearavg(input=f"{fdir}/{var}", output=f"{outdir}/{var}")


def seasavg(fdir, var):
  tmpdir = f"{fdir[:-7]}/temp"
  _checkdir(tmpdir)
  infile = f"{fdir}/{var}"
  tmpfile = f"{tmpdir}/{var}.seasavg.nc"
  cdo.seasavg(input=infile, output=tmpfile)
  cdo.splitseas(input=tmpfile, output=f"{tmpdir}/{var}.seasavg.")
  for seas in ["DJF","MAM","JJA","SON"]:
    outdir = f"{fdir[:-7]}/{seas}avg"
    _checkdir(outdir)
    os.system(f"mv {tmpdir}/{var}.seasavg.{seas}.nc {outdir}/{var}")
  os.system(f"rm {tmpdir}/{var}.seasavg.*")


def mergehist(config, comp, var, hfile, htype):
  outfolder = f"{config['run']['folder']}/{config['run']['name']}/{comp}/hist/{htype}"
  _checkdir(outfolder)

  fnames_all = []
  for key,item in config["runs"].items():
    fnames = glob.glob(f"{config['runs'][key]['folder']}/{key}/{comp}/hist/*.{hfile}.*.nc")
    fnames_all.append(fnames)
  fnames_all = [item for sublist in fnames_all for item in sublist]

  f = xr.open_mfdataset(fnames_all, concat_dim="time")
  f = f.sortby("time")

  try:
    bnds = cftime.date2num(f[config["compset"][comp]["bnds"]].values, "days since 0001-01-01 00:00:00", calendar="noleap")
  except:
    sys.exit("Provided time bounds does not exsist, update config.yml: compset/[component]/bnds")

  bnds = (bnds[:,0]+bnds[:,1])/2
  bnds = cftime.num2date(bnds, "days since 0001-01-01 00:00:00", calendar="noleap")
  bnds = xr.DataArray(bnds, name="time", dims=("time"))
  bnds.attrs["long_name"] = f.time.long_name
  f["time"] = bnds

  data = f[var]
  data = data.to_dataset()

  try: # Check if previous data exists
    data_already = xr.open_dataset(f"{outfolder}/{var}.nc")
    data = xr.concat([data, data_already], dim="time")
    data = data.sortby("time")
    data_already.close()
  except FileNotFoundError:
    None

  data.encoding["unlimited_dims"] = "time"
  data.to_netcdf(f"{outfolder}/{var}.nc")

  data.close()
  f.close()
