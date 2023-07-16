import numpy as np
import cv2
import time
import os

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_CONVERT_RGB, 0)
# Use raw mode
cap.set(cv2.CAP_PROP_ZOOM, 0x8002)
# Calibrate
#cap.set(cv2.CAP_PROP_ZOOM, 0x8000)


def get_frame():
    ret, frame = cap.read()

    frame = frame.reshape(196, 256, 2)  # 0: LSB. 1: MSB

    # Remove the four extra rows
    # Convert to uint16
    return frame[:192, ...].view(dtype=np.dtype(('<u2', [('x', np.uint8, 2)]))).astype(np.float32)


bkg = None
dark = None
flat = None

flatfile = "flat.npy"
if os.path.exists(flatfile):
    print("flat found")
    flat = np.load(flatfile, allow_pickle=True)
    print(f"flat Min: {flat.min()}, Max: {flat.max()}, Avg: {flat.mean()}")
    print(f"shape {flat.shape}")

darkfile = "dark.npy"
if os.path.exists(darkfile):
    print("dark found")
    dark = np.load(darkfile, allow_pickle=True)
    print(f"dark Min: {dark.min()}, Max: {dark.max()}, Avg: {dark.mean()}")
    print(f"shape {dark.shape}")


while(True):
    frame = get_frame()

    n=3

    for i in range(n-1):
        frame += get_frame()

    frame /=n




    #displayframe = frame.copy()
    displayframe = cv2.normalize(frame, None, 0, 65535, cv2.NORM_MINMAX)
    # Sketchy auto-exposure
    displayframe -= displayframe.min()
    displayframe /= displayframe.max()
    displayframe -= displayframe.mean() - 3*displayframe.std()
    displayframe /= displayframe.max()# + 3*displayframe.std()
    displayframe = np.clip(displayframe, 0, 1) ** (1/1)

    print(cap.get(cv2.CAP_PROP_FPS))


    scale = 2
    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('frame', scale*192, scale*256)

    cv2.imshow('frame',displayframe)
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break
    elif key & 0xFF == ord('s'):
        print("closing shutter")
        cap.set(cv2.CAP_PROP_ZOOM, 0x8000)

    elif key & 0xFF == ord('d'):
        print("closing shutter")
        cap.set(cv2.CAP_PROP_ZOOM, 0x8000)

        # trash a few frames
        for i in range(4):
            darkframe = get_frame()

        n = 11
        dark_array = np.zeros((darkframe.shape[0], darkframe.shape[1], darkframe.shape[2],n), dtype=np.float32)

        for i in range(n):
            dark_array[:,:,:,i] = get_frame()

        dark = np.mean(dark_array, axis=3)


        dark -= np.median(dark_array)

        print(f"dark Min: {dark.min()}, Max: {dark.max()}, Avg: {dark.mean()}")

    elif key & 0xFF == ord('w'):
        np.save("dark.npy", dark)
        np.save("flat.npy", flat)
        print("Cal Files written")

    elif key & 0xFF == ord('m'):
        print(f"Min: {frame.min()}, Max: {frame.max()}, Avg: {frame.mean()}, Std: {frame.std()}")

    elif key & 0xFF == ord('b'):

        # trash a few frames
        for i in range(1):
            bkg = get_frame()


        n = 20
        bkg_array = np.zeros((bkg.shape[0], bkg.shape[1], 1, n), dtype=np.float32)

        for i in range(n):
            bkg_array[:, :, :, i] = get_frame()

        bkg = np.median(bkg_array, axis=3)

        if dark is not None:
            bkg -= dark

        print(f"bkg Min: {bkg.min()}, Max: {bkg.max()}, Avg: {bkg.mean()}")
        time.sleep(1)

    elif key & 0xFF == ord('f'):

        # trash a few frames
        for i in range(1):
            flat = get_frame()

        n = 15
        flat_array = np.zeros((flat.shape[0], flat.shape[1], 1, n), dtype=np.float32)

        for i in range(n):
            flat_array[:, :, :, i] = get_frame()

        flat = np.mean(flat_array, axis=3)

        if dark is not None:
            flat -= dark
            print(f"flat Min: {flat.min()}, Max: {flat.max()}, Avg: {flat.mean()}")

    elif key & 0xFF == ord('l'):
        flat = np.load(flatfile, allow_pickle=True)

    elif key & 0xFF == ord('c'):
        bkg = None
        dark = None
        flat=None

    elif key & 0xFF == ord('y'):
        cap.set(cv2.CAP_PROP_ZOOM, 0x8005)
    elif key & 0xFF == ord('n'):
        cap.set(cv2.CAP_PROP_ZOOM, 0x8020)
    elif key & 0xFF == ord('h'):
        cap.set(cv2.CAP_PROP_ZOOM, 0x8021)
    elif key & 0xFF == ord('0'):
        cap.set(cv2.CAP_PROP_ZOOM, 0x8800)
    elif key & 0xFF == ord('1'):
        cap.set(cv2.CAP_PROP_ZOOM, 0x8801)
    elif key & 0xFF == ord('2'):
        cap.set(cv2.CAP_PROP_ZOOM, 0x8802)
    elif key & 0xFF == ord('3'):
        cap.set(cv2.CAP_PROP_ZOOM, 0x8003)
    elif key & 0xFF == ord('4'):
        cap.set(cv2.CAP_PROP_ZOOM, 0x8004)
    elif key & 0xFF == ord('5'):
        cap.set(cv2.CAP_PROP_ZOOM, 0x8005)
    elif key & 0xFF == ord('6'):
        cap.set(cv2.CAP_PROP_ZOOM, 0x8006)
    elif key & 0xFF == ord('7'):
        cap.set(cv2.CAP_PROP_ZOOM, 0x8007)

cap.release()