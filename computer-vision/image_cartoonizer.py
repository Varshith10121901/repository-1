import cv2
import numpy as np

def cartoonize_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load image at path '{image_path}'")
        return

    img = cv2.resize(img, (800, 600))

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)

    # Detect edges
    edges = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
        cv2.THRESH_BINARY, 9, 10
    )

    # Apply bilateral filter to smooth colors
    color = cv2.bilateralFilter(img, 9, 250, 250)

    # Combine edges and color
    cartoon = cv2.bitwise_and(color, color, mask=edges)

    # Save and/or display the result
    output_path = "cartoon_output.jpg"
    cv2.imwrite(output_path, cartoon)
    print(f"Cartoonized image saved as '{output_path}'")

    # Display if GUI support exists
    try:
        cv2.imshow("Cartoonized Image", cartoon)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except cv2.error:
        print("GUI display not supported in this environment.")

# Replace with the actual path to your image
cartoonize_image("C:/Users/Dell/Downloads/john-wick-chapter-4-3840x3840-10587.jpg")
