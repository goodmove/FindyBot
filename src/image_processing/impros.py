from image_processing import detection_helpers as det_hlp
from image_processing.clf_constants import CONSTANTS
from skimage.transform import pyramid_gaussian
from skimage import transform
import matplotlib as mpl
import numpy as np
import random
import cv2
import os

class ImageProcessor(object):
    def __init__(
                self,
                face_clf=CONSTANTS['face_clf'],
                eye_clf=CONSTANTS['eye_clf'],
                mouth_clf=CONSTANTS['mouth_clf']
                ):
        self.face_clf = face_clf
        self.eye_clf = eye_clf
        self.mouth_clf = mouth_clf

    @staticmethod
    def detect_face_ext(bounds=None, path=None, img=None, visualize=False):
        """
            @descr:
                Detects face and localizes it with a rectangle. Then extends the
                rectangle by given `bounds` values, if they don't move the rectangle
                beyond image borders. Otherwise, `bounds` is half the distance to
                the image borders.
            @args:
                bounds - (tuple(dx, dy)); max shift by Ox and Oy axis respectively
            @return:
                (tuple) - dimensions of extended face frame and axis shifts
        """
        face = ImageProcessor.detect_face(path=path, img=img)

        if len(face) == 0:
            print('No face detected')
            return tuple()

        imw, imh = img.shape
        x, y, w, h = face
        dx, dy = (int(0.3*w), int(0.3*h)) if bounds is None else bounds

        dx1 = dx if x-2*dx > 0 else x/2
        dx2 = dx if imw  > (x+w) + 2*dx else (imw - (x+w))/2
        dx = int(min(dx1, dx2))

        dy1 = dy if y-2*dy >= 0 else y/2
        dy2 = dy if imh  >= (y+h) + 2*dy else (imh - (y+h))/2
        dy = int(min(dy1, dy2))

        # exception handling. a weird case.
        if dx < 0 || dy < 0:
            return tuple()

        X = x-dx
        Y = y-dy
        W = w+2*dx
        H = h+2*dy

        if visualize:
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
            cv2.rectangle(img,(X,Y),(X+W,Y+H),(0,255,0),2)
            cv2.imshow('img', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        # return dimensions of extended face frame and axis shifts
        return (X, Y, W, H, dx, dy)

    @staticmethod
    def detect_face(path=None, img=None):
        """
            @args:
                path - (str); relative path to the image
                img - (ndarray); 2-D image array
            @return:
                (x, y, w, h) – a tuple for one face detected
                () – empty tuple if zero or more than one face were detected
        """
        face_cascade = cv2.CascadeClassifier();

        if not face_cascade.load(CONSTANTS['face_clf']):
            print('Couldn\'t load face classifier xml')
            return tuple();

        if img is None and not path is None:
            img = cv2.imread(path, 0)
        elif img is None and path == None:
            print('Can\'t open image. Provide either a path or an image array')
            return tuple()

        if img is None:
            print('Couldn\'t open file. Path: ', path)
            return tuple()

        faces = face_cascade.detectMultiScale(img, 1.3, 4)

        # if no faces found or there are too many, return empty tuple
        if len(faces) != 1:
            return tuple();

        return faces[0]

    def detect_eyes(self, img, visualize=False):
        eye_cascade = cv2.CascadeClassifier();

        if not eye_cascade.load(self.eye_clf):
            print('Couldn\'t load eye classifier xml')
            return;

        upper_half = img[:2*img.shape[1]/3, 0:img.shape[0]]
        eyes = eye_cascade.detectMultiScale(upper_half)

        if visualize:
            for (x, y, w, h) in eyes:
                cv2.rectangle(upper_half,(x,y),(x+w,y+h),(0,255,0),2)
            cv2.imshow('upper_half', upper_half)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return eyes

    def detect_mouth(self, img, visualize=False):
        smile_cascade = cv2.CascadeClassifier();

        if not smile_cascade.load(self.mouth_clf):
            print('Couldn\'t load smile classifier xml')
            return;

        img = img[2*img.shape[1]/3:, :]

        smiles = smile_cascade.detectMultiScale(img, 1.4, 6)

        if visualize:
            for (x, y, w, h) in smiles:
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
            cv2.imshow('img', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return smiles

    def detect_nose(self, img, eyes_rect, visualize=False):
        """
            @descr:
                approximates nose position by finding eyeballs and rotating image,
                based on the direction vector between detected eyeballs
            @args:
                img - (ndarray); image to detect nose in
                eyes_rect - (ndarray); [x, y, w, h] for rectangle, which localizes eyes
        """
        _eyes_rect = (eyes_rect[0], eyes_rect[1], eyes_rect[2], eyes_rect[3])
        return self._detect_nose(img, _eyes_rect, self.detect_eyeballs(img, _eyes_rect, visualize), visualize=visualize)

    def detect_eyeballs(self, img, eyes_rect, visualize=False):
        """
            @descr:
                finds eyeballs by applying DoG and looking for local maxima inside eyes_rect
        """
        x, y, w, h = eyes_rect
        left_eye = img[y:y+h, x:(2*x+w)/2]
        right_eye = img[y:y+h, (2*x+w)/2:x+w]

        left_blob = det_hlp.filter_blobs(det_hlp.show_eyeballs(left_eye), w/2, h, left_eye)
        right_blob = det_hlp.filter_blobs(det_hlp.show_eyeballs(right_eye), w/2, h, right_eye)

        lx, rx = left_blob[1], right_blob[1] + w/2
        ly, ry = left_blob[0], right_blob[0]
        eye_vector = np.array([rx-lx, ry-ly]) / det_hlp.v_len((rx-lx, ry-ly)) # (x, y) -> direction vector for eyeballs normalized

        if visualize:
            det_hlp.visualize_blobs(left_eye, right_eye, left_blob, right_blob)

        return ((lx, ly), (rx, ry), eye_vector)

    def _detect_nose(self, img, eyes_rect, eyeballs, visualize=False):
        """
            @args:
                eyeballs - (tuple);  contains (x, y) for left and right eyeballs
                                    and normalized direction vector for eyeballs
        """
        x, y, w, h = eyes_rect
        leye, reye, eye_vector = eyeballs
        norm_vector = np.array([-eye_vector[1], eye_vector[0]]) # (x, y) -> direction vector for nose normalized

        height = 0.9*det_hlp.v_len((reye[0]-leye[0], reye[1]-leye[1]))
        X = x+w/2-w/6
        Y = y+h/2

        rows, cols = img.shape
        anchor = [x+w/2, y+h/2]
        deg = -det_hlp.angle((0, 1), norm_vector)
        M = cv2.getRotationMatrix2D((anchor[0], anchor[1]), deg, 1) # 1 is passed to preserve color depth
        dst = cv2.warpAffine(img, M, (cols, rows))

        if visualize:
            nose = mpl.patches.Rectangle((X, Y), w/3, height, fill=False)
            det_hlp.visualize_nose(dst, nose)

        return (X, Y, w/3, height)

    def crop(self, img, dims, path, fn, full_path=None, resize=False, dsize=None):
        """
            @args:
                img - (numpy.array); image to crop from
                dims - (tuple); position and dimesnions of image to crop | (x, y, w, h)
                path - (str); path name to save into
                fn - (str); filename to save with
                full_path - (str); if set, overrides path and fn entirely
                resize - (bool); True if cropped `img` needs to be resized
                dsize - (tuple); dimensions to resize to
        """
        fmt = 'jpg'
        x, y, w, h = dims

        cropped = img[y:y+h, x:x+w]

        if resize and dsize != None:
            cropped = self.resize_img(cropped, dsize)

        if not full_path:
            cv2.imwrite('{0}/{1}_.{2}'.format(path, fn, fmt), cropped)
        else:
            cv2.imwrite(full_path, cropped)

    @staticmethod
    def rotate_img(img, deg, anchor=None):
        w, h = img.shape
        if anchor == None:
            anchor = (w/2, h/2)
        M = cv2.getRotationMatrix2D(anchor, deg, 1) # 1 is passed to preserve color depth
        dst = cv2.warpAffine(img, M, (h, w))

        return dst

    @staticmethod
    def mirror_img(img, axis=1):
        return cv2.flip(img, axis)

    @staticmethod
    def image_pyr(img, downscale=2, layers=5):
        return tuple(pyramid_gaussian(img, downscale=downscale, max_layer=layers))

    @staticmethod
    def resize_img(img, size, preserve_range=True):
        return transform.resize(img, size, preserve_range=preserve_range)

    @staticmethod
    def shift_img(img, dims, shift_values, randomize=True):
        """
            @descr:
                shifts `img` by values set in `shift_values`
                if `randomize` is True, shifts by random values in [-z, z], z from `shift_values`
        """
        x, y, w, h = dims
        dx, dy = shift_values
        _dx = random.randint(-dx, dx) if randomize else dx
        _dy = random.randint(-dy, dy) if randomize else dy
        x, y = x+_dx, y+_dy
        return img[y:y+h, x:x+w]