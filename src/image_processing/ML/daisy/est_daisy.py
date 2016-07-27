from sklearn.cross_validation import KFold
from sklearn.externals import joblib
from sklearn import grid_search
from sklearn.svm import SVC
import numpy as np
import pandas

data_face = pandas.read_csv("daisy/daisy_features_face.csv", header=None)
data_le = pandas.read_csv("daisy/daisy_features_le.csv", header=None)
data_re = pandas.read_csv("daisy/daisy_features_re.csv", header=None)
data_nose = pandas.read_csv("daisy/daisy_features_nose.csv", header=None)

X = pandas.concat([data_face.iloc[:, :-1], data_le.iloc[:, :-1], data_re.iloc[:, :-1], data_nose.iloc[:, :-1]], axis=1)
y = data_face.iloc[:, -1]


print(data_face.shape, data_le.shape, data_re.shape, data_nose.shape)
print(X.shape)
y = [int(x) for x in y.tolist()]
print(y)

def train(grid, X, y):
    print('Tuning hyper-parameters with {0} kernel'.format(grid['kernel'][0]))

    cv = KFold(len(y), n_folds=5, shuffle=True, random_state=241)
    gs = grid_search.GridSearchCV(SVC(random_state=241, decision_function_shape='ovr'), grid, scoring='accuracy', cv=cv, verbose=3)
    gs.fit(X, y)

    print('Model training is finished.\n')
    print('Best params: {0}. Best score: {1}'.format(gs.best_params_, gs.best_score_))
    print(gs.get_params(deep=True))
    print('')
    joblib.dump(gs, './clfs/daisy/{0}/svm_daisy_clf.pkl'.format(grid['kernel'][0]))

grid1 = {
    'kernel': ['linear'],
    'C': np.power(10.0, np.arange(-5, 6))
}
grid2 = {
    'kernel': ['rbf'],
    # 'gamma': np.power(2.0, np.arange(-4, 5)),
    # 'C': np.power(10.0, np.arange(0, 6))
    'gamma': np.power(2.0, np.arange(-10, 3)),
    'C': np.power(10.0, np.arange(-2, 6))
}
# train(grid1, X, y)
# train(grid2, X, y)