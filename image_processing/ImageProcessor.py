import numpy as np
import cv2
import os

class ImageProcessor(object):
    """docstring for ImageProcessor"""
    def __init__(self, img_dir_list, face_clf, eye_clf, nose_clf, smile_clf):
        """
            @args:
                img_dir_list - (list); list of directories to search for images in. must be inside 'data' directory
        """

        self.img_dir_list = img_dir_list
        self.face_clf = face_clf
        self.eye_clf = eye_clf
        self.nose_clf = nose_clf
        self.smile_clf = smile_clf

        self.DEFAULT = ''

    def propagate_images(self):
        """
            goes over each directory in self.img_dir_list,
            finds images inside, looks for faces and crops them,
            finds eyes, eyebrows, mouth and nose and crops them
        """

        if len(self.img_dir_list) == 0:
            self.img_dir_list = os.listdir('./data')

        for dir in self.img_dir_list:
            if os.path.isfile('./data/' + dir):
                self._detect_face(dir)
            else:
                for fn in os.listdir('./data/' + dir):
                    if os.path.isfile('./data/' + dir + '/' + fn):
                        self._detect_face(dir, fn)


    def _detect_face(self, dir, fn=''):

        """
            @args:
                dir - (str); directory name to scan photos in (may be a file name in case `fn` is not set)
                fn - (str) [optional]; filename to find face in
        """

        face_cascade = cv2.CascadeClassifier();

        if not face_cascade.load(self.face_clf):
            print('Couldn\'t load face classifier xml')
            return;

        open_path_tmp = './data/{0}' if fn == self.DEFAULT else './data/{0}/{1}'

        img = cv2.imread(open_path_tmp.format(dir, fn))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, 1.3, 4)

        # if no faces found or there are too many, remove the file
        if len(faces) != 1:
            print('Either no or too many faces found')
            os.remove(open_path_tmp.format(dir, fn))
            return;

        # cropp face and save it
        _dir = dir.split('.')[0] if fn == '' else dir
        _fn =  fn.split('.')[0]
        fmt = 'jpg'
        slash_sign = '' if fn == '' else '/'

        x, y, w, h = faces[0]
        cv2.imwrite('./data/{0}{1}{2}{3}.{4}'.format(_dir, slash_sign, _fn, '_', fmt), gray[y:y+h, x:x+w])


    def _detect_eyes(self, img):

        eye_cascade = cv2.CascadeClassifier();

        if not eye_cascade.load(self.eye_clf):
            print('Couldn\'t load eye classifier xml')
            return;

        # img = exposure.equalize_hist(img)
        upper_half = img[:2*img.shape[1]/3, 0:img.shape[0]]
        eyes = eye_cascade.detectMultiScale(upper_half)

        for (x, y, w, h) in eyes:
            cv2.rectangle(upper_half,(x,y),(x+w,y+h),(0,255,0),2)
        cv2.imshow('upper_half', upper_half)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def _detect_mouth(self, img):

        smile_cascade = cv2.CascadeClassifier();

        if not smile_cascade.load(self.smile_clf):
            print('Couldn\'t load smile classifier xml')
            return;

        img = img[2*img.shape[1]/3:, 0:img.shape[0]]

        smiles = smile_cascade.detectMultiScale(img, 1.4, 6)

        for (x, y, w, h) in smiles:
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
        cv2.imshow('img', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def _detect_nose(self, img):

        noise_cascade = cv2.CascadeClassifier();

        if not noise_cascade.load(self.nose_clf):
            print('Couldn\'t load nose classifier xml')
            return;

        width = img.shape[0]
        height = img.shape[1]

        middle = img[height*(2/5) : height*(4/5), width/4:width*(3/4)]
        noses = noise_cascade.detectMultiScale(middle)

        for (x, y, w, h) in noses:
            cv2.rectangle(middle,(x,y),(x+w,y+h),(0,255,0),2)
        cv2.imshow('middle', middle)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


face_clf = './clf/haarcascade_frontalface_default.xml'
eye_clf = './clf/eyes1.xml'
smile_clf = './clf/mouth.xml'
nose_clf = './clf/nose.xml'

imp = ImageProcessor([], face_clf, eye_clf, nose_clf, smile_clf)
