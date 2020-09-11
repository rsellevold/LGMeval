import os,sys
from eofs.standard import Eof
from mpl_toolkits.basemap import shiftgrid
import xarray as xr
from cdo import Cdo
import numpy as np
import cftime

cdo = Cdo()

class cv:
	def __init__(self, diri, run, ystart, yend):
		self.diri = diri
		self.run = run
		self.ystart = ystart
		self.yend = yend

	def ENSO(self):
		fin = f"{self.diri}/{self.run}/atm/monavg/TS.{self.ystart}-{self.yend}.nc"
		fland = f"{self.diri}/{self.run}/atm/monavg/LANDFRAC.{self.ystart}-{self.yend}.nc"
		f = xr.open_dataset(fin)
		origtime = f.time[10:-9]
		f = cdo.shifttime("2months", input=f, returnXDataset=True)
		flandfrc = xr.open_dataset(fland)


		# Mask land
		data = f["TS"][10:-9,:,:].sel(lat=slice(-5,5), lon=slice(120,360-90))
		data.values = data.values - 273.15
		landmask = flandfrc["LANDFRAC"][10:-9,:,:].sel(lat=slice(-5,5), lon=slice(120,360-90))

		# Remove monthly long term means
		for i in range(len(data.time.values)):
			month = data[i,:,:]["time.month"].values
			data.values[i,:,:] = data.values[i,:,:] - data.sel(time=data["time.month"]==month).mean("time").values
		data.values[landmask.values>0.5] = np.nan
		data.to_netcdf("test.nc")
		sys.exit()

		# Calculate November-March average
		dayspermonth = np.array(origtime.dt.days_in_month.values, dtype=np.float32)
		months = np.arange(1,13,1)
		for i in range(len(dayspermonth)):
			mon = months[(i+10)%12]
			if mon==4 or mon==5 or mon==6 or mon==7 or mon==8 or mon==9 or mon==10:
				dayspermonth[i] = 0

		weight = dayspermonth/(30.+31.+31.+28.+31)
		data.values = data.values * weight[:, np.newaxis, np.newaxis]
		data = data.groupby("time.year").sum()


	def NAO(self, seas):
		# Calculates NAO for seasonal averages,
		# and saves to file
		for s in seas:
			fin = f"{self.diri}/{self.run}/atm/{s}avg/PSL.{self.ystart}-{self.yend}.nc"
			f = xr.open_dataset(fin)
			data = f["PSL"]

			data.values = data.values - data.mean("time").values
			area = cdo.gridarea(input=f, returnXDataset=True)
			area = area.cell_area

			lon = data.lon.values - 360
			data.values, lonx = shiftgrid(-180, data.values, lon)
			data.coords["lon"] = lonx
			area.values, lonx = shiftgrid(-180, area.values, lon)
			area.coords["lon"] = lonx

			data = data.sel(lat=slice(20,80), lon=slice(-90,40))
			area = area.sel(lat=slice(20,80), lon=slice(-90,40))

			solver = Eof(data.values, weights=area.values)
			eof1 = solver.eofsAsCovariance(neofs=1)
			vari = solver.varianceFraction()
			pc1 = solver.pcs(npcs=1, pcscaling=1)

			# Structure into xr.Dataset
			lon = xr.DataArray(data.lon, name="lon", dims=("lon"))
			eof1 = xr.DataArray(eof1[0,:,:], name="pattern", dims=("lat","lon"), coords=[data.lat, lon])
			pc1 = xr.DataArray(pc1[:,0], name="timeseries", dims=("time"), coords=[data.time])
			fout = xr.Dataset({"pattern": eof1, "timeseries": pc1})
			fout.attrs["variance"] = vari[0]*100
			fout.encoding["unlimited_dims"] = "time"
			fout.to_netcdf(f"{self.diri}/{self.run}/atm/{s}avg/NAO.{self.ystart}-{self.yend}.nc")
