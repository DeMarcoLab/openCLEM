from dataclasses import dataclass, field
from enum import Enum
from pprint import pprint
from typing import get_type_hints
import itertools
from copy import deepcopy

import napari
import numpy as np
import tifffile as tiff
from fibsem.imaging import masks
from PyQt5 import QtCore, QtGui, QtWidgets
from scipy.fftpack import fft2, fftshift, ifft2, ifftshift
from scipy.ndimage import gaussian_filter, median_filter

from openlm.tools import continuous_wavelet_transforms
from openlm.ui.qt import OpenLMWaveletWidget

filters = {
    "gaussian": gaussian_filter,
    "median": median_filter,
}


class ImageMode(Enum):
    LM = 1
    FIB = 2


class GuiMainWindow(OpenLMWaveletWidget.Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(self, viewer: napari.Viewer = None):
        super(GuiMainWindow, self).__init__()
        self.setupUi(self)
        self.viewer = viewer
        self.setup_parameters()
        self.setup_connections()
        self.setup_availability()

    def setup_parameters(self):
        self.widget_parameters = WaveletWidgetParameters()
        self.widget_parameters.translation_x = 0

    def setup_connections(self):
        self.pushButton_LoadImage_LM.clicked.connect(
            lambda: self.load_image(image_mode=ImageMode.LM)
        )
        self.pushButton_LoadImage_FIB.clicked.connect(
            lambda: self.load_image(image_mode=ImageMode.FIB)
        )
        self.pushButton_Filter_LM.clicked.connect(
            lambda: self.image_filter(image_mode=ImageMode.LM)
        )
        self.pushButton_Filter_FIB.clicked.connect(
            lambda: self.image_filter(image_mode=ImageMode.FIB)
        )
        self.pushButton_FFT_LM.clicked.connect(
            lambda: self.fft_transform(image_mode=ImageMode.LM)
        )
        self.pushButton_FFT_FIB.clicked.connect(
            lambda: self.fft_transform(image_mode=ImageMode.FIB)
        )
        self.pushButton_Bandpass_Mask_LM.clicked.connect(
            lambda: self.bandpass_mask(image_mode=ImageMode.LM)
        )
        self.pushButton_Bandpass_Mask_FIB.clicked.connect(
            lambda: self.bandpass_mask(image_mode=ImageMode.FIB)
        )
        self.pushButton_Bandpass_LM.clicked.connect(
            lambda: self.bandpass_filter(image_mode=ImageMode.LM)
        )
        self.pushButton_Bandpass_FIB.clicked.connect(
            lambda: self.bandpass_filter(image_mode=ImageMode.FIB)
        )
        self.pushButton_Wavelet_Scales_LM.clicked.connect(
            lambda: self.wavelet_scales(image_mode=ImageMode.LM)
        )
        self.pushButton_Wavelet_Scales_FIB.clicked.connect(
            lambda: self.wavelet_scales(image_mode=ImageMode.FIB)
        )
        self.pushButton_Wavelet_Apply_LM.clicked.connect(
            lambda: self.wavelet_crosscorrelation()
        )
        self.pushButton_Wavelet_Apply_FIB.clicked.connect(
            lambda: self.wavelet_crosscorrelation()
        )
        self.buttonGroup.buttonClicked.connect(self.change_display)
        
        self.checkBox_Image_Filter_lm.stateChanged.connect(lambda: self.change_combination(image_mode=ImageMode.LM))
        self.checkBox_Bandpass_lm.stateChanged.connect(lambda: self.change_combination(image_mode=ImageMode.LM))
        self.checkBox_Image_Filter_fibsem.stateChanged.connect(lambda: self.change_combination(image_mode=ImageMode.FIB))
        self.checkBox_Bandpass_fibsem.stateChanged.connect(lambda: self.change_combination(image_mode=ImageMode.FIB))

        self.pushButton_Fourier_Pad.clicked.connect(lambda: self.pad_fourier_space())

    def change_combination(self, image_mode: ImageMode):
        # print which boxes are checked
        choice_dict = {
            ImageMode.LM: {
                "name": "combined_image_lm",
                "cmap": "turbo",
                "combined_image": self.widget_parameters.combined_image_lm,
                "source_image": self.widget_parameters.image_lm,
                "image_filter": self.checkBox_Image_Filter_lm.isChecked(),
                "bandpass": self.checkBox_Bandpass_lm.isChecked(),
            },
            ImageMode.FIB: {
                "name": "combined_image_fibsem",
                "cmap": "gray",
                "combined_image": self.widget_parameters.combined_image_fibsem,
                "source_image": self.widget_parameters.image_fibsem,
                "image_filter": self.checkBox_Image_Filter_fibsem.isChecked(),
                "bandpass": self.checkBox_Bandpass_fibsem.isChecked(),
                "translate": True,
            },
        }

        functions = {
            "image_filter": self.image_filter,
            "bandpass": self.bandpass_filter,
        }

        possible_combinations = [
            ["image_filter", "bandpass"],
            ["image_filter"],
            ["bandpass"],
            [],
        ]

        # check which combination is selected
        for combination in possible_combinations:
            if all(choice_dict[image_mode][key] for key in combination):
                image = deepcopy(choice_dict[image_mode]["source_image"][0]["data"])
                for key in combination:
                    image = functions[key](image_mode, image)

                break
            else:
                image = choice_dict[image_mode]["source_image"][0]["data"]
            

        parameter_dict = [self.create_widget_parameter_dict(
            choice_dict=choice_dict, mode=image_mode, data=image
        )]

        self.update_widget_parameters(
            name=parameter_dict[0]["name"], structure=parameter_dict
        )

        self.display_images(self.widget_parameters.__getattribute__(choice_dict[image_mode]["name"])) 
        self.radioButton_Combined.setChecked(True)
        self.radioButton_Combined.click()
        self.update_translations()

    def setup_availability(self):
        self.frame_Filters.setEnabled(False)  
        self.frame_Display.setEnabled(False)
        self.frame_Combined.setEnabled(False)     

    def change_display(self):
        choice_dict = {
            self.radioButton_Combined: {
                "lm": self.widget_parameters.combined_image_lm,
                "fibsem": self.widget_parameters.combined_image_fibsem,
            },
            self.radioButton_Image_Raw: {
                "lm": self.widget_parameters.image_lm,
                "fibsem": self.widget_parameters.image_fibsem,
            },
            self.radioButton_Image_Filter: {
                "lm": self.widget_parameters.image_filtered_lm,
                "fibsem": self.widget_parameters.image_filtered_fibsem,
            },
            self.radioButton_FFT: {
                "lm": self.widget_parameters.fft_lm,
                "fibsem": self.widget_parameters.fft_fibsem,
            },
            self.radioButton_Bandpass_Mask: {
                "lm": self.widget_parameters.mask_bandpass_lm,
                "fibsem": self.widget_parameters.mask_bandpass_fibsem,
            },
            self.radioButton_Bandpass_Filtered: {
                "lm": self.widget_parameters.image_bandpass_filtered_lm,
                "fibsem": self.widget_parameters.image_bandpass_filtered_fibsem,
            },
            self.radioButton_Wavelet: {
                "lm": self.widget_parameters.wavelet_coeffs_lm,
                "fibsem": self.widget_parameters.wavelet_coeffs_fibsem,
            },
            self.radioButton_Cross_Correlation: {
                "lm": self.widget_parameters.crosscorrelation_lm,
                "fibsem": self.widget_parameters.crosscorrelation_fibsem,
            },
            self.radioButton_Padded: {
                "lm": self.widget_parameters.padded_lm,
                "fibsem": self.widget_parameters.padded_fibsem,
            }
        }
        
        for layer in self.viewer.layers:
            layer.visible = False
        if len(choice_dict[self.radioButton_Wavelet]["lm"]) > 0:
            for coeff in choice_dict[self.radioButton_Wavelet]["lm"]: 
                self.viewer.layers[coeff.get("name")].visible = False
        if len(choice_dict[self.radioButton_Wavelet]["fibsem"]) > 0:
            for coeff in choice_dict[self.radioButton_Wavelet]["lm"]: 
                self.viewer.layers[coeff.get("name")].visible = False

        for choice in choice_dict:
                if self.buttonGroup.checkedButton() != choice:
                    continue
                if choice is not self.radioButton_Wavelet and choice is not self.radioButton_Cross_Correlation and choice is not self.radioButton_Padded:
                    if len(choice_dict[choice]["lm"]) > 0:
                        self.toggle_visibility(choice_dict[choice]["lm"][0].get("name"))
                    if len(choice_dict[choice]["fibsem"]) > 0:
                        self.toggle_visibility(choice_dict[choice]["fibsem"][0].get("name"))
                else:
                    for coeff in choice_dict[choice]["lm"]:
                        self.toggle_visibility(coeff.get("name"))
                    for coeff in choice_dict[choice]["fibsem"]:
                        self.toggle_visibility(coeff.get("name"))

    def toggle_visibility(self, layer):
        self.viewer.layers[layer].visible = True

    def load_image(self, image_mode: ImageMode):
        choice_dict = {
            ImageMode.LM: {"name": "image_lm", "cmap": "turbo", "combined": "combined_image_lm"},
            ImageMode.FIB: {"name": "image_fibsem", "cmap": "gray", "combined": "combined_image_fibsem"},
        }

        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open Image", "", "Image Files (*.tif *.tiff)"
        )

        if not file_name:
            return
        data = tiff.imread(file_name)

        parameter_dict = [
            self.create_widget_parameter_dict(
                choice_dict=choice_dict, mode=image_mode, data=data
            )
        ]


        self.update_widget_parameters(
            name=parameter_dict[0]["name"], structure=parameter_dict
        )
        
        self.update_widget_parameters(
            name=choice_dict[image_mode]["combined"], structure=parameter_dict
        )

        self.display_images(
            self.widget_parameters.__getattribute__(choice_dict[image_mode]["name"])
        )

        self.display_images(
            self.widget_parameters.__getattribute__(choice_dict[image_mode]["combined"])
        )

        self.frame_Filters.setEnabled(True)
        self.frame_Display.setEnabled(True)
        self.frame_Combined.setEnabled(True)
        self.radioButton_Combined.setEnabled(True)
        self.radioButton_Combined.setChecked(True)
        self.radioButton_Combined.click()

        return data

    def image_filter(self, image_mode: ImageMode, image: np.ndarray=None):
        choice_dict = {
            ImageMode.LM: {
                "name": "image_filtered_lm",
                "source_image": "image_lm",
                "cmap": "turbo",
                "comboBox": self.comboBox_Filter_Type_LM,
                "spinBox": self.spinBox_Filter_LM,
            },
            ImageMode.FIB: {
                "name": "image_filtered_fibsem",
                "source_image": "image_fibsem",
                "cmap": "gray",
                "comboBox": self.comboBox_Filter_Type_FIB,
                "spinBox": self.spinBox_Filter_FIB,
            },
        }

        filter_type = choice_dict[image_mode]["comboBox"].currentText()
        filter_size = choice_dict[image_mode]["spinBox"].value()
        filter = filters.get(filter_type)
        source_image = self.widget_parameters.__getattribute__(
            choice_dict[image_mode]["source_image"]
        )

        if image is not None:
            print("Filtering Combined Image")
            return filter(image, filter_size)
        
        data = filter(source_image[0].get("data"), filter_size)
        parameter_dict = [
            self.create_widget_parameter_dict(
                choice_dict=choice_dict, mode=image_mode, data=data
            )
        ]
        self.update_widget_parameters(
            name=parameter_dict[0]["name"], structure=parameter_dict
        )

        self.display_images(
            self.widget_parameters.__getattribute__(choice_dict[image_mode]["name"])
        )
        self.radioButton_Image_Filter.setEnabled(True)
        self.radioButton_Image_Filter.setChecked(True)
        self.radioButton_Image_Filter.click()

        return data

    def fft_transform(self, image_mode: ImageMode, image: np.ndarray=None):
        choice_dict = {
            ImageMode.LM: {
                "name": "fft_lm",
                "source_image": "image_lm",
                "cmap": "turbo",
            },
            ImageMode.FIB: {
                "name": "fft_fibsem",
                "source_image": "image_fibsem",
                "cmap": "gray",
            },
        }

        if image is not None:
            image_fft = fft2(image)
            image_fft[0, 0] = 0
            data = fftshift(image_fft)
            return data

        source_image = self.widget_parameters.__getattribute__(
            choice_dict[image_mode]["source_image"]
        )

        fft_ = fft2(source_image[0].get("data"))
        fft_[0, 0] = 0
        data = fftshift(fft_)

        parameter_dict = [
            self.create_widget_parameter_dict(
                choice_dict=choice_dict, mode=image_mode, data=data
            )
        ]

        self.update_widget_parameters(
            name=parameter_dict[0]["name"], structure=parameter_dict
        )

        self.display_images(
            self.widget_parameters.__getattribute__(choice_dict[image_mode]["name"])
        )
        self.radioButton_FFT.setEnabled(True)

        return data

    def bandpass_mask(self, image_mode: ImageMode, image: np.ndarray=None):
        choice_dict = {
            ImageMode.LM: {
                "name": "mask_bandpass_lm",
                "source_image": "image_lm",
                "cmap": "turbo",
                "comboBox_LP": self.spinBox_Bandpass_LM_LP,
                "comboBox_HP": self.spinBox_Bandpass_LM_HP,
                "spinBox_Sigma": self.spinBox_Bandpass_Sigma_LM,
            },
            ImageMode.FIB: {
                "name": "mask_bandpass_fibsem",
                "source_image": "image_fibsem",
                "cmap": "gray",
                "comboBox_LP": self.spinBox_Bandpass_FIB_LP,
                "comboBox_HP": self.spinBox_Bandpass_FIB_HP,
                "spinBox_Sigma": self.spinBox_Bandpass_Sigma_FIB,
            },
        }

        low_pass = choice_dict[image_mode]["comboBox_LP"].value()
        high_pass = choice_dict[image_mode]["comboBox_HP"].value()
        source_image = self.widget_parameters.__getattribute__(
            choice_dict[image_mode]["source_image"]
        )
        sigma = choice_dict[image_mode]["spinBox_Sigma"].value()

        if image is not None:
            data = masks.create_bandpass_mask(
                shape=image.shape, lp=low_pass, hp=high_pass, sigma=sigma
            )
            return data

        data = masks.create_bandpass_mask(
            shape=source_image[0].get("data").shape,
            lp=low_pass,
            hp=high_pass,
            sigma=sigma,
        )

        parameter_dict = [
            self.create_widget_parameter_dict(
                choice_dict=choice_dict, mode=image_mode, data=data
            )
        ]

        self.update_widget_parameters(
            name=parameter_dict[0]["name"], structure=parameter_dict
        )

        self.display_images(
            self.widget_parameters.__getattribute__(choice_dict[image_mode]["name"])
        )
        self.radioButton_Bandpass_Mask.setEnabled(True)

        return data

    def bandpass_filter(self, image_mode: ImageMode, image: np.ndarray=None):
        choice_dict = {
            ImageMode.LM: {
                "name": "image_bandpass_filtered_lm",
                "cmap": "turbo",
            },
            ImageMode.FIB: {
                "name": "image_bandpass_filtered_fibsem",
                "cmap": "gray",
            },
        }

        if image is not None:
            print("Bandpass filtering Combined Image")
            image_fft = self.fft_transform(image_mode, image)
            bandpass_mask = self.bandpass_mask(image_mode, image)
            data_fft = image_fft * bandpass_mask
            data = ifft2(data_fft)
            return data

        fft_ = self.fft_transform(image_mode)
        bandpass_mask = self.bandpass_mask(image_mode)


        data_fft = fft_ * bandpass_mask
        data = ifft2(data_fft)

        parameter_dict = [
            self.create_widget_parameter_dict(
                choice_dict=choice_dict, mode=image_mode, data=data
            )
        ]

        self.update_widget_parameters(
            name=parameter_dict[0]["name"], structure=parameter_dict
        )

        self.display_images(
            self.widget_parameters.__getattribute__(choice_dict[image_mode]["name"])
        )
        self.radioButton_Bandpass_Filtered.setEnabled(True)
        self.radioButton_Bandpass_Filtered.setChecked(True)
        self.radioButton_Bandpass_Filtered.click()

        return data

    def wavelet_scales(self, image_mode: ImageMode):
        choice_dict = {
            ImageMode.LM: {
                "name": "wavelet_coeffs_lm",
                "source_image": "combined_image_lm",
                "cmap": "turbo",
                "comboBox": self.comboBox_Wavelet_LM,
                "spinBox_Pixel_Size": self.spinBox_Wavelet_LM_Pixel_Size,
                "spinBox_Feature_Size": self.spinBox_Wavelet_LM_Feature_Size,
                "spinBox_Buffer_Size": self.spinBox_Wavelet_LM_Buffer_Size,
                "spinBox_n_Scales": self.spinBox_Wavelet_LM_n_Scales,
                "wavelet_save": self.widget_parameters.wavelet_lm,
            },
            ImageMode.FIB: {
                "name": "wavelet_coeffs_fibsem",
                "source_image": "combined_image_fibsem",
                "cmap": "gray",
                "comboBox": self.comboBox_Wavelet_FIB,
                "spinBox_Pixel_Size": self.spinBox_Wavelet_FIB_Pixel_Size,
                "spinBox_Feature_Size": self.spinBox_Wavelet_FIB_Feature_Size,
                "spinBox_Buffer_Size": self.spinBox_Wavelet_FIB_Buffer_Size,
                "spinBox_n_Scales": self.spinBox_Wavelet_FIB_n_Scales,
                "wavelet_save": self.widget_parameters.wavelet_fibsem,
            },
        }

        temp_name = choice_dict[image_mode]["name"]

        source_image = self.widget_parameters.__getattribute__(
            choice_dict[image_mode]["source_image"]
        )

        coeffs, wav_norm, scales = continuous_wavelet_transforms.wavelet_transform(
            source_image[0].get("data"),
            choice_dict[image_mode]["comboBox"].currentText(),
            choice_dict[image_mode]["spinBox_Pixel_Size"].value(),
            choice_dict[image_mode]["spinBox_Feature_Size"].value(),
            choice_dict[image_mode]["spinBox_Buffer_Size"].value(),
            choice_dict[image_mode]["spinBox_n_Scales"].value(),
        )
        # reshape so that the third axis is the first dimension
        coeffs = np.moveaxis(coeffs, 2, 0)
        widget_coeffs = []
        # print(coeffs.shape)
        for i, data in enumerate(coeffs):
            choice_dict[image_mode]["name"] = (
                "wavelet_" + str(scales[i]) + "_" + image_mode.name
            )
            choice_dict[image_mode]["translate_y"] = data.shape[0] * (i * 1.02)
            parameter_dict = self.create_widget_parameter_dict(
                choice_dict=choice_dict, mode=image_mode, data=data
            )
            widget_coeffs.append(parameter_dict)
            

        self.update_widget_parameters(name=temp_name, structure=widget_coeffs)
        self.display_images(self.widget_parameters.__getattribute__(temp_name))

        self.radioButton_Wavelet.setEnabled(True)
        self.radioButton_Wavelet.setChecked(True)
        self.radioButton_Wavelet.click()

    def get_wavelet_combinations(self):
        # go through the widget parameters
        # find all the wavelet coefficients
        # separate them into LM and FIBSEM
        # find all the combinations of LM and FIBSEM
        # return the combinations
        if len(self.widget_parameters.padded_lm) > 0:
            self.wavelet_coeffs_lm = deepcopy(self.widget_parameters.padded_lm)
        elif len(self.widget_parameters.wavelet_coeffs_lm) == 0:
            self.wavelet_coeffs_lm = deepcopy(self.widget_parameters.combined_image_lm)
        else:
            self.wavelet_coeffs_lm = deepcopy(self.widget_parameters.wavelet_coeffs_lm)
        if len(self.widget_parameters.padded_fibsem) > 0:
            self.wavelet_coeffs_fibsem = deepcopy(self.widget_parameters.padded_fibsem)
        elif len(self.widget_parameters.wavelet_coeffs_fibsem) == 0:
            self.wavelet_coeffs_fibsem = deepcopy(self.widget_parameters.combined_image_fibsem)
        else:
            self.wavelet_coeffs_fibsem = deepcopy(
                self.widget_parameters.wavelet_coeffs_fibsem
            )

        self.wavelet_combinations = list(
            itertools.product(self.wavelet_coeffs_lm, self.wavelet_coeffs_fibsem)
        )

        print("Wavelet combinations: ", self.wavelet_combinations)

    def wavelet_crosscorrelation(self):
        self.get_wavelet_combinations()
        image_mode = ImageMode.LM
        choice_dict = {
            ImageMode.LM: {
                "name": "crosscorrelation_lm",
                "source_image": "image_lm",
                "cmap": "turbo",
                },
                ImageMode.FIB: {
                "name": "crosscorrelation_fibsem",
                "source_image": "image_fibsem",
                "cmap": "gray"
                },
            }

        temp_name = "crosscorrelation_lm"

        cross_correlations = []
        for i, combination in enumerate(self.wavelet_combinations):
            if combination[1]["data"].shape[0] < combination[0]["data"].shape[0]:
                # pad the fibsem image to match
                diff_x = combination[0]["data"].shape[0] - combination[1]["data"].shape[0]
                diff_y = combination[0]["data"].shape[1] - combination[1]["data"].shape[1]
                combination[1]["data"] = np.pad(
                    combination[1]["data"],
                    ((0, diff_x), (0, diff_y)),
                    "constant",
                    constant_values=0,
                )                

            data = crosscorrelation_v2(combination[0]["data"], combination[1]["data"])
                
            choice_dict[image_mode]["name"] = (
                "crosscorrelation_" + combination[0]["name"] + "_" + combination[1]["name"] + str(i)
            )
            choice_dict[image_mode]["translate_y"] = data.shape[0] * (i * 1.02)

            parameter_dict = self.create_widget_parameter_dict(
                choice_dict=choice_dict, mode=image_mode, data=data
            )

            cross_correlations.append(parameter_dict)
            
        self.update_widget_parameters(name=temp_name, structure=cross_correlations)
        
        self.display_images(self.widget_parameters.__getattribute__(temp_name))

        self.radioButton_Cross_Correlation.setEnabled(True)
        self.radioButton_Cross_Correlation.setChecked(True)
        self.radioButton_Cross_Correlation.click()

    def pad_fourier_space(self):
        image_mode = ImageMode.LM
        choice_dict = {
            ImageMode.LM: {
                "name": "padded_lm",
                "source_image": "combined_image_lm",
                "cmap": "turbo",
                }
            }
        pixel_size_lm = self.doubleSpinBox_Pixel_Size_lm.value()
        pixel_size_fibsem = self.doubleSpinBox_Pixel_Size_fibsem.value()
        realspace_size_lm = pixel_size_lm * self.widget_parameters.image_lm[0].get("data").shape[1]
        # realspace_size_fibsem = pixel_size_fibsem * self.widget_parameters.image_fibsem[0].get("data").shape[1]
        n_pixels = realspace_size_lm/pixel_size_fibsem
        diff = n_pixels - self.widget_parameters.image_lm[0].get("data").shape[1]

        if len(self.widget_parameters.wavelet_coeffs_lm) == 0:
            self.paddable_images = deepcopy(self.widget_parameters.combined_image_lm)
        else:
            self.paddable_images = deepcopy(self.widget_parameters.wavelet_coeffs_lm)

        padded_images = []
        for i, image in enumerate(self.paddable_images):
            fft_ = fft2(image.get("data"))
            fft_[0,0] = 0  # Remove the DC component
            pad_rows = int(diff/2)  # Double the number of rows
            pad_cols = int(diff/2)  # Double the number of columns
            padded_fft = np.pad(fft_, ((pad_rows, pad_rows), (pad_cols, pad_cols)), mode='constant', constant_values=0)
            padded_image = ifft2(padded_fft)
            if self.checkBox_Gaussian_Fourier.isChecked():
                padded_image = gaussian_filter(padded_image, sigma=self.spinBox_Gaussian_Fourier.value())
            choice_dict[image_mode]["name"] = (
                "padded_" + image["name"] + str(i)
            )
            choice_dict[image_mode]["translate_y"] = padded_image.shape[0] * (i * 1.02)

            parameter_dict = self.create_widget_parameter_dict(
            choice_dict=choice_dict, mode=image_mode, data=padded_image
            )
            
            padded_images.append(parameter_dict)

        self.update_widget_parameters(name="padded_lm", structure=padded_images)
        self.display_images(self.widget_parameters.__getattribute__("padded_lm"))

        self.radioButton_Padded.setEnabled(True)
        self.radioButton_Padded.setChecked(True)
        self.radioButton_Padded.click()

    def create_widget_parameter_dict(
        self, choice_dict: dict, mode: ImageMode, data: np.ndarray
    ):
        widget_parameter_dict = {
            "name": choice_dict[mode]["name"],
            "data": data,
            "mode": mode,
            "translate": (mode is ImageMode.FIB),
            "cmap": choice_dict[mode]["cmap"],
            "translate_y": choice_dict[mode].get("translate_y", False),
        }
        return widget_parameter_dict

    def update_widget_parameters(self, name, structure):
        self.widget_parameters.__setattr__(name, structure)

    def display_images(self, parameter: dict):
        layers_list = [layer.name for layer in self.viewer.layers._list]

        if isinstance(parameter, list):
            for param in parameter:
                self.display_images(param)
            return
        else:
            data = parameter.get("data")
            if np.iscomplexobj(data):
                data = np.abs(data)

            if parameter.get("name") not in layers_list:
                self.viewer.add_image(
                    data=data,
                    name=parameter.get("name"),
                    colormap=parameter.get("cmap", "turbo"),
                )
            else:
                self.viewer.layers[parameter.get("name")].data = data

        self.update_translations()

    def update_translations(self):
        if len(self.widget_parameters.image_lm) == 0:
            return
        if self.widget_parameters.image_lm[0].get("data") is not None:
            self.widget_parameters.translation_x = self.widget_parameters.image_lm[0][
                "data"
            ].shape[1]
        else:
            self.widget_parameters.translation_x = 0

        for key, parameter in self.widget_parameters:
            if isinstance(parameter, int) or isinstance(parameter, float):
                continue
            for layer in parameter:
                if layer.get("name") in self.viewer.layers:
                    if layer.get("translate"):
                        self.viewer.layers[layer.get("name")].translate = [
                            layer.get("translate_y", 0),
                            self.widget_parameters.translation_x,
                        ]
                    elif layer.get("translate_y"):
                        self.viewer.layers[layer.get("name")].translate = [
                            layer.get("translate_y"),
                            0,
                        ]

    # setup callbacks for evaluating/displaying values, such as peaks
    # def set_callbacks(self, layer):
    #     layer.events.data.connect(self.update_viewer_v2)

  

