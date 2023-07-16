from thermal_imager import T2Sp, ThermalImager, T2Sp_cmd
import numpy as np
import cv2
import time
import os
import logging
import enum
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Viewer:
    def __init__(self, imager: ThermalImager, cam_index=1, scale=2, n_avg=1):
        self.imager = imager
        self.height = imager.image_height
        self.width = imager.image_width
        self.scale = scale
        self.n_avg = n_avg

        self.normalize_image = True
        self.auto_exposure = True
        self.gamma = 1
        self.min = -1
        self.max = 2

    def run(self):

        while (True):
            frame = self.imager.get_frame()

            for i in range(self.n_avg - 1):
                frame += self.imager.get_frame()

            frame /= self.n_avg

            frame -= self.imager.dark
            frame /= self.imager.flat

            if self.auto_exposure:
                self.min = frame.min()
                self.max = frame.max()

            frame -= self.min
            frame /= self.max
            # frame -= frame.mean() - 3 * frame.std()
            # frame /= frame.max()  # + 3*displayframe.std()
            frame = np.clip(frame, 0, 1) ** (1 / self.gamma)



            if self.normalize_image:
                frame = cv2.normalize(frame, None, 0, 1, cv2.NORM_MINMAX)

            cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('frame', self.scale * self.height, self.scale * self.width)
            cv2.imshow('frame', frame)

            if self.process_key_input(cv2.waitKey(1)):
                self.imager.close()
                break

    def process_key_input(self, key):
        #logger.info(f"Key pressed {key} > {key & 0xFF}")

        if key & 0xFF == ord('q'):
            self.imager.close()
            return True

        elif key & 0xFF == ord('s'):
            self.imager.dark_calibration()

        elif key & 0xFF == ord('d'):
            self.imager.dark_calibration()

        elif key & 0xFF == ord('w'):
            self.imager.store_calibration_files()

        elif key & 0xFF == ord('m'):
            frame = self.imager.get_corrected_frame()
            print(f"Min: {frame.min()}, Max: {frame.max()}, Avg: {frame.mean()}, Std: {frame.std()}")
            print(f"Scale Min: {self.min}, Max: {self.max}")

        elif key & 0xFF == ord('b'):
            self.imager.background_calibration()

        elif key & 0xFF == ord('f'):
            self.imager.flat_calibration()

        elif key & 0xFF == ord('l'):
            self.imager.load_calibration_files()

        elif key & 0xFF == ord('c'):
            self.imager.enable_flat_correction = True
            self.imager.enable_dark_correction = True
            self.imager.enable_background_correction = True

        elif key & 0xFF == ord('c'):
            self.imager.enable_flat_correction = False
            self.imager.enable_dark_correction = False
            self.imager.enable_background_correction = False

        elif key & 0xFF == ord('a'):
            self.auto_exposure = not self.auto_exposure
            logger.info(f"auto_exposure {self.auto_exposure}")
            logger.info((f"min: {self.min} max: {self.max}"))

        elif key & 0xFF == ord('n'):
            self.normalize_image = not self.normalize_image
            logger.info(f"Normalize {self.normalize_image}")

        elif key & 0xFF == ord('g'):
           self.imager.enable_room_temperature_mode()

        elif key & 0xFF == ord('-'):
            self.gamma *=.9
            logger.info(f"Gamma {self.gamma}")

        elif key & 0xFF == ord('+'):
            self.gamma /=.9
            logger.info(f"Gamma {self.gamma}")

        elif key & 0xFF == ord('h'):
           self.imager.enable_high_temperature_mode()

        elif key & 0xFF == ord('r'):
           self.imager.enable_room_temperature_mode()


        elif key & 0xFF == ord('0'):
            self.imager.capture.set(cv2.CAP_PROP_ZOOM, 0x8800)
        elif key & 0xFF == ord('1'):
            self.imager.capture.set(cv2.CAP_PROP_ZOOM, 0x8801)
        elif key & 0xFF == ord('2'):
            self.imager.capture.set(cv2.CAP_PROP_ZOOM, 0x8802)
        elif key & 0xFF == ord('3'):
            self.imager.capture.set(cv2.CAP_PROP_ZOOM, 0x8003)
        elif key & 0xFF == ord('4'):
            self.imager.capture.set(cv2.CAP_PROP_ZOOM, 0x8004)
        elif key & 0xFF == ord('5'):
            self.imager.capture.set(cv2.CAP_PROP_ZOOM, 0x8005)
        elif key & 0xFF == ord('6'):
            self.imager.capture.set(cv2.CAP_PROP_ZOOM, 0x8006)
        elif key & 0xFF == ord('7'):
            self.imager.capture.set(cv2.CAP_PROP_ZOOM, 0x8007)


    def calibrate(self, frame):
        pass
        #T = B / np.log( (Gain*emissivity) / R*(S_obj-dark))




if __name__ == "__main__":

    cam = T2Sp(0)
    view = Viewer(cam)
    view.run()
