import pandas as pd
from geopy.geocoders import Nominatim
import time

# Read your CSV file
df = pd.read_csv(r'C:\Users\zweb3\OneDrive\Documents\ISE-3230\distinct_Address_License.csv')

print(f"Loaded {len(df)} addresses")
print(f"Columns in your CSV: {list(df.columns)}")

# Initialize geocoder
geolocator = Nominatim(user_agent="facility_geocoder_v1")

def geocode_address(row):
    try:
        # Use the actual column names from your CSV
        full_address = f"{row['site_address']}, {row['city']}, Ohio, USA"
        location = geolocator.geocode(full_address)
        
        if location:
            print(f"✓ Geocoded: {row['site_address']}")
            return location.latitude, location.longitude
        else:
            print(f"✗ Failed: {row['site_address']}")
            return None, None
    except Exception as e:
        print(f"✗ Error: {row['site_address']} - {e}")
        return None, None

# Add coordinate columns (they don't exist yet)
df['latitude'] = None
df['longitude'] = None

print("Starting geocoding...")

# Geocode each address
for index, row in df.iterrows():
    lat, lon = geocode_address(row)
    df.at[index, 'latitude'] = lat
    df.at[index, 'longitude'] = lon
    time.sleep(1.1)  # Rate limiting

print("Geocoding complete!")

# NOW you can drop rows where geocoding failed
df_clean = df.dropna(subset=['latitude', 'longitude'])

print(f"Successfully geocoded: {len(df_clean)}/{len(df)} addresses")

# Save both full results and clean results
df.to_csv('all_addresses_with_coordinates.csv', index=False)
df_clean.to_csv('successfully_geocoded_addresses.csv', index=False)

print("Saved results:")
print(f"- all_addresses_with_coordinates.csv (all addresses)")
print(f"- successfully_geocoded_addresses.csv (only successful geocodes)")

# Show sample of results
print("\nSample of successfully geocoded addresses:")
print(df_clean[['site_address', 'city', 'latitude', 'longitude']].head(10))
