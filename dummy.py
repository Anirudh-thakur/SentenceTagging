from collections import defaultdict
def get_ngram_features(words, i):
    result = []
    n = len(words)
    add = "prevbigram-"
    j = i-1
    if j < 0:
        add = add + '<s>'
    else:
        add = add+words[j]
    result.append(add)
    add = "nextbigram-"
    j = i+1
    if j >= n:
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
    k = j-1
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

words = ["the", "happy", "cat"]
i = 0
#print(get_ngram_features(words, i))


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
    for i in range(1,len(shape)):
        if shape[i]!=shape[i-1]:
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


#print(get_word_features("UTDallas"))


def get_features(words, i, prevtag):
    result = get_ngram_features(words, i)+get_word_features(words[i])
    result.append("tagbigram-"+prevtag)
    for i in range(len(result)):
        if "wordshape-" not in result[i]:
            result[i] = result[i].lower()
    return result


print(get_features(["UTDallas"], 0, "prevtag"))

corpus_features = []
corpus_features.append(get_features(
    ["UTDallas"], 0, "prevtag").append('nextskip-</s>'))
def remove_rare_features(corpus_features, threshold=5):
    featureDict = defaultdict(int)
    for sentences in corpus_features:
        for features in sentences:
            temp = features.split("-")
            print(temp[0])
            featureDict[temp[0]] += 1
    commonSet = set()
    rareSet = set()
    for features in featureDict.keys():
        if featureDict[features] < threshold:
            rareSet.add(features)
        else:
            commonSet.add(features)
    common_features = []
    for sentences in corpus_features:
        fList = []
        for features in sentences:
            temp = features.split("-")
            if temp[0] in commonSet:
                fList.append(features)
        common_features.append(fList)
    result = (corpus_features, common_features)
    return result


print(remove_rare_features(corpus_features,2))