def crosscorrelation_v2(
    img1: np.ndarray, img2: np.ndarray, bandpass: np.ndarray = None
) -> np.ndarray:
    """
    Cross-correlate two images using Fourier convolution matching.

    Args:
        img1 (np.ndarray): The reference image.
        img2 (np.ndarray): The new image to be cross-correlated with the reference.
        bandpass (np.ndarray, optional): A bandpass mask to apply to both images before cross-correlation. Defaults to None.

    Returns:
        np.ndarray: The cross-correlation map between the two images.
    """
    if img1.shape != img2.shape:
        err = (
            f"Image 1 {img1.shape} and Image 2 {img2.shape} need to have the same shape"
        )
        raise ValueError(err)

    if bandpass is None:
        bandpass = np.ones_like(img1)

    n_pixels = img1.shape[0] * img1.shape[1]

    img1ft = np.fft.ifftshift(bandpass * np.fft.fftshift(np.fft.fft2(img1)))
    tmp = img1ft * np.conj(img1ft)
    img1ft = n_pixels * img1ft / np.sqrt(tmp.sum())

    img2ft = np.fft.ifftshift(bandpass * np.fft.fftshift(np.fft.fft2(img2)))
    img2ft[0, 0] = 0
    tmp = img2ft * np.conj(img2ft)

    img2ft = n_pixels * img2ft / np.sqrt(tmp.sum())

    # import matplotlib.pyplot as plt
    # fig, ax = plt.subplots(1, 2, figsize=(15, 15))
    # ax[0].imshow(np.fft.ifft2(img1ft).real)
    # ax[1].imshow(np.fft.ifft2(img2ft).real)
    # plt.show()

    # plt.title("Power Spectra")
    # plt.imshow(np.log(np.abs(np.fft.fftshift(np.fft.fft2(img1)))))
    # plt.show()

    xcorr = np.real(np.fft.fftshift(np.fft.ifft2(img1ft * np.conj(img2ft))))

    return xcorr

