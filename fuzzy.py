import arcpy
from arcpy.sa import *
from arcpy import env

#define workspace
env.workspace = "./"
env.extent = 'KhorramAbad.shp'
#Flood Zoning

#Eucldean distacne calculate
outEucDistance_river = arcpy.gp.EucDistance_sa("river.shp", '#', '#', "./eucriver")


#Fuuzy membership calculate
outFzyMember_slope_better = FuzzyMembership("./slope.tif", FuzzyLinear(3, 15))
outFzyMember_slope_worse = FuzzyMembership("./slope.tif", FuzzyLinear(15, 3))

outFzyMember_river_worse = FuzzyMembership(outEucDistance_river, FuzzyLinear(0, 6000))
outFzyMember_river_better = FuzzyMembership(outEucDistance_river, FuzzyLinear(6000, 0))

outFzyMember_dem_worse = FuzzyMembership("./dem.tif", FuzzyLinear(500, 3000))
outFzyMember_dem_better = FuzzyMembership("./dem.tif", FuzzyLinear(3000, 500))

outFzyMember_soil_better = FuzzyMembership("./soil.tif", FuzzyLinear(1, 9))
outFzyMember_soil_worse = FuzzyMembership("./soil.tif", FuzzyLinear(9, 1))

outFzyMember_rain_better = FuzzyMembership("./rain.tif", FuzzyLinear(35, 56))
outFzyMember_rain_worse = FuzzyMembership("./rain.tif", FuzzyLinear(56, 35))

# Define Rules and Knowledge base
expressions = []
weights = [49, 75, 64, 90, 72, 98, 87, 113, 28, 54, 43, 69, 51, 77, 66, 92, 86, 112, 101, 127, 86, 135, 124, 150, 65, 91, 80, 114, 80, 114, 103, 129]

for i in range(1, 33):
    fuzzy_overlay = f'outFzyMember_slope_worse * {weight[i-1]}'
    for j in range(1, 5):
        fuzzy_overlay += f' * outFzyMember_{"river_worse" if j == 1 else "river_better" if j == 2 else "dem_worse" if j == 3 else "soil_worse" if j == 4 else "soil_better"}'
    expressions.append(f'FuzzyOverlay([{fuzzy_overlay}], "AND", "0.9")')

# Use Raster Calculator
denominatorZoning = ' + '.join(expressions)
numeratorZoning = ' + '.join([f'{expressions[i-1]} * {weights[i-1]}' for i in range(1, 33)])
finalZoning = numeratorZoning/denominatorZoning


#Fuzzy approach for site selection
#Eucldean distacne calculate
outEucDistance_health = arcpy.gp.EucDistance_sa("health.shp", '#', '#', "./eucdhealth")

outEucDistance_residental = arcpy.gp.EucDistance_sa("residental.shp", '#', '#', "./eucdresidental")

outEucDistance_roads = arcpy.gp.EucDistance_sa("roads.shp", '#', '#', "./eucdroads")


#Fuuzy membership calculate
outFzyMember_residental_worse = FuzzyMembership(outEucDistance_residental, FuzzyLinear(7000, 2000))
outFzyMember_residental_better = FuzzyMembership(outEucDistance_residental, FuzzyLinear(2000, 7000))

outFzyMember_zoning_worse = FuzzyMembership(finalZoning, FuzzyLinear(124, 48))
outFzyMember_zoning_better = FuzzyMembership(finalZoning, FuzzyLinear(48, 124))

outFzyMember_slope_better = FuzzyMembership("./slope.tif", FuzzyLinear(3, 15))
outFzyMember_slope_worse = FuzzyMembership("./slope.tif", FuzzyLinear(15, 3))

outFzyMember_roads_better = FuzzyMembership(outEucDistance_roads, FuzzyLinear(300, 1100))
outFzyMember_roads_worse = FuzzyMembership(outEucDistance_roads, FuzzyLinear(1100, 300))

outFzyMember_health_better = FuzzyMembership(outEucDistance_health, FuzzyLinear(1000, 3500))
outFzyMember_health_worse = FuzzyMembership(outEucDistance_health, FuzzyLinear(3500, 1000))

# Define the input fuzzy members
fuzzy_members = [
    "residental_worse",
    "zoning_worse",
    "slope_better",
    "roads_better",
    "health_worse",
    "health_better",
    "slope_worse",
    "roads_worse",
    "zoning_better",
    "residental_better"
]

# Initialize the denominator and numerator
denominator = 0
numerator = 0

# Iterate through the fuzzy members and calculate the overlay
for i in range(1, 33):
    Rs = FuzzyOverlay([getattr(outFzyMember, fuzzy_member) for fuzzy_member in fuzzy_members], 'AND', '0.9')
    denominator += Rs
    numerator += Rs * (129 - 22 * (i % 2))  # Using the pattern in the given code

# Use the denominator and numerator in further calculations

finalSiteSelection = numerator/denominator






#Save and export Zoning needed data and final map

# Save the rasters
for raster_name, raster in zip(["dem_better", "dem_worse", "rain_better", "rain_worse", "slope_better", "slope_worse", "soil_better", "soil_worse", "river_better", "river_worse"],
                               [outFzyMember_dem_better, outFzyMember_dem_worse, outFzyMember_rain_better, outFzyMember_rain_worse, outFzyMember_slope_better, outFzyMember_slope_worse, outFzyMember_soil_better, outFzyMember_soil_worse, outFzyMember_river_better, outFzyMember_river_worse]):
    raster.save(f"./fzym{raster_name}.tif")

# Save the rules
for raster_name, raster in zip(["R1", "R17", "R32"], [R1, Rs17, Rs32]):
    raster.save(f"./rules/{raster_name}.tif")

# Save the final results
for raster_name, raster in zip(["finalSiteSelection", "finalZoning"], [finalSiteSelection, finalZoning]):
    raster.save(f"./rules/{raster_name}.tif")

# Save the Euclidean distance rasters
for raster_name, raster in zip(["eucdhealth", "eucdresidental", "eucdroads", "eucriver"], [outEucDistance_health, outEucDistance_residental, outEucDistance_roads, outEucDistance_river]):
    raster.save(f"./{raster_name}")
