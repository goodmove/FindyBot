import cv2
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
from skimage.morphology import reconstruction
import numpy as np
from skimage.feature import blob_dog
from math import sqrt, cos, acos, degrees

def invert(img):
    max = (0.2126 + 0.7152 + 0.0722)*255
    img = [max - p for p in img]
    return img

def show_eyeballs(work_im):
    work_im = invert(work_im)
    work_im = gaussian_filter(work_im, 1.2)

    seed = np.copy(work_im)
    seed[1:-1, 1:-1] = work_im.min()
    mask = work_im

    dilated = reconstruction(seed, mask, method='dilation')

    image = work_im - dilated

    blobs_dog = blob_dog(image, min_sigma=5, max_sigma=10, threshold=.6)
    blobs_dog[:, 2] = blobs_dog[:, 2] * sqrt(2)

    return blobs_dog

def dist(p1, p2):
    res = sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    return res if res > 0 else 10 ** (-4)

def cof(blob, w, h, img):
    y, x, sigma = blob
    R = sigma * sqrt(2)
    max = (0.2126 + 0.7152 + 0.0722)*255
    intensity = max - img[y,x]

    return intensity * R / dist((x,y), (w/2,h/2))

def filter_blobs(blobs, w, h, img):
    scores = [(ind, cof(blob, w, h, img)) for ind, blob in enumerate(blobs)]
    return blobs[max(scores, key=lambda s: s[1])[0]]

def scalar_mult(v1, v2):
    return v1[0]*v2[0] + v1[1]*v2[1]

def v_len(v):
    return dist(v, (0,0))

def angle(v1, v2):
    return degrees(acos( scalar_mult(v1, v2) / (v_len(v1) * v_len(v2)) ))

def visualize_blobs(left_eye, right_eye, left_blob, right_blob):
    fig, (ax1, ax2) = plt.subplots(1, 2, sharex=True, sharey=True)

    def draw_blob(blob, axis):
        y, x, r = blob
        c = plt.Circle((x, y), r, color='red', linewidth=2, fill=False)
        axis.add_patch(c)

    draw_blob(left_blob, ax1)
    draw_blob(right_blob, ax2)
    ax1.imshow(left_eye)
    ax2.imshow(right_eye)
    plt.show()

def visualize_nose(img, nose):
    fig, (ax) = plt.subplots(1, 1)
    ax.imshow(img)
    ax.add_patch(nose)
    plt.show()