# from scipy.cluster.vq import kmeans2
from sklearn.cluster import KMeans
CLUSTERS_SIZE = 2


# a = [
#     [185.0, 1535.0],
#     [252.0, 1534.0],
#     [368.0, 1534.0],
#     [524.0, 1541.0],
# ]
def perform_kmeans_clustering(data):
    kmeans = KMeans(n_clusters=2)
    kmeans = kmeans.fit(data)
    labels = kmeans.predict(data)
    # centroid, labels = kmeans2(data, CLUSTERS_SIZE)
    return labels
