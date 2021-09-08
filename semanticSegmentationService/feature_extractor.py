import numpy as numpy
import cv2


class FeatureExtractor:
    def __init__(self):
        # Define the window size
        self._windowsize_r = 5
        self._windowsize_c = 5
        self._grey_levels = 256

    def readImage(self, img=None):

        if img:
            image = cv2.imread("image4.jpg", 0)
        else:  # generate an image
            image = numpy.random.randint(0, grey_levels, size=(11, 11))

        self._image = image

    def generateImgHistogram(self):
        for r in range(0, self._image.shape[0] - self._windowsize_r, self._windowsize_r):
            for c in range(0, self._image.shape[1] - self._windowsize_c, self._windowsize_c):
                window = self._image[r:r + self._windowsize_r, c:c + self._windowsize_c]
                hist = numpy.histogram(window, bins=self._grey_levels)
