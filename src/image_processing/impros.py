from src.image_processing import detection_helpers as det_hlp
from src.image_processing.impros_conf import CONFIG
from skimage.transform import pyramid_gaussian
from skimage import transform
import matplotlib as mpl
import numpy as np
import requests
import random
import cv2
import os

class ImageProcessor(object):
    def __init__(self):
        pass;

    @staticmethod
    def detect_face_ext(displ=None, path=None, img=None, visualize=False):
        """
            @descr:
                Detects face and localizes it with a rectangle. Then extends the
                rectangle by given `displ` values, if they don't move the rectangle
                beyond image borders. Otherwise, `displ` is half the distance to
                the image borders.
            @args:
                displ - (tuple(dx, dy)); max shift by Ox and Oy axis respectively
            @return:
                (tuple) - dimensions of extended face frame and axis shifts
        """

        face = ImageProcessor.detect_faces(path=path, img=img, count=1)

        if len(face) == 0:
            print('No face detected')
            return []

        if img is None:
            img = cv2.imread(path, 0)

        if img is None:
            print('Couldn\'t open file. Path: ', path)
            return []

        face = face[0]
        dx, dy = ImageProcessor.compute_shift(img.shape, face, displ)

        # exception handling. a weird case.
        if dx < 0 or dy < 0:
            print('weird case occured! Path:', path)
            return []

        x, y, w, h = face
        X, Y = x-dx, y-dy
        W, H = w+2*dx, h+2*dy

        if visualize:
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
            cv2.rectangle(img,(X,Y),(X+W,Y+H),(0,255,0),2)
            cv2.imshow('img', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        # return dimensions of extended face frame and axis shifts
        return (X, Y, W, H, dx, dy)

    @staticmethod
    def compute_shift(shape, face, displ):
        imw, imh = shape
        x, y, w, h = face
        dx, dy = (int(0.3*w), int(0.3*h)) if displ is None else displ

        dx1 = dx if x-2*dx >= 0 else x/2
        dx2 = dx if imw  >= (x+w) + 2*dx else (imw - (x+w))/2
        dx = int(min(dx1, dx2))

        dy1 = dy if y-2*dy >= 0 else y/2
        dy2 = dy if imh  >= (y+h) + 2*dy else (imh - (y+h))/2
        dy = int(min(dy1, dy2))

        return (dx, dy)

    @staticmethod
    def detect_faces(path=None, img=None, count=None):
        """
            @args:
                path - (str); relative path to the image
                img - (ndarray); 2-D image array
                count - (int); number of faces to return. if None, returns all faces that were detected
            @return:
                [z] – list of `count` tuples at max (if count is set) where z is (x, y, w, h) for each detected face
        """
        if img is None and path is None:
            print('Can\'t process image. Provide either a path or an image array')
            return []
        elif img is None and not path is None:
            img = cv2.imread(path, 0)

        if img is None:
            print('Couldn\'t open file. Path: ', path)
            return []

        face_cascade = cv2.CascadeClassifier();

        if not face_cascade.load(CONFIG['haar_conf']['face_clf']):
            print('Couldn\'t load face classifier xml')
            return [];

        faces = face_cascade.detectMultiScale(img, 1.22, 6)

        # if no faces found or there are too many, return empty tuple
        if count is None:
            return faces
        if not count is None and len(faces) < count:
            return [];
        return faces[:count]

    @staticmethod
    def detect_eyes(img, visualize=False):
        if img is None: return;

        eye_cascade = cv2.CascadeClassifier();
        if not eye_cascade.load(CONFIG['haar_conf']['eye_clf']):
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

    @staticmethod
    def detect_mouth(img, visualize=False):
        if img is None: return;

        smile_cascade = cv2.CascadeClassifier();
        if not smile_cascade.load(CONFIG['haar_conf']['mouth_clf']):
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

    @staticmethod
    def detect_nose(img, eyes_rect, visualize=False):
        """
            @descr:
                approximates nose position by finding eyeballs and rotating image,
                based on the direction vector between detected eyeballs
            @args:
                img - (ndarray); image to detect nose in
                eyes_rect - (ndarray); [x, y, w, h] for rectangle, which localizes eyes
        """
        if img is None: return;
        _eyes_rect = (eyes_rect[0], eyes_rect[1], eyes_rect[2], eyes_rect[3])
        return ImageProcessor._detect_nose(img, _eyes_rect, ImageProcessor.detect_eyeballs(img, _eyes_rect, visualize), visualize=visualize)

    @staticmethod
    def detect_eyeballs(img, eyes_rect, visualize=False):
        """
            @descr:
                finds eyeballs by applying DoG and looking for local maxima inside eyes_rect
        """
        x, y, w, h = eyes_rect
        left_eye = img[y:y+h, x:(2*x+w)/2]
        right_eye = img[y:y+h, (2*x+w)/2:x+w]

        left_blob = det_hlp.filter_blobs(det_hlp.show_eyeballs(left_eye), w/2, h, left_eye)
        right_blob = det_hlp.filter_blobs(det_hlp.show_eyeballs(right_eye), w/2, h, right_eye)
        if left_blob is None or right_blob is None:
            return None

        lx, rx = left_blob[1], right_blob[1] + w/2
        ly, ry = left_blob[0], right_blob[0]
        eye_vector = np.array([rx-lx, ry-ly]) / det_hlp.v_len((rx-lx, ry-ly)) # (x, y) -> direction vector for eyeballs normalized

        if visualize:
            det_hlp.visualize_blobs(left_eye, right_eye, left_blob, right_blob)

        return ((lx, ly), (rx, ry), eye_vector)

    @staticmethod
    def _detect_nose(img, eyes_rect, eyeballs, visualize=False):
        """
            @args:
                eyeballs - (tuple);  contains (x, y) for left and right eyeballs
                                    and normalized direction vector for eyeballs
        """
        if eyeballs is None:
            return None
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

        return (X, Y, w/3, height, deg)

    @staticmethod
    def crop(img, dims):
        """
            @args:
                img - (numpy.array); image to crop from
                dims - (tuple); position and dimesnions of image to crop | (x, y, w, h)
        """
        x, y, w, h = dims[:4]
        return img[y:y+h, x:x+w]

    @staticmethod
    def extend(shape, dims, displacement=None):
        imw, imh = shape[:2]
        x, y, w, h = dims
        dx, dy = (int(0.3*w), int(0.3*h)) if displacement is None else displacement

        dx1 = dx if x-2*dx > 0 else x/2
        dx2 = dx if imw  > (x+w) + 2*dx else (imw - (x+w))/2
        dx = max(int(min(dx1, dx2)), 0)

        dy1 = dy if y-2*dy >= 0 else y/2
        dy2 = dy if imh  >= (y+h) + 2*dy else (imh - (y+h))/2
        dy = max(int(min(dy1, dy2)), 0)

        # exception handling. a weird case.
        if dx < 0 or dy < 0:
            return None

        # return dimensions of extended face frame and axis shifts
        return [x-dx, y-dy, w+2*dx, h+2*dy, dx, dy]

    @staticmethod
    def resize(img, size=CONSTANTS['resize_values'], preserve_range=True):
        return transform.resize(img, size, preserve_range=preserve_range)

    @staticmethod
    def get_faces_fpp(link):
        response = requests.get("https://faceplusplus-faceplusplus.p.mashape.com/detection/detect",
            params={
                'attribute': 'gender,race',
                'url': link
            },
            headers={
                "X-Mashape-Key": "rfOVSXuQohmshMrmwqe5mejsYueOp1icOY9jsnjTyfzOLZEkDN",
                "Accept": "application/json"
            }
        )
        try:
            json = response.json()
        except:
            print(response)
            return []
        if 'error' in json:
            print(json)
            return []
        return json

    @staticmethod
    def get_faces_facerect(link=None, filename=None, features=True):
        if link is None and filename is None:
            raise Exception('bad arguments')
        if link is not None:
            response = requests.get("https://apicloud-facerect.p.mashape.com/process-url.json",
                params={
                    'url': link,
                    'features': features
                },
                headers={
                    "X-Mashape-Key": "KAYR0pJ7v4mshZv89eZehTaFHEH5p1aHcH6jsnv2HKQQP0mqry",
                    "Accept": "application/json"
                }
            )
        elif filename is not None:
            response = requests.post("https://apicloud-facerect.p.mashape.com/process-file.json",
                files={ "image": open(filename, mode="rb") },
                data={ 'features': features },
                headers={
                    "X-Mashape-Key": "KAYR0pJ7v4mshZv89eZehTaFHEH5p1aHcH6jsnv2HKQQP0mqry",
                    "Accept": "application/json"
                }
            )
        try:
            json = response.json()
        except:
            print(response)
            return []
        if 'error' in json:
            print(json)
            return []
        return json['faces']

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
        return transform.resize(img, size, preserve_range=False)

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

    @staticmethod
    def draw_rect(img, dims):
        x,y,w,h = dims
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
        return img

    @staticmethod
    def check_import():
        print('Image processor imported successfuly')