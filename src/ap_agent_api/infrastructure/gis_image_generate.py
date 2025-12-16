import requests
import json
from pyproj import CRS, Transformer

# from ap_agent_api.config import PROPERTY_RESULTS_DIR
from ap_agent_api.domain.models.property import PropertyAddress
from ap_agent_api.domain.utils import get_property_directory

import coloredlogs, logging
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


# --- CONFIGURATION ---

# 1. Address to Geocode
# ADDRESS = "1C Raymel Crescent, Campbelltown, SA 5074"
ADDRESS = "1A Ormbsy Street, Widsor Gardens"
# 2. Target Coordinate Systems
# WGS 84 (Latitude/Longitude) - WKID 4326
WGS84 = CRS.from_epsg(4326)
# Web Mercator - WKID 3857 (Used by the Map Server)
WMERC = CRS.from_epsg(3857)

# 3. Box Size (Level 17 Tile Dimension)
# to get the box size we have to fetch the informaiton from 
# https://location.sa.gov.au/arcgis/rest/services/BaseMaps/Topographic_wmas/MapServer
# Origin: X: -2.0037508342787E7
# Y: 2.0037508342787E7
# • Level ID: 17 [ Start Tile, End Tile ]
# 	○ Resolution: 1.1943285668550503
# 	○ Scale: 4513.988705
# Spatial Reference: 102100  (3857)
# Width/Height: 256 (tile size)
# tile dimension = resolution * tile size
BOX_SIDE_METERS = 305.748113  # Meters

# 4. Map Service URL (SA Geohub Topographic Placeholder)
# This will be used to get the final image
CONTOURMAP_SERVICE_EXPORT_URL = "https://lsa1.geohub.sa.gov.au/arcgis/rest/services/BaseMaps/Topographic_wmas/MapServer/export"
PARCELMAP_SERVICE_EXPORT_URL = "https://lsa1.geohub.sa.gov.au/arcgis/rest/services/BaseMaps/StreetMapCased_wmas/MapServer/export"
ROAD_SERVICE_EXPORT_URL = "https://lsa2.geohub.sa.gov.au/arcgis/rest/services/SAPPA/PropertyPlanningAtlasV17/MapServer/export"
# 5. Geocoding Service URL (SA Geohub Geocoding Placeholder)
GEOCODE_SERVICE_URL = "https://location.sa.gov.au/arcgis/rest/services/Locators/SAGAF_PLUS/GeocodeServer/geocodeAddresses"

# --- STEP 1: Get Geocode Address (from x.com / Geohub) ---
def get_geocode_from_service(address):
    """
    Submits the address to the geocoding service and returns coordinates (in WGS 84).
    """
    logger.debug(f"1. Geocoding Address: {address}")
    
    # Structure the address for batch geocoding (as discussed)
    addresses_payload = {
        "records": [
            {
                "attributes": {
                    "OBJECTID": 1,
                    "Street": address.split(',')[0].strip(),
                    "City": address.split(',')[1].strip(),
                }
            }
        ]
    }
    
    params = {
        "addresses": json.dumps(addresses_payload),
        "f": "json"
    }

    try:
        response = requests.post(GEOCODE_SERVICE_URL, data=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract location from the best match (first candidate)
        if data and 'locations' in data and data['locations']:
            wgs84_x = data['locations'][0]['location']['x']
            wgs84_y = data['locations'][0]['location']['y']
            logger.debug(f"   -> WGS 84 Coordinates (Lat/Lon): X={wgs84_x}, Y={wgs84_y}")
            return wgs84_x, wgs84_y
        else:
            logger.error("   -> ERROR: Geocoding failed or no matches found.")
            return None, None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"   -> ERROR during geocoding request: {e}")
        return None, None


# --- STEP 2: Convert WGS 84 to WKID 3857 (Web Mercator) ---
def transform_coordinates(wgs84_x, wgs84_y):
    """
    Converts WGS 84 (4326) coordinates to Web Mercator (3857) using pyproj.
    """
    logger.debug("2. Converting WGS 84 (4326) to Web Mercator (3857)")
    
    # Create a transformer object
    transformer = Transformer.from_crs(WGS84, WMERC, always_xy=True)
    
    # Perform the transformation
    wm_x, wm_y = transformer.transform(wgs84_x, wgs84_y)
    
    logger.debug(f"   -> Web Mercator Coordinates: X={wm_x:.4f}, Y={wm_y:.4f}")
    return wm_x, wm_y


