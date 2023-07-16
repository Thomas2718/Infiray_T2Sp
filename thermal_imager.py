import numpy as np
import cv2
import time
import os
import logging
import enum
logger = logging.getLogger(__name__)


class T2Sp_cmd(enum.IntEnum):

    # working and tested commands
    close_shutter = 0x8000
    background_calibration = 0x8001
    raw_output = 0x8002
    cmd3 = 0x8003
    nuc_16bit_output = 0x8004
    yuyv_output = 0x8005

    save_config = 0x80FE
    save_parameters = 0x80FF

    high_gain = 0x8020
    low_gain = 0x8021

    # not working yet
    palette_white_hot = 0x8800
    palette_black_hot = 0x8801
    palette_iron = 0x8802
    palette_lava= 0x8803
    palette_rainbow = 0x8804
    palette_iron_grey = 0x8805
    palette_red_hot = 0x8806
    palette_rainbow2 = 0x8807


    sys_reset_to_rom = 0x0805
    spi_transfer = 0x8201
    get_device_info = 0x8405
    pseudo_color = 0x8005
    shutter_vtemp = 0x840c
    prop_tpd_params = 0x8514
    cur_vtemp = 0x8b0d
    preview_start = 0xc10f
    preview_stop = 0x020f
    y16_preview_start = 0x010a
    y16_preview_stop = 0x020a


class ThermalImager:
    def __init__(self, camera_index, data_rows):
        self.image_height = None
        self.image_width = None

        self.data_rows = data_rows

        self.flat = None
        self.dark = None
        self.background = None


        self.enable_dark_correction = True
        self.enable_flat_correction = True
        self.enable_background_correction = False

        self.flatfile = r"./calibration_files/flat.npy"
        self.darkfile = r"./calibration_files/dark.npy"


        self.capture = cv2.VideoCapture(camera_index)
        self.frame_count = 0

    def set(self, cmd):
        raise NotImplementedError

    def query(self, cmd):
        raise NotImplementedError

    def load_calibration_files(self):
        if os.path.exists(self.flatfile):
            logger.info("flat found")
            self.flat = np.load(self.flatfile, allow_pickle=True)
            logger.info(f"flat Min: {self.flat.min()}, Max: {self.flat.max()}, Avg: {self.flat.mean()}")
            logger.info(f"flat shape {self.flat.shape}")
        else:
            logger.exception("Flat file not found")

        if os.path.exists(self.darkfile):
            logger.info("dark found")
            self.dark = np.load(self.darkfile, allow_pickle=True)
            logger.info(f"dark Min: {self.dark.min()}, Max: {self.dark.max()}, Avg: {self.dark.mean()}")
            logger.info(f"shape {self.dark.shape}")
        else:
            logger.exception("Dark file not found")

    def store_calibration_files(self):
        if os.path.exists(os.path.basename(self.darkfile)) and os.path.exists(os.path.basename(self.darkfile)):
            np.save(self.darkfile, self.dark)
            np.save(self.flatfile, self.flat)
            logger.info("Cal Files written")
        else:
            logger.exception("Cal File folder not found")

    def get_frame(self):
        raise NotImplementedError

    def close(self):
            self.capture.release()


class T2Sp(ThermalImager):
    def __init__(self, camera_index):
        super().__init__(camera_index, data_rows=4)

        self.image_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.image_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)) - self.data_rows
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        logger.info((f"Found camera {self.image_height}x{self.image_width} @ {self.fps}"))

        self.initialize_camera()
        self.load_calibration_files()

    def set(self, cmd):
        self.capture.set(cv2.CAP_PROP_ZOOM, cmd)

    def query(self, cmd):
        return self.capture.get(cmd)

    def initialize_camera(self):
        self.capture.set(cv2.CAP_PROP_CONVERT_RGB, 0)
        self.set(T2Sp_cmd.raw_output)

    def get_frame(self):
        ret, raw_frame = self.capture.read()

        #np.frombuffer(raw_frame, dtype=np.uint8).reshape((P2Pro_resolution[1] // 2, P2Pro_resolution[0], 2))

        # reshape to 2D
        frame = raw_frame.reshape(self.image_height+self.data_rows, self.image_width, 2)

        #seperate metadata from image
        self.metadata = frame[self.image_height:]
        frame = frame[:self.image_height]

        # cast to 16bit
        frame = frame.view(dtype=np.dtype(('<u2', [('x', np.uint8, 2)]))).astype(np.float32)
        #logger.info(f"acq frame {frame.shape}")
        return frame

    def close_shutter(self):
        self.set(T2Sp_cmd.close_shutter)

    def enable_room_temperature_mode(self):
        self.set(T2Sp_cmd.high_gain)

    def enable_high_temperature_mode(self):
        self.set(T2Sp_cmd.low_gain)

    def get_n_averaged_frames(self, n=11, trash_frames=4):


        for i in range(trash_frames):
            frame = self.get_frame()

        frames = np.zeros((self.image_height, self.image_width, frame.shape[2], n),
                              dtype=np.float32)

        for i in range(n):
            frames[:, :, :, i] = self.get_frame()

        avg_frames = np.mean(frames, axis=3)
        logger.info(f"frames Min: {self.dark.min()}, Max: {self.dark.max()}, Avg: {self.dark.mean()}")
        return avg_frames

    def dark_calibration(self):
        self.close_shutter()
        self.dark = self.get_n_averaged_frames(11,4)

    def flat_calibration(self):
        self.dark_calibration()
        time.sleep(2)
        self.flat = self.get_n_averaged_frames(11, 4)







if __name__ == "__main__":

    cam = T2Sp(0)

