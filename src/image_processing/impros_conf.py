CONFIG = {
    'haar_conf': {
        'face_clf': 'src/image_processing/haar_clfs/haarcascade_frontalface_alt.xml',
        'face_clf1': 'src/image_processing/haar_clfs/haarcascade_frontalface_default.xml',
        'eye_clf': 'src/image_processing/haar_clfs/eyes1.xml',
        'eye_clf1': 'src/image_processing/haar_clfs/haarcascade_eye.xml',
        'mouth_clf': 'src/image_processing/haar_clfs/mouth.xml'
    },
    'hog_conf': {
        'resize_values': (150, 150),
        'num_of_shifts': 10,
        'shift_values': None,
        'orientations': 8,
        'pixels_per_cell': (16, 16),
        'cells_per_block': (1, 1),
        'transform_sqrt': False
    },
    'daisy_conf': {
        'face_size': (150, 150),
        'le_size': (96, 96),
        're_size': (96, 96),
        'nose_size': (64, 56)
    },
    'clf_svm': {
        'svm_hog_clf_path': 'src/image_processing/clfs/rbf/svm_hog_clf.pkl'
    },
    'data': {
        'hog_data_path': './image_processing/data/hog/data_hog.csv',
        'daisy_data_face_path': './image_processing/data/daisy/data_daisy_face.csv',
        'daisy_data_le_path': './image_processing/data/daisy/data_daisy_le.csv',
        'daisy_data_re_path': './image_processing/data/daisy/data_daisy_re.csv',
        'daisy_data_nose_path': './image_processing/data/daisy/data_daisy_nose.csv'
    }
}