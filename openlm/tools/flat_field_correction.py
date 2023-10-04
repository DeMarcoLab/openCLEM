import numpy as np
import matplotlib.pyplot as plt
import tifffile as tf
import openlm.tools
import os

# get path of tools
tools_path = os.path.dirname(openlm.tools.__file__)
FLATFIELDARRAY = np.load(os.path.join(tools_path, 'flat_field.npy'))
FLATFIELDNORMALISED = FLATFIELDARRAY / np.mean(FLATFIELDARRAY)
DARKFIELD = np.zeros(FLATFIELDARRAY.shape)

def corrected_image(image, dark_field_image, flat_field_image, correction_factor=1):
    # Correct image
    corrected_image = (image - dark_field_image) * np.mean(flat_field_image - dark_field_image) * correction_factor / (flat_field_image - dark_field_image)
    return corrected_image
