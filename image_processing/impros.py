from skimage import transform
import detection_helpers as det_hlp
import matplotlib as mpl
import numpy as np
import cv2
import os

class ImageProcessor(object):
    def __init__(self, img_dir_list, face_clf, eye_clf, nose_clf, mouth_clf):
        """
            @args:
                img_dir_list - (list); list of directories to search for images in. must be inside 'photos' directory
        """
        self.img_dir_list = img_dir_list
        self.face_clf = face_clf
        self.eye_clf = eye_clf
        self.nose_clf = nose_clf
        self.mouth_clf = mouth_clf

    def propagate_images(self, dsize=None, clean=False):
        """
            goes over each directory in self.img_dir_list,
            finds images inside, looks for faces and crops them,
            finds eyes, eyebrows, mouth and nose and crops them
        """
        # go over all files in "./photos" if `self.img_dir_list` is empty
        if len(self.img_dir_list) == 0:
            self.img_dir_list = os.listdir('./photos')

        for dir in self.img_dir_list:
            if os.path.isdir('./photos/' + dir):
                for fn in os.listdir('./photos/' + dir):
                    path = './photos/' + dir + '/' + fn
                    if os.path.isfile(path):
                        self.detect_face(path, crop=True, resize=True, dsize=dsize)

    def detect_face(self, path, crop=False, resize=False, dsize=None):
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

        if img == None:
            print('Couldn\'t open file. Path: ', path)
            return tuple()

        faces = face_cascade.detectMultiScale(img, 1.3, 4)

        # if no faces found or there are too many, remove the file
        if len(faces) != 1:
            os.remove(path)
            return tuple();

        if crop:
            # crop face and save it
            _path = path.split('/')
            _fn =  _path[-1].split('.')[0]
            _path = '/'.join(_path[:-1])

            self.crop(img, faces[0], _path, _fn, resize=resize, dsize=dsize)

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

        img = img[2*img.shape[1]/3:, 0:img.shape[0]]

        smiles = smile_cascade.detectMultiScale(img, 1.4, 6)

        if visualize:
            for (x, y, w, h) in smiles:
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
            cv2.imshow('img', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return smiles

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
            cropped = transform.resize(cropped, dsize, preserve_range=True)

        if not full_path:
            cv2.imwrite('{0}/{1}_.{2}'.format(path, fn, fmt), cropped)
        else:
            cv2.imwrite(full_path, cropped)

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
        eye_vector = np.array([rx-lx, ry-ly]) / det_hlp.dist((0,0), (rx-lx, ry-ly)) # (x, y) -> direction vector for eyeballs normalized

        if visualize:
            det_hlp.visualize_blobs(left_eye, right_eye, left_blob, right_blob)

        return [(lx, ly), (rx, ry), eye_vector]

    def _detect_nose(self, img, eyes_rect, eyeballs, visualize=False):
        """
            @args:
                eyeballs - (list);  contains (x, y) for left and right eyeballs 
                                    and normalized direction vector for eyeballs
        """
        x, y, w, h = eyes_rect
        leye = eyeballs[0]
        reye = eyeballs[1]
        eye_vector = eyeballs[2]
        norm_vector = np.array([-eye_vector[1], eye_vector[0]]) # (x, y) -> direction vector for nose normalized

        height = 0.9*det_hlp.v_len((reye[0]-leye[0], reye[1]-leye[1]))
        X = x+w/2-w/6
        Y = y+h/2

        rows, cols = img.shape
        anchor = [x+w/2, y+h/2]
        M = cv2.getRotationMatrix2D((anchor[0], anchor[1]), -det_hlp.angle((0, 1), norm_vector), 1) # 1 is passed to preserve color depth
        dst = cv2.warpAffine(img, M, (cols, rows))

        if visualize:
            nose = mpl.patches.Rectangle((X, Y), w/3, height, fill=False)
            det_hlp.visualize_nose(dst, nose)

        return [X, Y, w/3, height]