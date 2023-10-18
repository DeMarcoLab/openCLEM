import os
from dataclasses import dataclass

import cv2
import numpy as np
import tifffile as tiff
import matplotlib.pyplot as plt

from openlm.structures import StitchingParameters
from stitching import AffineStitcher

def stitch_tile(image_tiles: list, stitching_parameters: StitchingParameters, **kwargs) -> np.ndarray:
    """
    Stitch a list of images together.

    :param image_tiles: A list of lists of images to stitch together.  Each list is a row of images.
    :return: The stitched image.
    """
    # get the dpi of the images from kwargs
    dpi = kwargs.get("dpi", 100)
    cmap = kwargs.get("cmap", "gray")
    figsize = kwargs.get("figsize", (10, 10))

    result_ = stitch_row(image_tiles[0], stitching_parameters, **kwargs)
    for i in range(1, len(image_tiles)):
        result = stitch_row(image_tiles[i], stitching_parameters, **kwargs)

        if stitching_parameters.debug:
            ax, fig = plt.subplots(1, 3, dpi=dpi, figsize=figsize)
            fig[0].imshow(result_.T, cmap=cmap)
            fig[1].imshow(result.T, cmap=cmap)
            
        result_ = stitch(result.T, result_.T, stitching_parameters).T
        if stitching_parameters.debug:
            fig[2].imshow(result_.T, cmap=cmap)
            plt.show()

    return result_

def stitch_row(
    image_row: list, stitching_parameters: StitchingParameters, **kwargs
) -> np.ndarray:
    """
    Stitch a row of images together.

    :param image_row: A list of images to stitch together.
    :return: The stitched image.
    """
    # get the dpi of the images from kwargs
    dpi = kwargs.get("dpi", 100)
    cmap = kwargs.get("cmap", "gray")
    figsize = kwargs.get("figsize", (10, 10))
    result_ = image_row[0]
    for i in range(1, len(image_row)):
        result = stitch(result_, image_row[i], stitching_parameters)
        if stitching_parameters.debug:
            ax, fig = plt.subplots(1, 3, dpi=dpi, figsize=figsize)
            fig[0].imshow(result_, cmap=cmap)
            fig[1].imshow(image_row[i], cmap=cmap)
            fig[2].imshow(result, cmap=cmap)
            plt.show()
            print('-'*200)
        result_ = result
    return result


def stitch(image1: np.ndarray, image2: np.ndarray, stitching_parameters: StitchingParameters):
    # convert the images to uint8 and normalise
    converted_img1 = cv2.normalize(image1, None, 0, 255, cv2.NORM_MINMAX).astype(
        "uint8"
    )
    converted_img2 = cv2.normalize(image2, None, 0, 255, cv2.NORM_MINMAX).astype(
        "uint8"
    )

    # temporarily save the images to disk
    img1_path = os.path.join(stitching_parameters.folder_path, "converted_img1_temp.tif")
    img2_path = os.path.join(stitching_parameters.folder_path, "converted_img2_temp.tif")
    tiff.imwrite(img1_path, converted_img1)
    tiff.imwrite(img2_path, converted_img2)

    settings = {# The whole plan should be considered
            "crop": True,
            # The matches confidences aren't that good
            "confidence_threshold": 0.3}  
    stitcher = AffineStitcher(**settings)

    stitched_image = stitcher.stitch([img1_path, img2_path])
    # remove the temporary images
    os.remove(img1_path)
    os.remove(img2_path)

    return stitched_image[:, :, 0]
