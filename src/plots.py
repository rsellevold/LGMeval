import cartopy.crs as ccrs

class plots:

	def __init__(self):
		None

	##########
	# Mapplots
	##########

	def map_trend(self,data,p):
		fig = plt.figure(self.figsize)
		ax1 = plt.subplot(1,1,1, projection=self.proj)
		ax1.coastlines(resolution="50m", linewidth=0.5)
		ax1.set_title(f"{data.long_name} (data.units)", loc="left")
		plot = ax1.pcolormesh(data.lon.values, data.lat.values, data.values, data.clevs, data.norm, data.cmap, transform=self.proj)
		ax1.contourf(data.lon.values, data.lat.values, p, [self.significance, 1.0], hatches=["..."], alpha=0.0, transform=self.proj)
		plt.colorbar(plot)
		plt.savefig(f'{self.plotdir}/map_trend/{data.name}.{self.ext}')
