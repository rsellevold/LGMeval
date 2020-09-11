import os, sys, glob
import xarray as xr
import numpy as np
import cftime
import Ngl
from cdo import Cdo

cdo = Cdo()

def merge_hist(info, comp, varlist, vdict, hfile, htype, dimensions=2):
	# Check if output folder exists
	print("Merging history files for component ", comp, " and history tape ", hfile)
	outfolder = f"{info['run']['folder']}/{info['run']['name']}/{comp}/hist/{htype}"
	check = os.path.exists(outfolder)
	if not(check):
		os.system(f"mkdir -p {outfolder}")

	# Get all the files and open
	fnames_all = []
	for key,item in info.items():
		if key!="run":
			fnames = glob.glob(f"{info[key]['folder']}/{key}/{comp}/hist/*.{hfile}.*.nc")
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
	
	for var in varlist:
		print(var)
		if dimensions==3:
			levels = xr.DataArray(np.array([500.0]), name="level", dims=("lev"))
			data = Ngl.vinth2p(f[var].values, f["hyam"].values[0,:], f["hybm"].values[0,:], levels.values, f["PS"], 1, 1000.0, 1, False)
			data = xr.DataArray(data, name=var, dims=("time","lev","lat","lon"), coords=[f.time, levels, f.lat, f.lon])
		else:
			data = f[var]
		data.values = data.values * vdict[var]["scalar"]
		data.attrs["units"] = vdict[var]["units"]
		data.attrs["long_name"] = vdict[var]["long_name"]
		data.attrs["cmap"] = vdict[var]["cmap"]
		data = data.to_dataset()
		data.encoding["unlimited_dims"] = "time"
		data.to_netcdf(f"{outfolder}/{var}.{info['run']['ystart']}-{info['run']['yend']}.nc")

