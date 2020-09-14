import sys
import yaml

sys.path.append("/home/raymond/LGMeval")
import src.viz as viz

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

################
# Plotting resources
################
def plot():
   

for seas in seasons:
  fdir = f"{scratchdir}/{run}/atm/trend/{seas}"
  for var in varlist:
    fname = f"{fdir}/{var}.{ystart_use}-{yend_use}.nc"
    print(fname)
    sys.exit()
