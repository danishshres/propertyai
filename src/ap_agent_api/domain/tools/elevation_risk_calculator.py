import cv2
import numpy as np
import math
from typing import Dict, List, Tuple
from matplotlib import pyplot as plt
import random

import logging
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
CENTER_PIXEL = (200, 200)  # Assuming a 600x600 image center for the property
RISK_RINGS = [
    (0, 30, 100, "High Risk (Immediate Property)"),
    (30, 80, 50,  "Moderate Risk (Adjacent Properties)"),
    (80, 200, 25, "Low Risk (Neighborhood Scale)"),
]

# --- IMAGE PROCESSING FUNCTIONS ---
def subtract_roads_from_contours(contour_img_path: str) -> np.ndarray:
    """
    Loads two images, converts them to grayscale, and subtracts the road features
    from the contour map to isolate only the elevation lines.
    
    Returns: A binary image where white pixels represent contours.
    """
    print("1. Isolating Contour Lines using Image Subtraction...")
    
    # Load images as grayscale
    # NOTE: The images must be the same size and perfectly aligned.
    contour_img = cv2.imread(contour_img_path)
    img_hsv=cv2.cvtColor(contour_img, cv2.COLOR_BGR2HSV)
    img_bin = cv2.cvtColor(contour_img, cv2.COLOR_BGR2GRAY)
    _, img_bin = cv2.threshold(img_bin, 230, 255, cv2.THRESH_BINARY_INV)

    # Removing the roads.
    # lower mask (0-10)
    lower_orange = np.array([0, 140, 200])
    upper_orange = np.array([10, 255, 255])
    road_mask = cv2.inRange(img_hsv, lower_orange, upper_orange)

    # or your HSV image, which I *believe* is what you want
    road_hsv = contour_img.copy()
    road_hsv[np.where(road_mask==0)] = 0

    # Removing the watermarks for the roads
    lower_black = np.array([0, 0, 50])
    upper_black = np.array([179, 40, 230])
    label_mask = cv2.inRange(img_hsv, lower_black, upper_black)
    labels_hsv = contour_img.copy()
    labels_hsv[np.where(label_mask==0)] = 0

    label_bin = cv2.cvtColor(labels_hsv, cv2.COLOR_BGR2GRAY)
    _, label_bin = cv2.threshold(label_bin, 10, 255, cv2.THRESH_BINARY)
    label_bin = cv2.dilate(label_bin, None, iterations=2)

    road_bin = cv2.cvtColor(road_hsv, cv2.COLOR_BGR2GRAY)
    _, road_bin = cv2.threshold(road_bin, 10, 255, cv2.THRESH_BINARY)
    road_bin = cv2.dilate(road_bin, None, iterations=2)

    isolated_contours = img_bin - road_bin - label_bin
    _, isolated_contours = cv2.threshold(isolated_contours, 10, 255, cv2.THRESH_BINARY)
    # cv2.morphologyEx(isolated_contours, cv2.MORPH_CLOSE, np.ones((3,3), np.uint8), isolated_contours, iterations=1)
    cv2.dilate(isolated_contours, None, isolated_contours, iterations=3)

    # plt.subplots(1,4, figsize=(15,5))
    # plt.subplot(1,4,1)
    # plt.imshow(img_bin, cmap='gray')
    # plt.title("Original HSV Image")
    # plt.subplot(1,4,2)
    # plt.imshow(road_bin, cmap='gray')
    # plt.title("Road Binary Image")
    # plt.subplot(1,4,3)
    # plt.imshow(label_bin, cmap='gray')
    # plt.title("Label Binary Image")
    # plt.subplot(1,4,4)
    # plt.imshow(isolated_contours, cmap='gray')
    # plt.title("Isolated Contours")
    # plt.show()
    return isolated_contours

def get_contour_pixels(isolated_contours: np.ndarray) -> List[Tuple[int, int]]:
    """
    Finds the coordinates of all pixels that belong to a contour line.
    """
    # Find all white pixels (where the value is 255)
    contour_coords = np.argwhere(isolated_contours == 255)
    # The result is (row, col) which corresponds to (y, x)
    return [(c, r) for r, c in contour_coords]

