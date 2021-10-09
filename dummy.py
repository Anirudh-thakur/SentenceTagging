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
        else:
            if letter.isupper():
                shape = shape+"X"
            else:
                shape = shape+"x"
    result.append("wordshape-"+shape)
    shortShape = ""
    visited = []
    for let in shape:
        if let not in visited:
            shortShape += let
            visited.append(let)
    result.append("short-wordshape-"+shortShape)
    if 'd' in visited:
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


print(get_word_features("UTDallas"))
