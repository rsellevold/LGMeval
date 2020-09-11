import yaml, sys
import src

##########
# Merging of history files
##########

# Get variable dictionary
with open("src/vars/cam.yml","r") as f:
	atmdict = yaml.safe_load(f)

def hist_atm(info,atmdict):
	# Atmosphere (h0)
	varlist = ["CLDHGH", "CLDLOW", "CLDMED", "CLDTOT", "FLDS", "FLNS", "FLNSC", "FLNT", "FSDS", "FSDSC", "FSNS",
		"FSNSC", "FSNT", "ICEFRAC", "LHFLX", "PRECC", "PRECL", "PRECSC", "PRECSL", "PSL", "SHFLX", "TGCLDCWP",
		"TGCLDIWP", "TMQ", "TS", "U250", "U500", "U850", "V250", "V500", "V850"]
	src.merge_hist(info, "atm", varlist, atmdict, "h0", "monavg")
	varlist = src.calcadd(info, "atm", varlist, atmdict, "monavg")
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


##########
# Climate variability
##########

def climate_variability(info):
	diri = info["run"]["folder"]
	run = info["run"]["name"]
	ystart = info["run"]["ystart"]
	yend = info["run"]["yend"]

	clim = src.cv(diri, run, ystart, yend)
	clim.NAO(["DJF","JJA"])

##########
# Main
##########

def main():
	with open("src/vars/cam.yml","r") as f:
        	atmdict = yaml.safe_load(f)
	with open("runs.yml","r") as f:
	        info = yaml.safe_load(f)

	hist_atm(info,atmdict)
	climate_variability(info)
	

main()