# TODO: These should be lists
@dataclass
class WaveletWidgetParameters:
    # Raw images
    image_lm: dict = field(default_factory=dict)
    image_fibsem: dict = field(default_factory=dict)
    # Filtered images (median/gaussian)
    image_filtered_lm: dict = field(default_factory=dict)
    image_filtered_fibsem: dict = field(default_factory=dict)
    # FFTs
    fft_lm: dict = field(default_factory=dict)
    fft_fibsem: dict = field(default_factory=dict)
    # Bandpass masks
    mask_bandpass_lm: dict = field(default_factory=dict)
    mask_bandpass_fibsem: dict = field(default_factory=dict)
    # Bandpass filtered images
    image_bandpass_filtered_lm: dict = field(default_factory=dict)
    image_bandpass_filtered_fibsem: dict = field(default_factory=dict)
    # Wavelet scales
    wavelet_scales_lm: list[dict] = field(default_factory=list)
    wavelet_scales_fibsem: list[dict] = field(default_factory=list)
    # Wavelet coefficients
    wavelet_coeffs_lm: list[dict] = field(default_factory=list)
    wavelet_coeffs_fibsem: list[dict] = field(default_factory=list)
    # Combined Image
    combined_image_lm: dict = field(default_factory=dict)
    combined_image_fibsem: dict = field(default_factory=dict)
    # Combined FFT
    crosscorrelation_lm: dict = field(default_factory=dict)
    crosscorrelation_fibsem: dict = field(default_factory=dict)
    wavelet_lm: dict = field(default_factory=dict)
    wavelet_fibsem: dict = field(default_factory=dict)
    padded_lm: dict = field(default_factory=dict)
    padded_fibsem: dict = field(default_factory=dict)
    # Translation values for displaying images side-by-side

    translation_x: float = 0.0

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value

if __name__ == "__main__":
    viewer = napari.Viewer(ndisplay=2)
    user_interface = GuiMainWindow(viewer=viewer)
    viewer.window.add_dock_widget(user_interface, area="right")
    napari.run()
