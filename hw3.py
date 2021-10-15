import sys

import nltk
from nltk.corpus import brown
import numpy
from scipy.sparse import csr_matrix
from sklearn.linear_model import LogisticRegression
from collections import defaultdict
# Load the Brown corpus with Universal Dependencies tags
# proportion is a float
# Returns a tuple of lists (sents, tags)
def load_training_corpus(proportion=1.0):
    brown_sentences = brown.tagged_sents(tagset='universal')
    num_used = int(proportion * len(brown_sentences))

    corpus_sents, corpus_tags = [None] * num_used, [None] * num_used
    for i in range(num_used):
        corpus_sents[i], corpus_tags[i] = zip(*brown_sentences[i])
    return (corpus_sents, corpus_tags)


# Generate word n-gram features
# words is a list of strings
# i is an int
# Returns a list of strings
def get_ngram_features(words, i):
    result = []
    n = len(words)
    add = "prevbigram-"
    j = i-1
    if j<0:
        add = add + '<s>'
    else:
        add = add+words[j]
    result.append(add)
    add = "nextbigram-"
    j = i+1
    if j>=n:
        add = add+"</s>"
    else:
        add = add+words[j]
    result.append(add)
    add = "prevskip-"
    j = i-2
    if j < 0:
        add = add+"<s>"
    else:
        add = add+words[j]
    result.append(add)
    add = "nextskip-"
    j = i+2
    if j >= n:
        add = add+"</s>"
    else:
        add = add+words[j]
    result.append(add)
    add = "prevtrigram-"
    j = i-1
    k= j-1
    if j < 0:
        add = add+"<s>-"
    else:
        add = add+words[j]+"-"
    if k < 0:
        add = add+"<s>"
    else:
        add = add+words[k]
    result.append(add)
    add = "nexttrigram-"
    j = i+1
    k = j+1
    if j >= n:
        add = add+"</s>"+"-"
    else:
        add = add+words[j]+"-"
    if k >= n:
        add = add+"</s>"
    else:
        add = add+words[k]
    result.append(add)
    add = "centertrigram-"
    j = i-1
    k = i+1
    if j < 0:
        add = add+"<s>"+"-"
    else:
        add = add+words[j]+"-"
    if k >= n:
        add = add+"</s>"
    else:
        add = add+words[k]
    result.append(add)
    return result
    


# Generate word-based features
# word is a string
# returns a list of strings
def get_word_features(word):
    result = []
    result.append("word-"+word)
    if word[:1].isupper():
        result.append("capital")
    if word.isupper():
        result.append("allcaps")
    shape = ""
    for letter in word:
        if letter.isdigit():
            shape = shape+"d"
        elif letter.isalpha():
            if letter.isupper():
                shape = shape+"X"
            else:
                shape = shape+"x"
        else:
            shape += letter
    result.append("wordshape-"+shape)
    shortShape = shape[0]
    for i in range(1, len(shape)):
        if shape[i] != shape[i-1]:
            shortShape += shape[i]

    result.append("short-wordshape-"+shortShape)
    if 'd' in shortShape:
        result.append("number")
    if '-' in word:
        result.append('hyphen')
    for i in range(1, 5):
        if i <= len(word):
            result.append("prefix"+str(i)+"-"+word[:i])
        else:
            break
    for i in range(1, 5):
        if len(word)-i >= 0:
            result.append("suffix"+str(i)+"-"+word[-i:])
        else:
            break
    return result


# Wrapper function for get_ngram_features and get_word_features
# words is a list of strings
# i is an int
# prevtag is a string
# Returns a list of strings
def get_features(words, i, prevtag):
    result = get_ngram_features(words, i)+get_word_features(words[i])
    result.append("tagbigram-"+prevtag)
    for i in range(len(result)):
        if "wordshape-" not in result[i]:
            result[i] = result[i].lower()
    return result




# Remove features that occur fewer than a given threshold number of time
# corpus_features is a list of lists, where each sublist corresponds to a sentence and has elements that are lists of strings (feature names)
# threshold is an int
# Returns a tuple (corpus_features, common_features)
def remove_rare_features(corpus_features, threshold=5):
    featureDict = defaultdict(int)
    for i in range(len(corpus_features)):
        for j in range(len(corpus_features[i])):
            FeatureList = corpus_features[i][j]
            for features in FeatureList:
                featureDict[features] += 1
    commonSet = set()
    rareSet = set()
    for features in featureDict.keys():
        if featureDict[features] < threshold:
            rareSet.add(features)
        else:
            commonSet.add(features)
    #print(commonSet)

    for i in range(len(corpus_features)):
        for j in range(len(corpus_features[i])):
            FeatureList = corpus_features[i][j]
            newFeatureList = []
            for features in FeatureList:
                if features in commonSet:
                    newFeatureList.append(features)
            corpus_features[i][j] = newFeatureList
    result = (corpus_features, commonSet)
    return result



