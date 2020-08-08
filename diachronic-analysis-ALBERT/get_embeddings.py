import os
import torch
import pickle
import numpy as np

from transformers import AlbertTokenizer, AlbertForMaskedLM, AlbertConfig
from collections import OrderedDict


def load_model(path, genre):

    print('\nLoading genre model: ' + genre)
    config = AlbertConfig.from_json_file(path + '/models' + '/' + genre + '/config.json')
    model = AlbertForMaskedLM.from_pretrained('albert-base-v2', config=config)
    state_dict_path = (path + '/models' + '/' + genre + '/pytorch_model.bin')
    model.load_state_dict(torch.load(state_dict_path))
    tokenizer = AlbertTokenizer.from_pretrained(path + '/models' + '/' + genre)

    return model, tokenizer


def retrieve_sentences_with_terms(word, terms, genre, corpus):

    if len(terms.split()) > 1:

        sentences = []
        for sentence in corpus[genre]:
            if all(x in sentence for x in terms.split()) and word in sentence:

                sentences.append(sentence)

    else:

        sentences = [sentence for sentence in corpus[genre] if terms in sentence and word in sentence]

    return sentences


def load_corpus(path):

    with open(path + '/pickled-d', 'rb') as f:

        d = pickle.load(f)

    return d


    #AddMoreClusters code
def get_embedding_for_sentence(tokenized_sent, genre, model, tokenizer):

    #print("Getting embedding for sentence")
    indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_sent)
    tokens_tensor = torch.tensor([indexed_tokens])
    segments_ids = [1] * len(tokenized_sent)
    segments_tensors = torch.tensor([segments_ids])

    with torch.no_grad():

        _ , encoded_layers = model(tokens_tensor, segments_tensors)
        batch_i = 0
        token_embeddings = []

        # For each token in the sentence...
        for token_i in range(len(tokenized_sent)):

            hidden_layers = []

            # For each of the 12 layers...
            for layer_i in range(len(encoded_layers)):

                # Lookup the vector for `token_i` in `layer_i`
                vec = encoded_layers[layer_i][batch_i][token_i]
                hidden_layers.append(vec)

            token_embeddings.append(hidden_layers
                                   )
        concatenated_last_4_layers = [torch.cat((layer[-1], layer[-2], layer[-3], layer[-4]), 0) for layer in token_embeddings]
        summed_last_4_layers = [torch.sum(torch.stack(layer)[-4:], 0) for layer in token_embeddings]
        last_layer = [layer[-1] for layer in token_embeddings]

        return summed_last_4_layers


    #provides a word embedding for every occurrence of the word
def get_embeddings_for_word(word, sentences, genre, model, tokenizer):

    word_embeddings = []
    valid_sentences = []
    for i, sentence in enumerate(sentences):

            marked_sent = "[CLS] " + sentence + " [SEP]"
            tokenized_sent = tokenizer.tokenize(marked_sent)
            tokenized_word = tokenizer.tokenize(word)[0]

            if tokenized_word in tokenized_sent and len(tokenized_sent) < 512 and len(tokenized_sent) > 3:

                sent_embedding = get_embedding_for_sentence(tokenized_sent, genre, model, tokenizer)
                word_indexes = list(np.where(np.array(tokenized_sent) == tokenized_word)[0])

                for index in word_indexes:

                    word_embedding = np.array(sent_embedding[index])
                    word_embeddings.append(word_embedding)
                    valid_sentences.append(sentence)


    word_embeddings = np.array(word_embeddings)
    valid_sentences = np.array(valid_sentences)

    return word_embeddings, valid_sentences


def get_embeddings(word, terms, genre, corpus, model, tokenizer):

    print("\nGetting ALBERT embeddings for word:", word)

    d = {}
    sentences = retrieve_sentences_with_terms(word, terms, genre, corpus)
    for sentence in sentences:

        marked_sent = "[CLS] " + sentence + " [SEP]"
        tokenized_sent = tokenizer.tokenize(marked_sent)

        if tokenizer.tokenize(word)[0] in tokenized_sent and len(tokenized_sent) < 512 and len(tokenized_sent) > 3:

            d[sentence], valid_sentence = get_embeddings_for_word(word, [sentence], genre, model, tokenizer)

    embeddings = []
    for sentence in d:
        for embedding in d[sentence]:

                embeddings.append(embedding)

    embeddings = np.array(embeddings)

    return d, embeddings
