from operator import attrgetter
import re
from math import log10
from math import prod
import time
import copy


class Feature:
    def __init__(self, word, inSentence, inVocab):
        self.word = word
        self.inSentence = inSentence
        self.inVocab = inVocab
        self.probNegative = 0
        self.probPositive = 0
        self.falsefalse = 0
        self.falsetrue = 0
        self.truefalse = 0
        self.truetrue = 0

class Label:
    word = "classlabel"
    reviewType = []
    probNegative = 0
    probPositive = 0


punct = [".", ",", ":", ";", "!", "$", "^", "*", "(", ")", "[", "]", "{", "}", "-", "", "&", "1", "2", "3", "4", "5",
         "6", "7", "8", "9", "0", "%", "+", "/", "\\"]

cl = Label()
sentenceList = []


def preprocess(s):

    f = open(s)
    lineList = f.readlines()

    count = 0
    vocab = []

    for line in lineList:
        a = line.split("\t")
        for i in punct:
            a[0] = a[0].replace(i, "")

        a[1] = a[1].strip()

        cl.reviewType.append(a[1])

        for b in a[0].split(" "):
            b = b.replace("'", "")
            if b == "":
                continue
            newFeat = Feature(b.lower(), [], False)

            if len(vocab) == 0:
                vocab.append(newFeat)

            for j in vocab:
                if j.word == newFeat.word:
                    if a[1] == "1":
                        j.probPositive += 1
                    if a[1] == "0":
                        j.probNegative += 1
                    newFeat.inVocab = True
                    break

            if not newFeat.inVocab:
                if a[1] == "1":
                    newFeat.probPositive += 1
                if a[1] == "0":
                    newFeat.probNegative += 1
                vocab.append(newFeat)

    vocab = sorted(vocab, key=attrgetter('word'))

    print("Finding whether a word is in a sentence... This may take some time.")

    for y in lineList:
        for i in punct:
            y = y.replace(i, "")
    
        y = y.lower()
    
        for j in vocab:
            if re.search(r"\b" + j.word + r"\b", y) is not None:
                j.inSentence.append(1)
            else:
                j.inSentence.append(0)

    f.close()

    return vocab


vocab = preprocess("trainingSet.txt")

m = len(vocab)
print("Vocab Length:", m)

cl.probNegative = cl.reviewType.count("0") / len(cl.reviewType)
cl.probPositive = cl.reviewType.count("1") / len(cl.reviewType)

print("negative:", cl.probNegative)
print("positive:", cl.probPositive)

for i in vocab:
    totalAppearance = i.probNegative + i.probPositive
    i.probNegative = i.probNegative / totalAppearance
    i.probPositive = i.probPositive / totalAppearance
    print("Negative P:", i.probNegative)
    print("Positive P:", i.probPositive)

f = open("preprocessed_train.txt", "w")

for i in vocab:
    f.write(i.word)
    f.write(", ")
    for j in i.inSentence:
        f.write(str(j))
        f.write(", ")
    f.write("\n")

f.close()

for i in vocab:
    for j in range(len(i.inSentence)):
        if i.inSentence[j] == 0 and cl.reviewType[j] == '0':
            i.falsefalse += 1
        if i.inSentence[j] == 1 and cl.reviewType[j] == '0':
            i.truefalse += 1
        if i.inSentence[j] == 0 and cl.reviewType[j] == '1':
            i.falsetrue += 1
        if i.inSentence[j] == 1 and cl.reviewType[j] == '1':
            i.truetrue += 1

for i in vocab:
    i.falsefalse = ((i.falsefalse + 1) / (cl.reviewType.count('0') + 2))
    i.falsetrue = ((i.falsetrue + 1) / (cl.reviewType.count('1') + 2))
    i.truefalse = ((i.truefalse + 1) / (cl.reviewType.count('0') + 2))
    i.truetrue = ((i.truetrue + 1) / (cl.reviewType.count('1') + 2))

f = open("testSet.txt", "r")

lineList = f.readlines()
counter = 1

for line in lineList:
    a = line.split("\t")

    for i in punct:
        a[0] = a[0].replace(i, "")

    a[0] = a[0].lower()
    a[0] = a[0].replace("'", "")

    clTrue = []
    clFalse = []
    for trainWord in vocab:
        if re.search(r"\b" + trainWord.word + r"\b", a[0]) is not None:
            clTrue.append(log10(trainWord.truetrue))
            clFalse.append(log10(trainWord.truefalse))
        else:
            clTrue.append(log10(trainWord.falsetrue))
            clFalse.append(log10(trainWord.falsefalse))

    resultTrue = log10(cl.probPositive) + sum(clTrue)
    resultFalse = log10(cl.probNegative) + sum(clFalse)

    if resultTrue > resultFalse:
        print("prediction for sentence:", counter),
        print("positive")
    else:
        print("prediction for sentence:", counter),
        print("negative")

    counter += 1
