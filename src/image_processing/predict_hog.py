from src.image_processing.impros import ImageProcessor as impros
from src.image_processing.clf_constants import CONSTANTS
from sklearn.externals import joblib
from skimage import feature
import cv2

def get_face(path, shift_values=None, resize_values=CONSTANTS['resize_values']):
    img = cv2.imread(path, 0)
    if img is None:
        print('Couldn\'t open img. Path: ', path)
        return [];

    res = impros.detect_face_ext(bounds=shift_values, img=img)

    if len(res) == 0:
        print('No faces found')
        return []

    x,y,w,h,dx,dy = res
    return impros.resize_img(img[y:y+h, x:x+w], resize_values)

def compute_hog(img):
    return feature.hog(
                    img,
                    orientations=CONSTANTS['orientations'],
                    pixels_per_cell=CONSTANTS['pixels_per_cell'],
                    cells_per_block=CONSTANTS['cells_per_block'],
                    transform_sqrt=CONSTANTS['transform_sqrt']
                    )

def predict_hog(path):
    """
        given an image, makes predictions on user_id using HOG features extractor
    """
    svm_hog_clf = joblib.load(CONSTANTS['svm_hog_clf_path'])
    face_img = get_face(path)
    if len(face_img) == 0:
        return {
            'response': 'failure',
            'data': None
        }
    hog_feature = compute_hog(face_img)
    id = -1;
    try:
        id = svm_hog_clf.predict(hog_feature.reshape(1,-1))
    except:
        print('Error while extracting HOG feature vector')
        return {
            'response': 'failure',
            'data': None
        }
    return {
        'response': 'success',
        'data': id
    }