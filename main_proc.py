import yaml, sys
import src

# Get variable dictionary
with open("src/vars/cam.yml","r") as f:
	atmdict = yaml.safe_load(f)



###############
# Atmosphere
###############

def hist_atm(info,atmdict): # Merge atmosphere history files and save to scratch
	# Atmosphere (h0)
	varlist = ["CLDHGH", "CLDLOW", "CLDMED", "CLDTOT", "FLDS", "FLNS", "FLNSC", "FLNT", "FSDS", "FSDSC", "FSNS",
		"FSNSC", "FSNT", "ICEFRAC", "LHFLX", "PRECC", "PRECL", "PRECSC", "PRECSL", "PSL", "SHFLX", "TGCLDCWP",
		"TGCLDIWP", "TMQ", "TS", "U250", "U500", "U850", "V250", "V500", "V850"]
	src.merge_hist(info, "atm", varlist, atmdict, "h0", "monavg")
	varlist = src.calcadd_atm(info, varlist, atmdict, "monavg")
	src.mon2seas(info, "atm", varlist)
	src.mon2ann(info, "atm", varlist)

	# Atmosphere (h1)
	varlist = ["LANDFRAC", "LWCF", "OCNFRAC", "QREFHT", "SWCF", "TREFHT", "U10"]
	src.merge_hist(info, "atm", varlist, atmdict, "h1", "monavg")
	src.mon2seas(info, "atm", varlist)
	src.mon2ann(info, "atm", varlist)

	varlist = ["U", "V", "Z3"]
	src.merge_hist(info, "atm", varlist, atmdict, "h1", "monavg", dimensions=3)
	src.mon2seas(info, "atm", varlist)
	src.mon2ann(info, "atm", varlist)

def proc_atm(info): # Post-process atmospheric fields
	diri = info["run"]["folder"]
	run = info["run"]["name"]
	ystart = info["run"]["ystart"]
	yend = info["run"]["yend"]
	ATMpp = src.pp(diri, run, "atm", ystart, yend)

	varlist = ["ALBEDO", "CLDHGH", "CLDLOW", "CLDMED", "CLDTOT", "FLDS", "FLNS", "FLNSC", "FLNT", "FSDS", "FSDSC", "FSNS", 
		"FSNSC", "FSNSC", "FSNT", "ICEFRAC", "LANDFRAC", "LHFLX", "LWCF", "OCNFRAC", "PRECC", "PRECL", "PRECSC", "PRECSL",
		"PRECT", "PSL", "QREFHT", "RAIN", "SHFLX", "SNOW", "SWCF", "TGCLDCWP", "TGCLDIWP", "TMQ", "TREFHT", "TS", "U10",
		"U250", "U500", "U850", "V250", "V500", "V850", "U", "V", "Z3", "RADTOA"]
	
	#ATMpp.trend(varlist, "annavg", nyears=30)

	ATMpp.timeseries(varlist, "annavg")
	ATMpp.timeseries(varlist, "annavg", region="NH")
	ATMpp.timeseries(varlist, "annavg", region="tropical")
	ATMpp.timeseries(varlist, "annavg", region="SH")



###############
# Climate variability
###############

def climate_variability(info): # Calculate indexes for climate variability
	diri = info["run"]["folder"]
	run = info["run"]["name"]
	ystart = info["run"]["ystart"]
	yend = info["run"]["yend"]

	clim = src.cv(diri, run, ystart, yend)
	clim.ENSO()
	clim.NAO(["DJF","JJA"])






###############
# Main
###############

def main():
	with open("src/vars/cam.yml","r") as f:
        	atmdict = yaml.safe_load(f)
	with open("runs.yml","r") as f:
	        info = yaml.safe_load(f)

	#hist_atm(info,atmdict)
	proc_atm(info)

	#climate_variability(info)
	
main()
