import pickle

from visualise import recursive_graph_vis

with open("pickled-centroids", "rb") as f:
    centroids = pickle.load(f)

with open("pickled-embedding_labels", "rb") as f:
    embedding_labels = pickle.load(f)


cluster_labels = [27, 33, 32]
n = 3
depth = 3
upper_cossim = 0.9
lower_cossim = 0.3
path = "/home/ayan-yue/Documents/projects/diachronic-analysis-ALBERT"

recursive_graph_vis(cluster_labels, centroids, embedding_labels, n, depth, upper_cossim, lower_cossim, path)
