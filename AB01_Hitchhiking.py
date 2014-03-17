'''#######################################################
# AB_HitchHiker.py
#
# Created: 03/27/13
# Author: ESRI
#######################################################'''

#=============================
# 1. Import Spatial Analyst
#=============================
import sys, os
import arcpy
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")

#Environment settings
from arcpy import env
env.overwriteOutput = 1
env.extent = os.path.join(sys.path[0],"data","Data.gdb","Studyarea")
env.snapRaster = os.path.join(sys.path[0],"data","VT","elev")
env.cellSize = 1000
env.workspace = os.path.join(sys.path[0],"output","scratch.gdb")
env.scratchWorkspace = os.path.join(sys.path[0],"output","scratch.gdb")

#Input and output parameters (layers)
inputAB = os.path.join(sys.path[0],"data","Data.gdb","AB_sampled")
inputData = [inputAB, os.path.join(sys.path[0],"data","Data.gdb","campgrounds"), 
    os.path.join(sys.path[0],"data","Data.gdb","Mills"), 
    os.path.join(sys.path[0],"data","Data.gdb","Urban"), 
    os.path.join(sys.path[0],"data","Data.gdb","MajorRoads")]
inputWeights =  [3,2,3,1,2]
ashLHRas = os.path.join(sys.path[0],"data","Data.gdb","ash_likelyhood")
nSims = 3

for i in range(0,nSims):
    HHlikely = ApplyEnvironment(0)                              #create constant raster                            
    weight_sum = 0                                              
    n = 0                                                       

    arcpy.AddMessage("="*40+"\nApplying non linear function decay and normalizing result for,")
    # Loop through each of the input datasets    
    for data in inputData:                                      
        arcpy.AddMessage("{}...".format(os.path.basename(data)))
        weight = int(inputWeights[n])                           # Get the weight which corresponds to the dataset

        #=============================
        # 2. Execute EucDistance and get raster property maximum distance
        #=============================
        eucdistout = EucDistance(data)                          
        maxdist = eucdistout.maximum                            

        #=============================
        # 3. Calculate non-linear decay distance, weight and combine rasters 
        #=============================
        out_exp = Power(0.05,(eucdistout/maxdist)) * weight     
        HHlikely += out_exp                                     
        weight_sum += weight                                    
        n += 1                                                  

    HHlikelihood = HHlikely/weight_sum                          # Divide the total susceptibility by the sum of the weights to normalize the result
    HHlikelihood.save("HH_likelihood")                          

    #=============================
    # 4. Find new infested areas 
    #=============================
    arcpy.AddMessage("="*40+"\nRunning hitch hiker susceptibility...")
    
    outsus = Con(HHlikelihood > 0.5, 1,'')
    outsus_areas = arcpy.RasterToPolygon_conversion(outsus,"#",)
    outsus_areasd = arcpy.Dissolve_management(outsus_areas,"#")
    out_randpnts = arcpy.CreateRandomPoints_management(
                    arcpy.env.scratchWorkspace,"rand_locs",outsus_areasd,'',25)
    hh_susceptible = ZonalStatistics(out_randpnts,"OID",ashLHRas,"MEAN","DATA")

    #Test if location will be infested.
    outInfested = Con(hh_susceptible > 5, 1,'')
    outInfested.save("HH_newInfested1")

    #Append the new infested locations as input to the next
    hhpnts = arcpy.RasterToPoint_conversion(outInfested,"HH_pnts{}".format(i))
    ABnewlocs = arcpy.Append_management(hhpnts,inputAB,"NO_TEST")

    arcpy.AddMessage("="*40+"\nCompleted {} simulation ...".format(i))

arcpy.AddMessage("Complete. New infestations by hitch hiking... {}".format(
                  ABnewlocs))

