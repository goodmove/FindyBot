import numpy as np
import cv2
import os

class ImageProcessor(object):

    def __init__(self, img_dir_list, face_clf, eye_clf, nose_clf, mouth_clf):
        """
            @args:
                img_dir_list - (list); list of directories to search for images in. must be inside 'data' directory
        """
        self.img_dir_list = img_dir_list
        self.face_clf = face_clf
        self.eye_clf = eye_clf
        self.nose_clf = nose_clf
        self.mouth_clf = mouth_clf

    def propagate_images(self):
        """
            goes over each directory in self.img_dir_list,
            finds images inside, looks for faces and crops them,
            finds eyes, eyebrows, mouth and nose and crops them
        """
        # go over all files in "./data" if `self.img_dir_list` is empty
        if len(self.img_dir_list) == 0:
            self.img_dir_list = os.listdir('./data')

        for dir in self.img_dir_list:
            if os.path.isdir('./data/' + dir):
                for fn in os.listdir('./data/' + dir):
                    path = './data/' + dir + '/' + fn
                    if os.path.isfile(path):
                        self.detect_face(path, crop=True)


    def detect_face(self, path, crop=False):
        """
            @args:
                path = (str); relative path to the image
            @return:
                (x, y, w, h) – a tuple for one face detected
                () – empty tuple if zero or more than one face were detected
        """
        face_cascade = cv2.CascadeClassifier();

        if not face_cascade.load(self.face_clf):
            print('Couldn\'t load face classifier xml')
            return tuple();

        img = cv2.imread(path, 0)

        faces = face_cascade.detectMultiScale(img, 1.3, 4)

        # if no faces found or there are too many, remove the file
        if len(faces) != 1:
            print('Either no or too many faces found')
            os.remove(open_path_tmp.format(dir, fn))
            return tuple();

        if crop:
            # crop face and save it
            _path = path.split('/')
            _fn =  _path[-1].split('.')[0]
            _path = '/'.join(_path[:-1])

            self.crop(img, faces[0], _path, _fn)

        return faces[0]

    def detect_eyes(self, img, visualize=False):
        eye_cascade = cv2.CascadeClassifier();

        if not eye_cascade.load(self.eye_clf):
            print('Couldn\'t load eye classifier xml')
            return;

        upper_half = img[:2*img.shape[1]/3, 0:img.shape[0]]
        eyes = eye_cascade.detectMultiScale(upper_half)

        for (x, y, w, h) in eyes:
            cv2.rectangle(upper_half,(x,y),(x+w,y+h),(0,255,0),2)

        if visualize:
            cv2.imshow('upper_half', upper_half)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return eyes

    def detect_mouth(self, img, visualize=False):
        smile_cascade = cv2.CascadeClassifier();

        if not smile_cascade.load(self.mouth_clf):
            print('Couldn\'t load smile classifier xml')
            return;

        img = img[2*img.shape[1]/3:, 0:img.shape[0]]

        smiles = smile_cascade.detectMultiScale(img, 1.4, 6)

        for (x, y, w, h) in smiles:
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)

        if visualize:
            cv2.imshow('img', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return smiles

    def detect_nose(self, img, visualize=False):
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

        if visualize:
            cv2.imshow('middle', middle)
            cv2.waitKey(0)
            cv2.destroyAllWindows

        return noses

    def crop(self, img, dims, path, fn, full_path=None):
        """
            @args:
                img - (numpy.array); image to crop from
                dims - (tuple); position and dimesnions of image to crop | (x, y, w, h)
                path - (str); path name to save into
                fn - (str); filename to save with
                full_path - (str); if set, overrides path and fn entirely
        """
        fmt = 'jpg'
        x, y, w, h = dims

        if not full_path:
            cv2.imwrite('{0}/{1}_.{2}'.format(path, fn, fmt), img[y:y+h, x:x+w])
        else:
            cv2.imwrite(full_path, img[y:y+h, x:x+w])