def calcadd_atm(info, varlist, vdict, htype):
	outfolder = f"{info['run']['folder']}/{info['run']['name']}/atm/hist/{htype}"

	try:
		FSNS = xr.open_dataset(f"{outfolder}/FSNS.{info['run']['ystart']}-{info['run']['yend']}.nc")
		FSDS = xr.open_dataset(f"{outfolder}/FSDS.{info['run']['ystart']}-{info['run']['yend']}.nc")
		ALBEDO = 1 - (FSNS["FSNS"]/FSDS["FSDS"])
		ALBEDO.name = "ALBEDO"
		ALBEDO.values = ALBEDO.values * vdict["ALBEDO"]["scalar"]
		ALBEDO.attrs["units"] = vdict["ALBEDO"]["units"]
		ALBEDO.attrs["long_name"] = vdict["ALBEDO"]["long_name"]
		ALBEDO.attrs["cmap"] = vdict["ALBEDO"]["cmap"]
		ALBEDO.to_dataset()
		ALBEDO.encoding["unlimited_dims"] = "time"
		ALBEDO.to_netcdf(f"{outfolder}/ALBEDO.{info['run']['ystart']}-{info['run']['yend']}.nc")
		varlist.append("ALBEDO")
	except:
		None

	try:
		PRECC = xr.open_dataset(f"{outfolder}/PRECC.{info['run']['ystart']}-{info['run']['yend']}.nc")
		PRECL = xr.open_dataset(f"{outfolder}/PRECL.{info['run']['ystart']}-{info['run']['yend']}.nc")
		PRECT = PRECC["PRECC"] + PRECL["PRECL"]
		PRECT.name = "PRECT"
		PRECT.values = PRECT.values * vdict["PRECT"]["scalar"]
		PRECT.attrs["units"] = vdict["PRECT"]["units"]
		PRECT.attrs["long_name"] = vdict["PRECT"]["long_name"]
		PRECT.attrs["cmap"] = vdict["PRECT"]["cmap"]
		PRECT.to_dataset()
		PRECT.encoding["unlimited_dims"] = "time"
		PRECT.to_netcdf(f"{outfolder}/PRECT.{info['run']['ystart']}-{info['run']['yend']}.nc")
		varlist.append("PRECT")
	except:
		None

	try:
		PRECSC = xr.open_dataset(f"{outfolder}/PRECSC.{info['run']['ystart']}-{info['run']['yend']}.nc")
		PRECSL = xr.open_dataset(f"{outfolder}/PRECSL.{info['run']['ystart']}-{info['run']['yend']}.nc")
		SNOW = PRECSC["PRECSC"] + PRECSL["PRECSL"]
		SNOW.name = "SNOW"
		SNOW.values = SNOW.values * vdict["SNOW"]["scalar"]
		SNOW.attrs["units"] = vdict["SNOW"]["units"]
		SNOW.attrs["long_name"] = vdict["SNOW"]["long_name"]
		SNOW.attrs["cmap"] = vdict["SNOW"]["cmap"]
		SNOW.to_dataset()
		SNOW.encoding["unlimited_dims"] = "time"
		SNOW.to_netcdf(f"{outfolder}/SNOW.{info['run']['ystart']}-{info['run']['yend']}.nc")
		varlist.append("SNOW")
	except:
		None

	try:
		PRECT = xr.open_dataset(f"{outfolder}/PRECT.{info['run']['ystart']}-{info['run']['yend']}.nc")
		SNOW = xr.open_dataset(f"{outfolder}/SNOW.{info['run']['ystart']}-{info['run']['yend']}.nc")
		RAIN = PRECT["PRECT"] - SNOW["SNOW"]
		RAIN.name = "RAIN"
		RAIN.values = RAIN.values * vdict["RAIN"]["scalar"]
		RAIN.attrs["units"] = vdict["RAIN"]["units"]
		RAIN.attrs["long_name"] = vdict["RAIN"]["long_name"]
		RAIN.attrs["cmap"] = vdict["RAIN"]["cmap"]
		RAIN.to_dataset()
		RAIN.encoding["unlimited_dims"] = "time"
		RAIN.to_netcdf(f"{outfolder}/RAIN.{info['run']['ystart']}-{info['run']['yend']}.nc")
		varlist.append("RAIN")
	except:
		None

	try:
		FSNT = xr.open_dataset(f"{outfolder}/FSNT.{info['run']['ystart']}-{info['run']['yend']}.nc")
		FLNT = xr.open_dataset(f"{outfolder}/FLNT.{info['run']['ystart']}-{info['run']['yend']}.nc")
		RADTOA = FSNT["FSNT"] - FLNT["FLNT"]
		RAIN.name = "RADTOA"
		RADTOA.values = RADTOA.values * vdict["RADTOA"]["scalar"]
		RADTOA.attrs["units"] = vdict["RADTOA"]["units"]
		RADTOA.attrs["long_name"] = vdict["RADTOA"]["long_name"]
		RADTOA.attrs["cmap"] = vdict["RADTOA"]["cmap"]
		RADTOA.to_dataset()
		RADTOA.encoding["unlimited_dims"] = "time"
		RADTOA.to_netcdf(f"{outfolder}/RADTOA.{info['run']['ystart']}-{info['run']['yend']}.nc")
		varlist.append("RADTOA")
	except:
		None

	return varlist


def mon2seas(info, comp, varlist):
	indir = f"{info['run']['folder']}/{info['run']['name']}/{comp}/hist/monavg"
	tmpdir = f"{info['run']['folder']}/{info['run']['name']}/{comp}/temp"
	os.system(f"mkdir -p {tmpdir}")
	for var in varlist:
		infile = f"{indir}/{var}.{info['run']['ystart']}-{info['run']['yend']}.nc"
		tmpfile = f"{tmpdir}/{var}.seasavg.nc"
		cdo.seasavg(input=infile, output=tmpfile)
		cdo.splitseas(input=tmpfile, output=f"{tmpdir}/{var}.seasavg.")
		for seas in ["DJF", "MAM", "JJA", "SON"]:
			outdir = f"{info['run']['folder']}/{info['run']['name']}/{comp}/hist/{seas}avg"
			check = os.path.exists(outdir)
			if not(check):
				os.system(f"mkdir -p {outdir}")
			os.system(f"mv {tmpdir}/{var}.seasavg.{seas}.nc {outdir}/{var}.{info['run']['ystart']}-{info['run']['yend']}.nc")
	os.system(f"rm -r {tmpdir}")

def mon2ann(info, comp, varlist):
	indir = f"{info['run']['folder']}/{info['run']['name']}/{comp}/hist/monavg"
	outdir = f"{info['run']['folder']}/{info['run']['name']}/{comp}/hist/annavg"
	os.system(f"mkdir -p {outdir}")
	for var in varlist:
		infile = f"{indir}/{var}.{info['run']['ystart']}-{info['run']['yend']}.nc"
		outfile = f"{outdir}/{var}.{info['run']['ystart']}-{info['run']['yend']}.nc"
		cdo.yearavg(input=infile, output=outfile)