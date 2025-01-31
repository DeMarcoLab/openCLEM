# dcam_show_single_captured_image.py : Jun 18, 2021
#
# Copyright (C) 2021 Hamamatsu Photonics K.K.. All right reserved.
#
# This sample source code just shows how to use DCAM-API.
# The performance is not guranteed.

"""
Sample script for showing a captured image with dcam.py
"""

from dcam import *

# pip install opencv-python
# import cv2
import matplotlib.pyplot as plt


def dcamtest_show_framedata(data):
    """
    Show numpy buffer as an image

    Arg1:   NumPy array
    """
    print(data)
    # plt.imshow(data)
    # plt.show()
    # plt.imshow('test', data)
    return

    if data.dtype == np.uint16:
        imax = np.amax(data)
        if imax > 0:
            imul = int(65535 / imax)
            # print('Multiple %s' % imul)
            data = data * imul

        plt.imshow('test', data)
        # cv2.waitKey(0)
    else:
        print('-NG: dcamtest_show_image(data) only support Numpy.uint16 data')


def dcam_show_single_captured_image(iDevice=0):
    """
    Capture and show a image
    """
    if Dcamapi.init() is not False:
        dcam = Dcam(iDevice)
        if dcam.dev_open() is not False:
            if dcam.buf_alloc(1) is not False:

                dcam.prop_setvalue(DCAM_IDPROP.EXPOSURETIME, 0.01)
                dcam.prop_setvalue(DCAM_IDPROP.TRIGGERSOURCE, 2)
                dcam.prop_setvalue(DCAM_IDPROP.TRIGGERACTIVE, 2)
                dcam.prop_setvalue(DCAM_IDPROP.TRIGGER_MODE, 1)
                dcam.prop_setvalue(DCAM_IDPROP.TRIGGERPOLARITY, 2)

                if dcam.cap_snapshot() is not False:
                    timeout_milisec = 2000
                    while True:
                        if dcam.wait_capevent_frameready(timeout_milisec) is not False:
                            dcam.cap_firetrigger()
                            data = dcam.buf_getlastframedata()
                            # data = dcam.buf_getframedata()
                            dcamtest_show_framedata(data)
                            break

                        dcamerr = dcam.lasterr()
                        if dcamerr.is_timeout():
                            print('===: timeout')
                            continue

                        print('-NG: Dcam.wait_event() fails with error {}'.format(dcamerr))
                        break
                else:
                    print('-NG: Dcam.cap_start() fails with error {}'.format(dcam.lasterr()))

                dcam.buf_release()
            else:
                print('-NG: Dcam.buf_alloc(1) fails with error {}'.format(dcam.lasterr()))
            dcam.dev_close()
        else:
            print('-NG: Dcam.dev_open() fails with error {}'.format(dcam.lasterr()))
    else:
        print('-NG: Dcamapi.init() fails with error {}'.format(Dcamapi.lasterr()))

    Dcamapi.uninit()


if __name__ == '__main__':
    dcam_show_single_captured_image()
