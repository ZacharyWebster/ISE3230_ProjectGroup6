import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import re
from geopy.exc import GeocoderTimedOut

# Read your CSV file
df = pd.read_csv(r'C:\Users\zweb3\Downloads\addresses_missing_in_geocode_by_addr_and_city.csv')

print(f"Loaded {len(df)} addresses")
print(f"Columns in your CSV: {list(df.columns)}")

# Initialize geocoder
geolocator = Nominatim(user_agent="facility_geocoder_v2")
# Wrap geocode with a rate limiter (about 1 call per second)
geocode = RateLimiter(
    geolocator.geocode,
    min_delay_seconds=1.1,
    max_retries=2,
    error_wait_seconds=2.0,
)

def clean_address(addr: str) -> str:
    """
    Normalize address spacing and remove some unit/apt noise
    that can confuse Nominatim (e.g., 'STE', 'SUITE', 'UNIT', 'APT', '#').
    """
    if not isinstance(addr, str):
        return ""
    a = addr.strip()
    # Collapse multiple spaces
    a = re.sub(r"\s+", " ", a)
    # Remove common unit markers and everything after them
    # Example: '5132 WALHAM GREEN RD APT. 301' -> '5132 WALHAM GREEN RD'
    unit_keywords = ["APT", "APT.", "UNIT", "STE", "STE.", "SUITE", "#"]
    for kw in unit_keywords:
        pattern = r"\b" + re.escape(kw) + r"\b.*"
        a = re.sub(pattern, "", a, flags=re.IGNORECASE).strip()
    return a

def geocode_address(row):
    # Use correct column names from NameAndAddress.csv
    raw_addr = str(row.get("Site Address", "")).strip()
    city = str(row.get("City", "")).strip()

    if not raw_addr:
        print("✗ Missing Site Address")
        return None, None

    # First attempt: full raw address + city + state + country
    if city:
        full_address = f"{raw_addr}, {city}, Ohio, USA"
    else:
        full_address = f"{raw_addr}, Ohio, USA"

    try:
        location = geocode(full_address)
        if location:
            print(f"✓ Geocoded (full): {full_address}")
            return location.latitude, location.longitude
        else:
            print(f"✗ No result (full): {full_address}")
    except GeocoderTimedOut:
        print(f"✗ Timeout (full): {full_address}")
    except Exception as e:
        print(f"✗ Error (full): {full_address} - {e}")

    # Second attempt: cleaned street (strips APT/UNIT/STE etc.) + city
    cleaned = clean_address(raw_addr)
    if cleaned:
        if city:
            cleaned_full = f"{cleaned}, {city}, Ohio, USA"
        else:
            cleaned_full = f"{cleaned}, Ohio, USA"

        if cleaned_full != full_address:
            try:
                location = geocode(cleaned_full)
                if location:
                    print(f"✓ Geocoded (cleaned): {cleaned_full}")
                    return location.latitude, location.longitude
                else:
                    print(f"✗ No result (cleaned): {cleaned_full}")
            except GeocoderTimedOut:
                print(f"✗ Timeout (cleaned): {cleaned_full}")
            except Exception as e:
                print(f"✗ Error (cleaned): {cleaned_full} - {e}")

    # Third attempt: cleaned street + just state + country
    if cleaned:
        cleaned_state_only = f"{cleaned}, Ohio, USA"
        try:
            location = geocode(cleaned_state_only)
            if location:
                print(f"✓ Geocoded (street+state): {cleaned_state_only}")
                return location.latitude, location.longitude
            else:
                print(f"✗ No result (street+state): {cleaned_state_only}")
        except GeocoderTimedOut:
            print(f"✗ Timeout (street+state): {cleaned_state_only}")
        except Exception as e:
            print(f"✗ Error (street+state): {cleaned_state_only} - {e}")

    print(f"✗ Failed all attempts: {raw_addr} (city: {city})")
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

print("Geocoding complete!")

# Drop rows where geocoding failed
df_clean = df.dropna(subset=['latitude', 'longitude'])

print(f"Successfully geocoded: {len(df_clean)}/{len(df)} addresses")

# Save both full results and clean results
df.to_csv('all_addresses_with_coordinates.csv', index=False)
df_clean.to_csv('successfully_geocoded_addresses.csv', index=False)

print("Saved results:")
print("- all_addresses_with_coordinates.csv (all addresses)")
print("- successfully_geocoded_addresses.csv (only successful geocodes)")

print("\nSample of successfully geocoded addresses:")
print(df_clean[['Site Address', 'City', 'latitude', 'longitude']].head(10))