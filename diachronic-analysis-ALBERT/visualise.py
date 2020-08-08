import os
import numpy as np
import random

import plotly.graph_objs as go
import plotly.io as pio
import plotly.express as px

import matplotlib.pyplot as plt
import networkx as nx

from sklearn import preprocessing
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity
from clustering import compute_nearest_cluster


def colour_labels(labels):

    colours = ["aquamarine", "black", "blue", "blueviolet", "burlywood",
               "cadetblue", "chartreuse", "chocolate", "coral", "cornflowerblue",
               "cyan", "darkblue", "darkcyan", "darkgoldenrod", "darkgrey", "darkgreen",
               "darkkhaki", "darkolivegreen", "darkorchid", "darksalmon", "darkseagreen",
               "darkslategrey", "darkturquoise", "deeppink", "deepskyblue",
               "dimgrey", "dodgerblue", "forestgreen", "fuchsia",
               "gainsboro", "gold", "goldenrod", "grey",
               "green", "hotpink", "indianred", "indigo",
               "khaki", "lavender", "lavenderblush",
               "lemonchiffon", "lightblue", "lightcoral", "lightcyan",
               "lightgrey", "lightgreen", "lightsalmon", "lightseagreen",
               "lightskyblue", "lightsteelblue", "limegreen", "maroon",
               "mediumaquamarine", "mediumblue", "mediumorchid", "mediumpurple",
               "mediumseagreen", "mediumslateblue", "mediumturquoise", "mediumvioletred",
               "midnightblue", "mintcream", "mistyrose",
               "olive", "olivedrab", "orange", "orangered",
               "orchid", "palegoldenrod", "palegreen", "paleturquoise",
               "palevioletred", "peru", "pink",
               "plum", "powderblue", "purple", "red", "rosybrown",
               "royalblue", "rebeccapurple", "saddlebrown",
               "sandybrown", "seagreen", "sienna", "silver",
               "skyblue", "slateblue", "slategrey",
               "springgreen", "steelblue", "tan", "teal", "thistle", "tomato",
               "turquoise", "violet", "yellow", "yellowgreen"]

    label_colours = {}
    cluster_labels = []
    for genre in labels:
        for year in labels[genre]:
            for label in labels[genre][year]:

                if label not in cluster_labels:

                    cluster_labels.append(label)

    for label in cluster_labels:
        if label not in list(label_colours):

            label_colours[label] = random.choice(colours)
            colours.remove(label_colours[label])

    return label_colours


def stacked_bar_vis(labels, word, terms, path, label_colours, kmeans=False):    #, normalise=False):

    cluster_labels = []
    for genre in labels:

        print("\nProducing stacked bar chart for sense distribution over time of word (" + word + ") with terms (" + terms + ") for genre (" + genre + ")...")
        years = [year for year in labels[genre]]
        years.sort()
        if years != []:

            for year in labels[genre]:
                for label in labels[genre][year]:

                    if label not in cluster_labels:

                        cluster_labels.append(label)

            data = []
            for label in cluster_labels:

                label_freq = []
                for year in years:

                    label_freq.append(labels[genre][year][label])

#            if normalise:
#                label_freq = preprocessing.normalize(np.array([label_freq]), norm="l1", axis=0)
                if label_freq == []:

                    del label_colours[label]

                data.append(go.Bar(name=str(label), x=years, y=label_freq, marker=go.bar.Marker(color=label_colours[label])))

            fig = go.Figure(data=data)
            fig.update_layout(title="Word (" + word + ") with terms (" + terms + ") for genre (" + genre + ")",
                              yaxis=dict(tickmode="linear", tick0=0, dtick=10),
                              xaxis=dict(tickmode="linear", tick0=years[0], dtick=1),
                              font=dict(size=25),
                              autosize=False,
                              width=3840,
                              height=2160,
                              barmode="stack")

            output_path = path + "/stacked_bar_charts" + "/" + genre
            if not os.path.exists(output_path):
                os.makedirs(output_path)

            if kmeans:
                pio.write_image(fig, output_path + "/" + word + "_" + terms + "_kmeans.png")

            else:
                pio.write_image(fig, output_path + "/" + word + "_" + terms + ".png")

    return label_colours


