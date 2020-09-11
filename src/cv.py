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
		fin = f"{self.diri}/{self.run}/atm/hist/monavg/TS.{self.ystart}-{self.yend}.nc"
		fland = f"{self.diri}/{self.run}/atm/hist/monavg/LANDFRAC.{self.ystart}-{self.yend}.nc"
		f = xr.open_dataset(fin)

		origtime = f.time[10:-2]
		f = cdo.shifttime("2months", input=f, returnXDataset=True)
		flandfrc = xr.open_dataset(fland)

		farea = cdo.gridarea(input=f, returnXDataset=True)
		farea = farea.sel(lat=slice(-5,5), lon=slice(120,360-90))

		# Mask land
		data = f["TS"][10:-2,:,:].sel(lat=slice(-5,5), lon=slice(120,360-90))
		data.values = data.values - 273.15
		landmask = flandfrc["LANDFRAC"][10:-2,:,:].sel(lat=slice(-5,5), lon=slice(120,360-90))

		# Subtract monthly mean climatology
		data_reshape = np.reshape(data.values, (int(len(data.time)/12),12,len(data.lat),len(data.lon)))
		for mon in range(12):
			data_reshape[:,mon,:,:] -= np.mean(data_reshape[:,mon,:,:], axis=0)[np.newaxis,...]
		data.values = np.reshape(data.values, data.values.shape)
		del(data_reshape)
		data.values[landmask.values>0.5] = 0

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
		
		# Calculate EOF
		solver = Eof(data.values, weights=farea.cell_area.values)
		eof1 = solver.eofsAsCovariance(neofs=1)
		vari = solver.varianceFraction()
		pc1 = solver.pcs(npcs=1, pcscaling=1)

		# Structure into xr.Dataset
		lon = xr.DataArray(data.lon, name="lon", dims=("lon"))
		eof1 = xr.DataArray(eof1[0,:,:], name="pattern", dims=("lat","lon"), coords=[data.lat, lon])
		pc1 = xr.DataArray(pc1[:,0], name="timeseries", dims=("time"), coords=[data.year])
		fout = xr.Dataset({"pattern": eof1, "timeseries": pc1})
		fout.attrs["variance"] = vari[0]*100
		fout.encoding["unlimited_dims"] = "time"
		odir = f"{self.diri}/{self.run}/atm/cv/annavg"
		os.system(f"mkdir -p {odir}")
		fout.to_netcdf(f"{odir}/ENSO.{self.ystart}-{self.yend}.nc")


		f.close()
		flandfrc.close()
		farea.close()


	def NAO(self, seas):
		# Calculates NAO for seasonal averages,
		# and saves to file
		for s in seas:
			fin = f"{self.diri}/{self.run}/atm/hist/{s}avg/PSL.{self.ystart}-{self.yend}.nc"
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
			odir = f"{self.diri}/{self.run}/atm/cv/{s}avg"
			os.system(f"mkdir -p {odir}")
			fout.to_netcdf(f"{odir}/NAO.{self.ystart}-{self.yend}.nc")