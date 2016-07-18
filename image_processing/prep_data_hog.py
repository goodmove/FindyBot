from skimage.transform import pyramid_gaussian
from impros import ImageProcessor as impros
from skimage import feature
import cv2
import os


face_clf = 'clf/haarcascade_frontalface_alt.xml'
eye_clf = 'clf/eyes1.xml'

imp = impros(eye_clf=eye_clf, face_clf=face_clf)

def propagate_images(path, num_of_shifts, randomize, shift_values, crop_size):
    global imp
    img = cv2.imread(path, 0)
    if img is None:
        print('Couldn\'t open img. Path: ', path)
        return;

    # remove the original image
    os.remove(path)
    res = imp.detect_face_ext(bounds=shift_values, img=img)

    if len(res) == 0:
        return;
    x,y,w,h,dx,dy = res

    for i in range(num_of_shifts):
        shifted = imp.shift_img(img, (x,y,w,h), (dx,dy), randomize=randomize)
        resized = imp.resize_img(shifted, crop_size)
        mirrored = imp.mirror_img(resized)
        # print(len(feature.hog(img, orientations=8, pixels_per_cell=(16, 16),
                        # cells_per_block=(1, 1))))
        print(i)
        # crop face and save it
        cv2.imwrite(path[:-4] + str(i) + '_.jpg', resized)
        cv2.imwrite(path[:-4] + str(i) + '__.jpg', mirrored)


def prep_data_hog(root, num_of_shifts=10, randomize=True, shift_values=None, crop_size=(150, 150)):
    dirs = os.listdir(root)
    # print(dirs)
    for dir in dirs:
        if os.path.isdir(root + '/' + dir):
            # print(os.listdir(root + '/' + dir))
            for fn in os.listdir(root + '/' + dir):
                path = root + '/' + dir + '/' + fn
                if os.path.isfile(path) and '_' not in fn:
                    propagate_images(path, num_of_shifts, randomize, shift_values, crop_size)