def cluster_genre_dist(word, terms, labels, path, label_colours, kmeans=False):

    print("\nVisualising distribution over all genres of uses of word (" + word + ") with terms (" + terms + ")...")
    genres = [genre for genre in labels]
    cluster_labels = []
    for genre in labels:

        for year in labels[genre]:
            for label in labels[genre][year]:

                if label not in cluster_labels:

                    cluster_labels.append(label)

    data = []
    for label in cluster_labels:

        label_freq = []
        for genre in labels:

            label_genre_freq = 0
            for year in labels[genre]:

                label_genre_freq += labels[genre][year][label]

            label_freq.append(label_genre_freq)

        if label_freq == []:

            del label_colours[label]

        data.append(go.Bar(name=str(label), x=genres, y=label_freq, marker=go.bar.Marker(color=label_colours[label])))

    fig = go.Figure(data=data)
    fig.update_layout(title="Distribution over all genres of uses of word (" + word + ") with terms (" + terms + ")",
                      yaxis=dict(tickmode="linear", tick0=0, dtick=10),
                      xaxis=dict(tickmode="linear", tick0=genres[0], dtick=1),
                      font=dict(size=25),
                      autosize=False,
                      width=3840,
                      height=2160,
                      barmode="stack")

    output_path = path + "/stacked_bar_charts"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    if kmeans:
        pio.write_image(fig, output_path + "/" + word + "_" + terms + "_kmeans_cluster_genre_dist.png")

    else:
        pio.write_image(fig, output_path + "/" + word + "_" + terms + "_cluster_genre_dist.png")


def recursive_graph_vis(cluster_labels, centroids, embedding_labels, n, depth, upper_cossim, lower_cossim, path):

    output_path = path + "/graphs"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    print("\n\nFinding each cluster's neighbours...")
    neighbours = NearestNeighbors(n_neighbors=n+1, radius=1.0)
    neighbours.fit(centroids)
    print("\nNeighbours found.\n")

    #find centroid labels
    centroid_labels = {}
    for label in embedding_labels:
        for centroid in centroids:

            if centroid in embedding_labels[label]:

                centroid_labels[str(centroid)] = label


    #recursive dictionary
    for centroid in centroids:
        if centroid_labels[str(centroid)] in cluster_labels:

            print("Constructing graph for cluster: " + str(centroid_labels[str(centroid)]) + "...")
            rec_d = {}
            neighbour_indices = neighbours.kneighbors([centroid], n+1, return_distance=False)[0]
            node_centroids = []
            for index in neighbour_indices:
                node_centroids.append(centroids[index])

            rec_d["0"] = node_centroids
            for i in range(depth):
                if i > 0:

                    rec_d[str(i)] = []

            for key in rec_d:
                if key != "0":

                    prev_key = str(int(key) - 1)
                    for n_centroid in rec_d[prev_key]:

                        depth_indices = neighbours.kneighbors([n_centroid], n+1, return_distance=False)[0]
                        for index in depth_indices:

                            rec_d[key].append(centroids[index])

                    print("Completed recursion instance: " + key)

        #construct graph
            G = nx.Graph()
            neighbour_centroids = []
            for key in rec_d:
                for n_centroid in rec_d[key]:

                    neighbour_centroids.append(n_centroid)

            for n_centroid in neighbour_centroids:
                for next_centroid in neighbour_centroids:

                    cos_sim = cosine_similarity(np.array([n_centroid]), np.array([next_centroid]))[0][0]
                    G.add_edge(centroid_labels[str(n_centroid)], centroid_labels[str(next_centroid)], weight=cos_sim)
                    G.remove_edges_from(G.selfloop_edges())

        #visualise
            fig = plt.figure(figsize = (80, 60))

        #figure size
            plt.rcParams["figure.figsize"] = [80, 60]

            elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] >= upper_cossim]
            emed = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] < upper_cossim and d["weight"] > lower_cossim]
            esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] <= lower_cossim]
            query_node = [node for node in G.nodes() if node == centroid_labels[str(centroid)]]
            other_nodes = [node for node in G.nodes() if node != centroid_labels[str(centroid)]]

            pos = nx.spring_layout(G)

        #nodes
            nx.draw_networkx_nodes(G, pos, nodelist=query_node, cmap=plt.get_cmap("hsv"), node_color="lime", node_size = 12800)
            nx.draw_networkx_nodes(G, pos, nodelist=other_nodes, cmap=plt.get_cmap("hsv"), node_color="lime", node_size = 400)

        #edges
            nx.draw_networkx_edges(G, pos, edgelist=elarge, width=8, edge_color="lime" )
            nx.draw_networkx_edges(G, pos, edgelist=emed, width=5, alpha=0.08, edge_color="r" )
            nx.draw_networkx_edges(G, pos, edgelist=esmall, width=4, alpha=0, edge_color="lavender")

        #labels
            nx.draw_networkx_labels(G, pos, font_size=40)

        #titles
            plt.title("Neighbours for cluster: " + str(centroid_labels[str(centroid)]) + "\nn = " + str(n) + "\nrecursion depth = " + str(depth) + "\nupper cosine similarity threshold = " + str(upper_cossim) + "\nlower cosine similarity threshold = " + str(lower_cossim), fontsize=50 )

        #save
            fig.savefig(output_path + "/" +  str(centroid_labels[str(centroid)]) + "_graph.png", bbox_inches = 'tight')
