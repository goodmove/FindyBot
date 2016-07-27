from src.image_processing.impros_conf import CONFIG
from sklearn.cross_validation import KFold
from sklearn.externals import joblib
from sklearn import grid_search
from sklearn.svm import SVC
import numpy as np
import pandas

def train_svm(data_path, clf_path):
    data = pandas.read_csv(data_path, header=None)
    y = data.iloc[:, -1]
    X = data.iloc[:, :-1];

    clf = SVC(kernel='rbf', random_state=241, C=10.0, gamma=0.125, decision_function_shape='ovr')
    clf.fit(X, y)
    joblib.dump(clf, clf_path)

def cross_validation(X, y, grid, descr):
    print('Tuning hyper-parameters with {0} kernel'.format(grid['kernel'][0]))

    cv = KFold(y.size, n_folds=5, shuffle=True, random_state=241)
    gs = grid_search.GridSearchCV(SVC(random_state=241, decision_function_shape='ovr'), grid, scoring='accuracy', cv=cv, verbose=3)
    gs.fit(X, y)

    print('Model training is finished.\n')
    print('Best params: {0}. Best score: {1}'.format(gs.best_params_, gs.best_score_))
    print(gs.get_params(deep=True))
    print('')
    joblib.dump(gs, 'src/image_processing/ML/{0}/clfs/{1}/svm_hog_clf.pkl'.format(descr, grid['kernel'][0]))

def train_daisy(grids):
    data_face = pandas.read_csv(CONFIG['data']['daisy_features_face_path'], header=None)
    data_le = pandas.read_csv(CONFIG['data']['daisy_features_le_path'], header=None)
    data_re = pandas.read_csv(CONFIG['data']['daisy_features_re_path'], header=None)
    data_nose = pandas.read_csv(CONFIG['data']['daisy_features_nose_path'], header=None)

    X = pandas.concat([data_face.iloc[:, :-1], data_le.iloc[:, :-1], data_re.iloc[:, :-1], data_nose.iloc[:, :-1]], axis=1)
    y = data_face.iloc[:, -1]
    y = [int(x) for x in y.tolist()]
    print(data_face.shape, data_le.shape, data_re.shape, data_nose.shape)

    for grid in grids:
        cross_validation(X, y, grid, 'daisy')

def train_hog(grids):
    data = pandas.read_csv(CONFIG['data']['hog_data_path'], header=None)
    X = data.iloc[:, :-1]
    y = data.iloc[:, -1]

    for grid in grids:
        cross_validation(X, y, grid, 'hog')


grid1 = {
    'kernel': ['linear'],
    'C': np.power(10.0, np.arange(-5, 6))
}
grid2 = {
    'kernel': ['rbf'],
    'gamma': np.power(2.0, np.arange(-10, 3)),
    'C': np.power(10.0, np.arange(-2, 6))
}

train_hog([grid2])