# Build feature and tag dictionaries
# common_features is a set of strings
# corpus_tags is a list of lists of strings (tags)
# Returns a tuple (feature_dict, tag_dict)
def get_feature_and_label_dictionaries(common_features, corpus_tags):
    feature_dict = dict()
    tag_dict = dict()
    counterTag = 0
    for i in range(len(corpus_tags)):
        for j in range(len(corpus_tags[i])):
            tag = corpus_tags[i][j]
            if tag not in tag_dict.keys():
                tag_dict[tag] = counterTag
                counterTag += 1
    counterFeature = 0
    for features in common_features:
        if features not in feature_dict.keys():
            feature_dict[features] = counterFeature
            counterFeature += 1
    result = (feature_dict,tag_dict)
    return result

# Build the label vector Y
# corpus_tags is a list of lists of strings (tags)
# tag_dict is a dictionary {string: int}
# Returns a Numpy array
def build_Y(corpus_tags, tag_dict):
    temp = []
    for i in range(len(corpus_tags)):
        for j in range(len(corpus_tags[i])):
            tag = corpus_tags[i][j]
            index = tag_dict[tag]
            temp.append(index)
    result = numpy.array(temp)
    return result

# Build a sparse input matrix X
# corpus_features is a list of lists, where each sublist corresponds to a sentence and has elements that are lists of strings (feature names)
# feature_dict is a dictionary {string: int}
# Returns a Scipy.sparse csr_matrix
def build_X(corpus_features, feature_dict):
    rows = []
    cols = []
    for sentences in corpus_features:
        for i,words in enumerate(sentences):
            for feature in words:
                rows.append(i)
                cols.append(feature_dict[feature])

    values = [1 for _ in range(len(rows))]
    r = numpy.array(rows)
    c = numpy.array(cols)
    v = numpy.array(values)
    result = csr_matrix((v,r,c))
    return result



# Train an MEMM tagger on the Brown corpus
# proportion is a float
# Returns a tuple (model, feature_dict, tag_dict)
def train(proportion=1.0):
    (corpus_sents, corpus_tags) = load_training_corpus(proportion)
    #print(corpus_tags[0]])
    print(corpus_sents[0])
    corpus_features = []
    for i,sentence in enumerate(corpus_sents):
        f_list = []
        for j,word in enumerate(sentence):
            if j == 0:
                f_list.append(get_features(word, j, "<s>"))
            else:
                print(corpus_tags[i][j-1])
                
                f_list.append(get_features(sentence, j, corpus_tags[i][j-1]))
        corpus_features.append(f_list)
    (corpus_features, commonSet) = remove_rare_features(corpus_features)
    (feature_dict, tag_dict) = get_feature_and_label_dictionaries(
        commonSet, corpus_tags)
    X = build_X(corpus_features,feature_dict)
    Y = build_Y(corpus_tags,tag_dict)
    print(X.shape)
    print(Y.shape)
    model = LogisticRegression(class_weight='balanced' , solver='saga',multi_class='multinomial')
    model.fit(X,Y)
    return (model,feature_dict,tag_dict)

    



# Load the test set
# corpus_path is a string
# Returns a list of lists of strings (words)
def load_test_corpus(corpus_path):
    with open(corpus_path) as inf:
        lines = [line.strip().split() for line in inf]
    return [line for line in lines if len(line) > 0]


# Predict tags for a test sentence
# test_sent is a list containing a single list of strings
# model is a trained LogisticRegression
# feature_dict is a dictionary {string: int}
# reverse_tag_dict is a dictionary {int: string}
# Returns a tuple (Y_start, Y_pred)
def get_predictions(test_sent, model, feature_dict, reverse_tag_dict):
    pass


# Perform Viterbi decoding using predicted log probabilities
# Y_start is a Numpy array of size (1, T)
# Y_pred is a Numpy array of size (n-1, T, T)
# Returns a list of strings (tags)
def viterbi(Y_start, Y_pred):
    pass


# Predict tags for a test corpus using a trained model
# corpus_path is a string
# model is a trained LogisticRegression
# feature_dict is a dictionary {string: int}
# tag_dict is a dictionary {string: int}
# Returns a list of lists of strings (tags)
def predict(corpus_path, model, feature_dict, tag_dict):
    pass


def main(args):
    model, feature_dict, tag_dict = train(0.25)

    predictions = predict('test.txt', model, feature_dict, tag_dict)
    for test_sent in predictions:
        print(test_sent)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
