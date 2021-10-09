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
print(get_ngram_features(words, i))