# --- STEP 3: Calculate Bounding Box (Xmin, Ymin, Xmax, Ymax) ---
def calculate_bounding_box(wm_x, wm_y, box_side):
    """
    Creates a square bounding box centered on the Web Mercator coordinates.
    """
    logger.debug("3. Calculating Bounding Box (Centered on Point)")
    
    buffer = box_side / 2
    
    # XMin = Center X - Buffer
    xmin = wm_x - buffer
    # YMin = Center Y - Buffer
    ymin = wm_y - buffer
    # XMax = Center X + Buffer
    xmax = wm_x + buffer
    # YMax = Center Y + Buffer
    ymax = wm_y + buffer
    
    bbox_string = f"{xmin},{ymin},{xmax},{ymax}"
    logger.debug(f"   -> Bounding Box: {bbox_string}")
    return bbox_string


# --- STEP 4: Use Bounding Box to Get Map Image (from link Y) ---
def get_map_image(bbox_string, url, layers=None):
    """
    Calls the MapServer export function to get the image.
    """
    logger.debug("4. Requesting Map Image from MapServer")
    
    # Define the parameters for the map export
    export_params = {
        "bbox": bbox_string,         # The calculated bounding box
        "bboxSR": 3857,              # The Spatial Reference of the bbox (Web Mercator)
        # "size": "600,600",           # Output image size in pixels (600x600 for a clear square)
        "f": "image"                 # Output format is image (PNG)
    }
    if layers:
        export_params["layers"] = layers

    try:
        # Use GET request for image export
        response = requests.get(url, params=export_params, timeout=20)
        response.raise_for_status()

        return response.content
        
    except requests.exceptions.RequestException as e:
        print(f"   -> ERROR requesting map image: {e}")

def save_image(image_data, filename):
    """
    Saves the binary image data to a file.
    """
    if image_data:
        with open(filename, 'wb') as f:
            f.write(image_data)

def run(address: PropertyAddress):

    address_str = f"{address.street}, {address.suburb}, {address.state}"

    # 1. Get WGS84 Geocode
    wgs84_x, wgs84_y = get_geocode_from_service(address_str)

    if wgs84_x is not None:
        # 2. Convert to Web Mercator (WKID 3857)
        wm_x, wm_y = transform_coordinates(wgs84_x, wgs84_y)

        # 3. Calculate Bounding Box
        bbox = calculate_bounding_box(wm_x, wm_y, BOX_SIDE_METERS)
        
        # 4. Get Contour Map Image
        contour_image = get_map_image(bbox, CONTOURMAP_SERVICE_EXPORT_URL)

        #5. Get Elevation Data (Optional - Not Implemented)
        parcel_image = get_map_image(bbox, PARCELMAP_SERVICE_EXPORT_URL)

        #6. Get Road Map Image
        road_image = get_map_image(bbox, ROAD_SERVICE_EXPORT_URL, layers="show:17")

        # Save images to files
        output_dir = get_property_directory(address)
        
        save_image(contour_image, output_dir / "contour_map.png")
        save_image(parcel_image, output_dir / "parcel_map.png")
        save_image(road_image, output_dir / "road_map.png")
        logger.debug(f"   -> SUCCESS: Contour map image saved in '{output_dir}'")

    return output_dir

# --- MAIN EXECUTION ---

if __name__ == "__main__":
    # address = PropertyAddress(
    #     street="1A Ormbsy Street",
    #     suburb="Widsor Gardens",
    #     state="SA",
    #     postcode="5087"
    # )
    # address = PropertyAddress(
    #     street="1C Raymel Crescent",
    #     suburb="Campbelltown",
    #     state="SA",
    #     postcode="5074"
    # )
    address = PropertyAddress(
        street="47 A Reid Ave",
        suburb="Felixstow",
        state="SA",
        postcode="5070"
    )
    run(address)