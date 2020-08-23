import os
import sys

from PIL import Image
import numpy as np

class Compresser:

    def compress(self, img):
        w, h = img.size
        k = w/h
        if h > 240:
            img = img.resize((int(240*k), 240), Image.ANTIALIAS)
        return img