# --- RISK ASSESSMENT FUNCTION ---

def assess_ring_risk(contour_pixels: List[Tuple[int, int]], center: Tuple[int, int], rings: List[Tuple[int, int, int, str]]) -> Tuple[Dict[str, Dict], float]:
    """
    Calculates the number of contour pixels (elevation changes) within concentric rings
    radiating from the property center.
    """
    logger.debug("Assessing Elevation Risk based on Contour Density in Rings...")
    
    total_risk = 0.0
    # Initialize dictionary to store results for each ring
    risk_data = {r[3]: {"count": 0, "density": 0.0} for r in rings}
    
    # Define the image size (assuming square)
    # img_size = isolated_contours.shape[0] 
    
    # Calculate the area of each ring (A = pi * R^2) for density calculation
    ring_areas: Dict[str, float] = {}
    
    prev_r2_area = 0.0
    for r_min, r_max, factor, name in rings:
        r_max_area = math.pi * (r_max ** 2)
        # Area of the current ring is the difference from the previous ring's outer area
        ring_area = r_max_area - prev_r2_area
        ring_areas[name] = ring_area / factor  # Adjusted by risk factor
        prev_r2_area = r_max_area

    # Iterate through every detected contour pixel
    cx, cy = center
    for px, py in contour_pixels:
        # Calculate the Euclidean distance from the center
        distance = math.hypot(px - cx, py - cy)
        # Determine which ring the pixel falls into
        for r_min, r_max, factor, name in rings:
            if r_min <= distance < r_max:
                risk_data[name]["count"] += 1
                break
                
    # Calculate density for comparison (Count / Area)
    for name, data in risk_data.items():
        if ring_areas[name] > 0:
            data["density"] = data["count"] / ring_areas[name]
            total_risk += data["density"]
    return risk_data, min(total_risk, 100)  # Cap total risk at 100

def extract_contour_lines(binary_img, epsilon=1.5):
    contours, _ = cv2.findContours(
        binary_img,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_NONE
    )
    contour_lines = []
    for cnt in contours:
        # Simplify pixel chain → polyline
        simplified = cv2.approxPolyDP(cnt, epsilon, closed=False)

        # Convert to list of (x, y)
        line = [(int(p[0][0]), int(p[0][1])) for p in simplified]

        if len(line) > 2:  # valid line
            contour_lines.append(line)
    return contour_lines

def visualize_colored_contours(contour_lines, image_shape=None):
    plt.figure(figsize=(8, 8))

    for line in contour_lines:
        xs = [p[0] for p in line]
        ys = [p[1] for p in line]

        color = (
            random.random(),
            random.random(),
            random.random()
        )
        plt.plot(xs, ys, color=color, linewidth=1)

    if image_shape:
        plt.xlim(0, image_shape[1])
        plt.ylim(image_shape[0], 0)

    plt.title("Color-Coded Contour Lines")
    plt.axis("equal")
    plt.show()

def calculate(image_path):
    try:
        # 1. Image Processing: Isolate Contours
        isolated_contours = subtract_roads_from_contours(image_path)

        # c_lines = extract_contour_lines(isolated_contours, epsilon=2.0)

        # visualize_colored_contours(c_lines, image_shape=isolated_contours.shape)
        
        # 2. Extract Contour Pixel Coordinates
        contour_pixels = get_contour_pixels(isolated_contours)

        # 3. Risk Assessment: Calculate Contour Density in Rings
        risk_results = assess_ring_risk(contour_pixels, CENTER_PIXEL, RISK_RINGS)
        # risk_results_by_contours = assess_ring_risk_by_contours(c_lines, CENTER_PIXEL, RISK_RINGS)
        logger.debug(f"Risk Results: {risk_results}")
        return risk_results
        
    except FileNotFoundError as e:
        logger.error(f"Fatal Error: {e}. Please ensure '{image_path}' are in the correct directory.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")


# --- MAIN EXECUTION ---

if __name__ == "__main__":
    CONTOUR_IMAGE_PATH = "contour_map_0.png"
    calculate(CONTOUR_IMAGE_PATH)