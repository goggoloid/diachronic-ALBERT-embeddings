import numpy as np
import os
import pickle

from get_embeddings import load_corpus, load_model, get_embeddings
from clustering import cluster_word_embeddings_aff_prop, compute_nearest_cluster
from get_metadata import get_years_files
from visualise import stacked_bar_vis, cluster_genre_dist, colour_labels

from collections import Counter


    #SETTINGS
path = "/home/ayan-yue/Documents/projects/diachronic-analysis-ALBERT"
word = "resilience"
terms = ""
target_genre = "all_genres"

    #preprocessing settings used for fine-tuning
disk = "/home/ayan-yue"
genres_dir = "/Documents/projects/genres"
genres_path = disk + genres_dir
max_char = 512
min_char = 25
patterns = ['[^A-Za-z0-9"''-£,()%./:; #]+']
kmeans_threshold = 60
k = 60


    #LOAD MODELS, GET EMBEDDINGS, CLUSTER & SAVE RESULTS:
corpus = load_corpus(path)
model, tokenizer = load_model(path, target_genre)

d, embeddings = get_embeddings(word, terms, target_genre, corpus, model, tokenizer)

print("\nClustering embeddings using affinity propagation...")
cluster_labels, centroids, counts = cluster_word_embeddings_aff_prop(embeddings)
if len(counts) > kmeans_threshold:
    print("\nToo many clusters, using k-means where k = " + k + "..." )
    cluster_labels, centroids = cluster_word_embeddings_k_means(word_embeddings, k=k)

with open("pickled-centroids", "wb") as f:
    pickle.dump(centroids, f)


    #{sentence: centroid}
#senses = {}
#for sentence in d:

#    senses[sentence] = [embedding for embedding in d[sentence] if embedding in centroids]
#    if senses[sentence] == []:

#        del senses[sentence]


    #{cluster label: [embeddings]}?????????????????????????????????????????????????????????
embedding_labels = {}
for label in list(set(cluster_labels)):

    embedding_labels[label] = np.array([embeddings[i] for i, _ in enumerate(cluster_labels) if cluster_labels[i] == label])

with open("pickled-embedding_labels", "wb") as f:
    pickle.dump(embedding_labels, f)


    #{sentence: cluster label}
sentence_labels = {}
for sentence in d:
    for embedding in d[sentence]:

        for label in embedding_labels:
            for labelled_embedding in embedding_labels[label]:

                if (labelled_embedding == embedding).all():

                    sentence_labels[sentence] = label


    #date all labelled sentences
print("\nRetrieving sentences, years and files...")

sentences = [sentence for sentence in sentence_labels]
year_d, file_d = get_years_files(sentences, target_genre, genres_path, max_char, min_char, patterns)


    #{cluster label: sentence}
clusters = {}
for sentence in sentences:
    clusters[sentence_labels[sentence]] = []

for label in clusters:
    clusters[label] = [sentence for sentence in sentences if sentence_labels[sentence] == label]


    #{genre: {year: Counter([cluster labels])}}
print("\nFinding distribution of labels per genre per year...")
labels = {}
for year in year_d:
    for _, genre in year_d[year]:

        labels[genre] = {}

for genre in labels:
    for year in year_d:

        year_sentences = [sentence for sentence, genre in year_d[year]]
        labels[genre][year] = [sentence_labels[sentence] for sentence in sentences if sentence in corpus[genre] and sentence in year_sentences]


for genre in labels:

    labels[genre] = {year: Counter(label_list) for year, label_list in labels[genre].items() if label_list != []}

with open("pickled-labels", "wb") as f:
    pickle.dump(labels, f)


    #results
output_path = path + "/clusters"
if not os.path.exists(output_path):
    os.makedirs(output_path)

f = open(output_path + "/" + word + "_" + terms + "_word_use_clusters.txt", "w")
f.write("Clusters for word (" + word + ") with terms (" + terms + "):")

for label in clusters:
    print("\n")
    print("\nCluster: " + str(label))

    f.write("\n")
    f.write("\n\nCluster: " + str(label))

    index = 0
    for sentence in sentence_labels:
        if sentence_labels[sentence] == label:

            index += 1
            print("\n" + sentence)
            print(file_d[sentence])
            print(index)

            f.write("\n\n" + sentence)
            f.write("\n" + file_d[sentence])
            f.write("\n" + str(index))

for genre in labels:
    print("\n")
    print(genre)
    for year in labels[genre]:
        print(year)
        print(labels[genre][year])

count = []
for label in clusters:
    for sentence in clusters[label]:
        count.append(sentence)

print("\nNumber of sentences found: " + str(len(count)))


    #visualise results with stacked bar charts
label_colours = colour_labels(labels)

if len(counts) > kmeans_threshold:

    stacked_bar_vis(labels, word, terms, path, label_colours, kmeans=True)
    cluster_genre_dist(word, terms, labels, path, label_colours, kmeans=True)

else:

    stacked_bar_vis(labels, word, terms, path, label_colours)
    cluster_genre_dist(word, terms, labels, path, label_colours)
