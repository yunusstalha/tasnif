import logging

import numpy as np
from img2vec_pytorch import Img2Vec
from rich.logging import RichHandler
from scipy.cluster.vq import kmeans2
from sklearn.decomposition import PCA

# Configure logging
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(
    level="INFO", format=LOG_FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)


def get_embeddings(use_gpu=False, images=None):
    """
    This Python function initializes an Img2Vec object, runs it on either GPU or CPU, and retrieves
    image embeddings.
    """

    logging.info(f"Img2Vec is running on {'GPU' if use_gpu else 'CPU'}...")
    img2vec = Img2Vec(cuda=use_gpu)

    embeddings = img2vec.get_vec(images, tensor=False)
    return embeddings


def calculate_pca(embeddings, pca_dim):
    """
    The function `calculate_pca` takes embeddings and a desired PCA dimension as input, performs PCA
    transformation, and returns the transformed embeddings.

    :param embeddings: The `embeddings` parameter is a NumPy array containing the data points to be used
    for PCA. Each row in the array represents a data point, and the columns represent the features of
    that data point
    :param pca_dim: The `pca_dim` parameter in the `calculate_pca` function represents the desired
    dimensionality of the PCA (Principal Component Analysis) transformation. It specifies the number of
    principal components to retain after the dimensionality reduction process
    :return: The function `calculate_pca` returns the embeddings transformed using PCA with the
    specified dimensionality reduction (`pca_dim`).
    """

    n_samples, _ = embeddings.shape
    if n_samples < pca_dim:
        n_components = min(n_samples, pca_dim)
        logging.info(
            f"Number of samples is less than the desired dimension. Setting n_components to {n_components}"
        )

    else:
        n_components = pca_dim

    pca = PCA(n_components=n_components)
    pca_embeddings = pca.fit_transform(embeddings.squeeze())
    logging.info("PCA calculated.")
    return pca_embeddings


def calculate_kmeans(pca_embeddings, num_classes):
    """
    The function `calculate_kmeans` performs KMeans clustering on PCA embeddings data to assign
    labels and centroids.
    """

    if not isinstance(pca_embeddings, np.ndarray):
        raise ValueError("pca_embeddings must be a numpy array")

    if num_classes > len(pca_embeddings):
        raise ValueError(
            "num_classes must be less than or equal to the number of samples in pca_embeddings"
        )

    try:
        centroid, labels = kmeans2(data=pca_embeddings, k=num_classes, minit="points")
        counts = np.bincount(labels)
        logging.info("KMeans calculated.")
        return centroid, labels, counts

    except Exception as e:
        raise RuntimeError(f"An error occurred during KMeans processing: {e}")
