import math


# DMS to decimal degrees converter
def dms_to_decimal(dms_str):
    """
    Convert DMS (Degree Minute Second) string to decimal degrees.
    Example format: "51°31'06\"N" -> 51.51833333333333
    """
    # Extract direction character
    direction = dms_str[-1].upper()
    num_part = dms_str[:-1].replace('"', '').replace('°', ' ').replace("'", ' ').strip()

    # Split into components
    parts = num_part.split()
    degrees = float(parts[0])
    minutes = float(parts[1]) if len(parts) > 1 else 0.0
    seconds = float(parts[2]) if len(parts) > 2 else 0.0

    # Calculate decimal value
    decimal = degrees + minutes / 60 + seconds / 3600

    # Adjust for direction
    if direction in ['S', 'W']:
        decimal = -decimal

    return decimal


# Haversine distance calculator
def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate great-circle distance between two points
    using Haversine formula (in kilometers)
    """
    # Earth radius (km)
    R = 6371.0

    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Calculate differences
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    # Haversine formula
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Calculate distance
    distance = R * c
    return distance


# Location database creator
def create_location_database():
    """
    Create coordinate database based on table data
    """
    location_data = [
        ["NHS Blood Centre (Filton)", "Start", "51°31'06\"N", "2°33'55\"W"],
        ["South Bristol NHS Community Hospital", "Start", "51°24'45\"N", "2°34'59\"W"],
        ["UWE Health Tech Hub", "Start", "51°30'03\"N", "2°33'07\"W"],
        ["Southmead Hospital", "Destination", "51°29'45\"N", "2°35'29\"W"],
        ["Bristol Royal Infirmary (BRI)", "Destination", "51°27'29\"N", "2°35'49\"W"],
        ["St Michael's Hospital", "Destination", "51°27'32\"N", "2°35'58\"W"],
        ["Eastville Medical Centre", "Destination", "51°28'13\"N", "2°33'44\"W"],
        ["Fishponds Primary Care Centre", "Destination", "51°28'47\"N", "2°31'36\"W"],
        ["Bristol Haematology and Oncology Centre (BHOC)", "Destination", "51°27'30\"N", "2°35'51\"W"],
        ["Emersons Green NHS Treatment Centre", "Destination", "51°30'12\"N", "2°29'47\"W"],
        ["Lawrence Hill Health Centre", "Destination", "51°27'27\"N", "2°34'19\"W"],
        ["Montpelier Health Centre", "Destination", "51°28'01\"N", "2°35'21\"W"]
    ]

    location_db = {}

    for row in location_data:
        name = row[0]
        lat_str = row[2]
        lon_str = row[3]

        # Convert coordinates
        lat = dms_to_decimal(lat_str)
        lon = dms_to_decimal(lon_str)

        location_db[name] = {"lat": lat, "lon": lon}

    return location_db


# Distance calculator function
def calculate_distance(location_a, location_b):
    """
    Calculate straight-line distance between two locations

    Parameters:
    location_a (str): Name of first location
    location_b (str): Name of second location

    Returns:
    float: Distance in kilometers between locations
    """
    # Create location database
    db = create_location_database()

    # Verify locations exist in database
    if location_a not in db:
        raise ValueError(f"Location A '{location_a}' not found in database")

    if location_b not in db:
        raise ValueError(f"Location B '{location_b}' not found in database")

    # Get coordinates
    coord_a = db[location_a]
    coord_b = db[location_b]

    # Calculate distance
    distance = haversine_distance(
        coord_a["lat"], coord_a["lon"],
        coord_b["lat"], coord_b["lon"]
    )

    return round(distance, 2)  # Return rounded value


# Example usage
if __name__ == "__main__":
    # Test cases
    locations = [
        ("NHS Blood Centre (Filton)", "Southmead Hospital"),
        ("UWE Health Tech Hub", "Emersons Green NHS Treatment Centre"),
        ("South Bristol NHS Community Hospital", "Lawrence Hill Health Centre")
    ]

    # Print header
    print("Medical Facility Distance Calculator")
    print("=" * 50)

    # Calculate and display distances
    for loc1, loc2 in locations:
        try:
            distance = calculate_distance(loc1, loc2)
            print(f"Distance from '{loc1}' to '{loc2}' is {distance} km")
        except ValueError as e:
            print(f"Error: {e}")

    print("\nAll Medical Facilities:")
    db = create_location_database()
    for facility in db:
        print(f"- {facility}")

    # Test invalid location
    try:
        print("\nTesting invalid location...")
        distance = calculate_distance("NHS Blood Centre (Filton)", "Invalid Facility")
    except ValueError as e:
        print(f"Error: {e}")

