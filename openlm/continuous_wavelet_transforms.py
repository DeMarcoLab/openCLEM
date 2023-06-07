import numpy as np
import matplotlib.pyplot as plt
import tifffile as tf
import py_cwt2d

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
    min = feature_size_pixels - buffer
    max = feature_size_pixels + buffer
    print(f"min: {min}, max: {max}")

    ss = np.geomspace(min, max, n_scales)
    return ss

def wavelet_transform(img, wavelet='db1', level=1, mode=None):
    """Performs wavelet transform on image.

    Parameters
    ----------
    img : np.ndarray
        Image to be transformed.
    wavelet : str
        Wavelet to be used for transform.
    level : int
        Number of levels to perform transform.

    Returns
    -------
    coeffs : list
        List of coefficients for each level of transform.
    """
    if mode is not None:
        coeffs = pywt.wavedec2(img, wavelet, level=level, mode=mode)
    else:
        coeffs = pywt.wavedec2(img, wavelet, level=level)
    return coeffs

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

