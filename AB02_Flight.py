'''######################################################
# AB_Flight.py
#
# Created: 03/27/13
# Author: ESRI
######################################################'''

import sys, os
import arcpy
from arcpy.sa import *
arcpy.CheckOutExtension('Spatial')

#Environment settings
from arcpy import env
env.overwriteOutput = 1
env.workspace = os.path.join(sys.path[0],"output","scratch.gdb")
env.scratchWorkspace = os.path.join(sys.path[0],"output","scratch.gdb")

#local variables
infestedRas = arcpy.Raster(os.path.join(sys.path[0],"data","Data.gdb",
                                        "ab_infested_pntras"))
inSuseptRas = arcpy.Raster(os.path.join(sys.path[0],"data","Data.gdb",
                                        "flight_sus_6040"))
outRaster = os.path.join(env.scratchWorkspace,"ABFly_locsnew")

dictDist = {"spring":5,"summer":20,"fall":10}
counter = 0

for season in ["spring","summer","fall"]:
    arcpy.AddMessage("Calculating flight model...{}".format(season))
    #=============================
    # 1. Create neighborhood class
    #=============================
    nbr_ABrange = NbrWedge(dictDist[season], -180, 0, "Cell")
    outFocalStatRas = FocalStatistics(infestedRas,nbr_ABrange,"SUM","DATA")

    #=============================
    # 2. Test if Location is infested
    #=============================
    outNewAB = Con(outFocalStatRas  & Con(inSuseptRas == 10,1,0),
                   1,Con(infestedRas > 0,1,0))
    outNewAB.save("NewAB_locsF_1{}_{}".format(counter,season))
    counter +=1
    infestedRas = outNewAB

arcpy.AddMessage("Complete. New infestations via flight... {}".format(outNewAB))