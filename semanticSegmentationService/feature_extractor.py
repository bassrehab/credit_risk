import numpy as numpy
import cv2

img = cv2.imread("image4.jpg",0)
grey_levels = 256
# Generate a test image
test_image = numpy.random.randint(0,grey_levels, size=(11,11))

# Define the window size
windowsize_r = 5
windowsize_c = 5

# Crop out the window and calculate the histogram
for r in range(0,test_image.shape[0] - windowsize_r, windowsize_r):
    for c in range(0,test_image.shape[1] - windowsize_c, windowsize_c):
        window = test_image[r:r+windowsize_r,c:c+windowsize_c]
        hist = numpy.histogram(window,bins=grey_levels)