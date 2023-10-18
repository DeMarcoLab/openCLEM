import numpy as np
import matplotlib.pyplot as plt
import tifffile as tf
import py_cwt2d
import cv2

def normalise_image(img):
    """Normalises image to range [0, 1]

    Parameters
    ----------
    img : np.ndarray
        Image to be normalised.

    Returns
    -------
    np.ndarray
        Normalised image.
    """
    return (img - np.min(img)) / (np.max(img) - np.min(img))

def create_wavelet_scales(img, pixel_size, feature_size, buffer, n_scales):
    shape = img.shape
    real_size = shape[0] * pixel_size
    feature_size_pixels = feature_size / pixel_size
    minimum = max(feature_size_pixels - buffer, 1)
    maximum = feature_size_pixels + buffer
    print(f"Minimum: {minimum}, Maximum: {maximum}")
    ss = np.geomspace(minimum, maximum, n_scales)
    return ss


def wavelet_transform(img, wavelet='mexh', pixel_size=1, feature_size=1, buffer=0, n_scales=10):
    """Performs wavelet transform on image.

    Parameters
    ----------
    img : np.ndarray
        Image to be transformed.
    scales : list
        List of scales to be used for transform.
    wavelet : str
        Wavelet to be used for transform.

    Returns
    -------
    np.ndarray
        Transformed image.
    """
    scales = create_wavelet_scales(img, pixel_size, feature_size, buffer, n_scales)
    coeffs, wav_norm = py_cwt2d.cwt_2d(img, scales, wavelet)
    return coeffs, wav_norm, scales

