'''#######################################################
# AB_RandomMovement.py
#
# Created: 03/27/13
# Author: ESRI
########################################################'''

def getABlocations(array1):
    ind = array1.nonzero()
    return ind

def randomABMovment(arrayABlocs, arrayABsus, maxDist):
    #Get current Ash Borer locations from array (1 = infested; 0 = not infested)
    ABlocations = getABlocations(arrayABlocs)
    #Reduce array for every third
    ABlocations3 = ABlocations[0][::3],ABlocations[1][::3]
    nlocs = len(ABlocations3[0])
    #for each input AB location
    for i in range(nlocs):
        p = ABlocations3[0][i],ABlocations3[1][i]
        arcpy.AddMessage("current location: %s" %(str(p)))
        # Test three random movements
        for i in range(3):
            #1. Generate random movement distance.
            randomXYdist = getRandomXYDist(maxDist)

            #2. New location for Ash Borer movement
            ABlocation_new = p[0] - randomXYdist[0], p[1] + randomXYdist[1]
            arcpy.AddMessage("new location %s" %(str(ABlocation_new)))

            #3. If new location is susceptible AB Infest = TRUE
            if arrayABlocs[ABlocation_new] != 1:
                if arrayABsus[ABlocation_new] >= 8:
                    arrayABlocs[ABlocation_new] = 1
                    arcpy.AddMessage("Infested")
                else:
                    arcpy.AddMessage("Not Infested")
    return arrayABlocs

def getRandomXYDist(maxDist):
#Using exponential distribution.
#lambd is 1.0 divided by the desired mean. It should be nonzero.
    x,y = 100,100
    ypos,yneg = 100,-100
    lambd = maxDist - 10
    while x >= maxDist:
        x = int(random.expovariate(1.0/lambd))
    while y < - maxDist or y > maxDist:
        while ypos >= maxDist:
            ypos = int(random.expovariate(1.0/lambd))
        while yneg <= -(maxDist):
            yneg = int(random.expovariate(-1.0/lambd))
            y = ypos + yneg
    return (x,y)


'''==== start script ======'''

import sys, os, random
import arcpy
from arcpy.sa import *

arcpy.CheckOutExtension('Spatial')

#Environment settings
from arcpy import env
env.overwriteOutput = 1
env.workspace = os.path.join(sys.path[0],"output","scratch.gdb")
env.scratchWorkspace = os.path.join(sys.path[0],"output","scratch.gdb")
env.extent = os.path.join(sys.path[0],"data","Data.gdb","Studyarea")

#local variables
inABlocRas = arcpy.Raster(os.path.join(sys.path[0],"data","Data.gdb",
                                       "ab_infested_pntras"))
inSusceptRas = arcpy.Raster(os.path.join(sys.path[0],"data","Data.gdb",
                                         "flight_sus_6040"))
outABLocRand = "ABLocsRand_1"
nSims = 3

arcpy.AddMessage("Calculating random movements...")
for i in range(0,nSims):
    #===========================================================
    #1. Create numPY array from input Raster
    #===========================================================
    arrayABlocs = arcpy.RasterToNumPyArray(inABlocRas)
    arrayABSuscept = arcpy.RasterToNumPyArray(inSusceptRas)

    #===========================================================
    #2. Custom Function: AB moves random EXP distance and infest
    #===========================================================
    arrayNewABlocs = randomABMovment(arrayABlocs, arrayABSuscept, 100)

    #===========================================================
    #3. Convert array back to raster
    #===========================================================
    ABNewLocsRas = arcpy.NumPyArrayToRaster(arrayNewABlocs,
                                            inABlocRas.extent.lowerLeft,
                                            inABlocRas.meanCellWidth)
    ABNewLocsRas.save(outABLocRand)
    arcpy.RasterToPoint_conversion(Con(ABNewLocsRas,1),
                                   "{0}{1}".format(outABLocRand,i))
    
    arcpy.AddMessage("Complete. New infestations via random movement... {}".format(outABLocRand))

'''====  end script =================================='''