from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.externals import joblib
from sklearn.cluster import KMeans
import numpy as np
import pandas
import csv


def build_features(suffix, clusters, n_descr):
    data = pandas.read_csv('daisy/data_daisy_'+suffix+'.csv', header=None)
    X = data.copy().iloc[:, :-1]

    print(data.shape)
    # return;

    cluster = KMeans(n_clusters=clusters, precompute_distances=True, n_jobs=1, random_state=241)
    cluster.fit(X)

    joblib.dump(cluster, './clfs/cluster/kmeans_'+suffix+'.pkl')

    counts = [ [0]*clusters for x in range(data.shape[0]//n_descr) ]
    labels = cluster.labels_
    # create a word for each image
    for ind in range(data.shape[0]):
        counts[ind//n_descr][labels[ind]]+=1

    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(counts)
    joblib.dump(tfidf, './clfs/cluster/kmeans_'+suffix+'_tfidf.pkl')
    f_vectors = tfidf.toarray()

    with open('daisy/daisy_features_'+suffix+'.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, strict=True)
        for ind in range(f_vectors.shape[0]):
            writer.writerow(np.append(f_vectors[ind, :], [int(data.iloc[ind*n_descr, -1])]))

build_features('face', 128, 169)
build_features('le', 128, 64)
build_features('re', 128, 64)
build_features('nose', 128, 20)