def plot_continuous_wavelet_transform(coeffs, scales, cmap='gray', figsize=(15, 15)):
    n = len(scales)
    # make a square grid
    cols = int(np.ceil(np.sqrt(n)))
    rows = int(np.ceil(n / cols))
    print(f"Rows: {rows}, Cols: {cols}")
    fig, ax = plt.subplots(rows, cols, figsize=figsize)
    for i, scale in enumerate(scales):
        ax[i // cols][i % cols].imshow(np.abs(coeffs[:, :, i]), cmap=cmap)
        ax[i // cols][i % cols].set_title(f'Scale {i}')
        ax[i // cols][i % cols].axis('off')
    plt.show()

def plot_SIFT_keypoints(image, coeffs, scales, cmap='gray', figsize=(15, 15)):
    n = len(scales)
    # make a square grid
    cols = int(np.ceil(np.sqrt(n)))
    rows = int(np.ceil(n / cols))
    print(f"Rows: {rows}, Cols: {cols}")
    fig, ax = plt.subplots(rows, cols, figsize=figsize)
    for i, scale in enumerate(scales):
        image8bit = cv2.normalize(np.abs(coeffs[:, :, i]), None, 0, 255, cv2.NORM_MINMAX).astype('uint8')
        descriptor = cv2.SIFT_create()
        keypoints, descriptors = descriptor.detectAndCompute(image8bit, None)

        ax[i // cols][i % cols].imshow(np.abs(coeffs[:, :, i]), cmap=cmap)
        ax[i // cols][i % cols].set_title(f'Scale {i}')
        ax[i // cols][i % cols].axis('off')
        ax[i // cols][i % cols].scatter([p.pt[0] for p in keypoints], [p.pt[1] for p in keypoints], c='r', marker='.')
    plt.show()



def plot_ORB_keypoints(image, coeffs, scales, cmap='gray', figsize=(15, 15)):
    n = len(scales)
    # make a square grid
    cols = int(np.ceil(np.sqrt(n)))
    rows = int(np.ceil(n / cols))
    print(f"Rows: {rows}, Cols: {cols}")
    fig, ax = plt.subplots(rows, cols, figsize=figsize)
    for i, scale in enumerate(scales):
        image8bit = cv2.normalize(np.abs(coeffs[:, :, i]), None, 0, 255, cv2.NORM_MINMAX).astype('uint8')
        descriptor = cv2.ORB_create()
        keypoints, descriptors = descriptor.detectAndCompute(image8bit, None)

        ax[i // cols][i % cols].imshow(np.abs(coeffs[:, :, i]), cmap=cmap)
        ax[i // cols][i % cols].set_title(f'Scale {i}')
        ax[i // cols][i % cols].axis('off')
        ax[i // cols][i % cols].scatter([p.pt[0] for p in keypoints], [p.pt[1] for p in keypoints], c='r', marker='.')
    plt.show()


def plot_ORB_scale(image, coeffs, scale, cmap='gray', figsize=(15, 15)):
    image8bit = cv2.normalize(np.abs(coeffs[:, :, scale]), None, 0, 255, cv2.NORM_MINMAX).astype('uint8')
    descriptor = cv2.ORB_create()
    keypoints, descriptors = descriptor.detectAndCompute(image8bit, None)
    plt.imshow(np.abs(coeffs[:, :, scale]), cmap=cmap)
    plt.scatter([p.pt[0] for p in keypoints], [p.pt[1] for p in keypoints], c='r', marker='.')
    plt.show()


def plot_ORB_scale_thresh(image, coeffs, scale, thresh, cmap='gray', figsize=(15, 15)):
    image_max = np.amax(np.abs(coeffs[:, :, scale]))
    thresh = thresh * image_max
    image_ = np.abs(coeffs[:, :, scale])
    # plt.imshow(image_, cmap=cmap)
    # plt.colorbar()
    # plt.show()
    print(f"Thresh: {thresh}")
    image_[image_ < thresh] = 0
    # plt.imshow(image_, cmap=cmap)
    # plt.colorbar()
    # plt.show()
    image8bit = cv2.normalize(image_, None, 0, 255, cv2.NORM_MINMAX).astype('uint8')
    descriptor = cv2.ORB_create()
    keypoints, descriptors = descriptor.detectAndCompute(image8bit, None)
    plt.imshow(image_, cmap=cmap)
    plt.scatter([p.pt[0] for p in keypoints], [p.pt[1] for p in keypoints], c='r', marker='.')
    plt.colorbar()
    plt.show()





def plot_combined_wavelet_coeffs(coeffs, cmap='gray', figsize=(15, 15)):
    fig, ax = plt.subplots(len(coeffs)-1, 4, figsize=figsize)
    for i, coeff in enumerate(coeffs[1:]):
        for j in range(3):
            ax[i][j].imshow(coeff[j], cmap=cmap)
            ax[i][j].set_title(f'Level {i+1}, {LABELS[j]}')
            ax[i][j].axis('off')
        ax[i][3].imshow(np.sqrt(coeff[0]**2 + coeff[1]**2 + coeff[2]**2), cmap=cmap)
        ax[i][3].set_title(f'Level {i+1}, Combined')
        ax[i][3].axis('off')

def plot_combined_wavelet_coeffs_only(coeffs, cmap='gray', figsize=(15, 15)):

    fig, ax = plt.subplots(len(coeffs)-1, 1, figsize=figsize)
    for i, coeff in enumerate(coeffs[1:]):
        ax[i].imshow(np.sqrt(coeff[0]**2 + coeff[1]**2 + coeff[2]**2), cmap=cmap)
        ax[i].set_title(f'Level {i+1}, Combined')
        ax[i].axis('off')

    plt.show()

def plot_wavelet_coeffs(coeffs, cmap='gray', figsize=(15, 15), combined=False):
    """Plots wavelet coefficients other than the initial

    Parameters
    ----------
    coeffs : list
        List of coefficients for each level of transform.
    cmap : str, optional
        Color map to use for plotting, by default 'gray'
    figsize : tuple, optional
        Size of figure, by default (15, 15)
    combined : bool, optional
        Whether to plot an image with all coefficients combined, by default False
    """
    if not combined:
        fig, ax = plt.subplots(len(coeffs)-1, 3, figsize=figsize)
        for i, coeff in enumerate(coeffs[1:]):
            for j in range(3):
                ax[i][j].imshow(coeff[j], cmap=cmap)
                ax[i][j].set_title(f'Level {i+1}, {LABELS[j]}')
                ax[i][j].axis('off')
    else:
        plot_combined_wavelet_coeffs(coeffs, cmap=cmap, figsize=figsize)
    plt.show()

def plot_wavelet_coeffs_col(coeffs, col, cmap='gray', figsize=(15, 15)):
    """Plots wavelet coefficients other than the initial

    Parameters
    ----------
    coeffs : list
        List of coefficients for each level of transform.
    """
    fig, ax = plt.subplots(len(coeffs)-1, 1, figsize=figsize)
    for i, coeff in enumerate(coeffs[1:]):
        ax[i].imshow(coeff[col], cmap=cmap)
        ax[i].set_title(f'Level {i+1}, {LABELS[col]}')
        ax[i].axis('off')
    plt.show()

def plot_wavelet_coeffs_row(coeffs, row, cmap='gray', figsize=(15, 15)):
    """Plots wavelet coefficients other than the initial

    Parameters
    ----------
    coeffs : list
        List of coefficients for each level of transform.
    """
    fig, ax = plt.subplots(1, 3, figsize=figsize)

    coeff = coeffs[row+1]
    for i, level in enumerate(coeff):
        ax[i].imshow(coeff[i], cmap=cmap)
        ax[i].set_title(f'Level {row+1}, {LABELS[i]}')
        ax[i].axis('off')
    plt.show()

