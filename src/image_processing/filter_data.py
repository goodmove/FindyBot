from sklearn.cluster import KMeans
import csv
import pandas
import numpy as np

MIN = 150

def filter_data(path):
    data = pandas.read_csv(path, header=None)
    X = data.copy().iloc[:, :-1]

    cluster = KMeans(n_clusters=3, precompute_distances=True, n_jobs=1, random_state=241)
    cluster.fit(X)

    labels = cluster.labels_
    unique, counts = np.unique(labels, return_counts=True)
    m = max(np.asarray((unique, counts)).T, key=lambda x: x[1])[0]
    inds = [i for i in range(X.shape[0]) if labels[i] == m]

    if len(inds) < MIN:
        return

    vectors = data.iloc[inds, :]
    with open('data_filtered.csv', 'a') as csvfile:
        for ind in range(len(vectors)):
            writer = csv.writer(csvfile, strict=True)
            v = vectors.iloc[ind, :].tolist()
            v[-1] = int(v[-1])
            writer.writerow(v)