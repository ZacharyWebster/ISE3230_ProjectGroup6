import pandas as pd
import geopandas as gpd
from geopy.geocoders import Nominatim
from shapely.geometry import Point

# Read your already geocoded CSV
# Change path as needed for your computer 
df = pd.read_csv(r'C:\Users\zweb3\OneDrive\Documents\ISE-3230\distinct_Address_License.csv')

# Remove any rows without coordinates
df = df.dropna(subset=['latitude', 'longitude'])

# Create geometry column from lat/lon
geometry = [Point(lon, lat) for lon, lat in zip(df['longitude'], df['latitude'])]

# Create GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

print(f"Created GeoDataFrame with {len(gdf)} locations")

# Save as GeoJSON for mapping
gdf.to_file("facilities.geojson", driver='GeoJSON')
print("Saved as 'facilities.geojson'")

# You can also save as shapefile
gdf.to_file("facilities.shp")
print("Saved as 'facilities.shp'")

# Quick plot (if you have matplotlib)
import matplotlib.pyplot as plt
gdf.plot(markersize=5, figsize=(10, 8))
plt.title("Facility Locations")
plt.savefig('facilities_map.png')
print("Saved map as 'facilities_map.png'")
