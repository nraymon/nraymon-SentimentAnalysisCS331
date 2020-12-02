from operator import attrgetter
import re
from math import log10
import time
import copy

punct = [".", ",", ":", ";", "!", "$", "^", "*", "(", ")", "[", "]", "{", "}", "-", "", "&", "1", "2", "3", "4", "5",
         "6", "7", "8", "9", "0", "%", "+", "/", "\\"]


# sets up the feature class the represent a word with a list of whether it is in a sentence - index corresponding to
# the sentence number - a boolean of inVocab is ensure there are no duplicate words, and attributes for the probability
# distribution table.
class Feature:
    def __init__(self, word, inSentence, inVocab):
        self.word = word
        self.inSentence = inSentence
        self.inVocab = inVocab
        self.falsefalse = 0
        self.falsetrue = 0
        self.truefalse = 0
        self.truetrue = 0


# sets up the class label class with a list of whether the sentence is positive or negative - index correspdoning to
# the sentence number - and two other attributes to keep track of the probability that sentence is positive or negative.
class Label:
    def __init__(self):
        self.word = "classlabel"
        self.reviewType = []
        self.probNegative = 0
        self.probPositive = 0


# This strips all the punctuation out of the sentences and only grabs with words with "'"s and words without any other
# punctuation specified in the punct list. All words with "'"s are then stripped of the "'" and put back into the set.
# It is then sorted alphabetically. The class label is also then generated along side the punctuation stripping.
def preprocess(name, label, label2):
    print("Processing", name)
    f = open(name, "r")
    lineList = f.readlines()
    f.close()

    vocab = []

    for line in lineList:
        a = line.split("\t")
        for i in punct:
            a[0] = a[0].replace(i, "")

        a[1] = a[1].strip()

        if name == "trainingSet.txt":
            label.reviewType.append(a[1])
        elif name == "testSet.txt":
            label2.reviewType.append(a[1])

        for b in a[0].split(" "):
            b = b.replace("'", "")
            if b == "":
                continue
            newFeat = Feature(b.lower(), [], False)

            if len(vocab) == 0:
                vocab.append(newFeat)

            for j in vocab:
                if j.word == newFeat.word:
                    newFeat.inVocab = True
                    break

            if not newFeat.inVocab:
                vocab.append(newFeat)

    vocab = sorted(vocab, key=attrgetter('word'))

    for line in lineList:
        for i in punct:
            line = line.replace(i, "")
    
        line = line.lower()
    
        for j in vocab:
            if re.search(r"\b" + j.word + r"\b", line) is not None:
                j.inSentence.append(1)
            else:
                j.inSentence.append(0)

    return vocab


# generates the output files based on the preprocessed data and formatted according to the assignment
def writeout(name):
    f = open(name, "w")
    if name == "preprocessed_train.txt":
        for i in trainVocab:
            f.write(i.word)
            f.write(", ")
        f.write("classlabel\n")
        sentenceCount = len(i.inSentence)
        for i in range(sentenceCount):
            for j in trainVocab:
                f.write(str(j.inSentence[i]))
                f.write("\t")
            f.write(trainCL.reviewType[i])
            f.write("\n")
    elif name == "preprocessed_test.txt":
        for i in testVocab:
            f.write(i.word)
            f.write(", ")
        f.write("classlabel\n")
        sentenceCount = len(i.inSentence)
        for i in range(sentenceCount):
            for j in testVocab:
                f.write(str(j.inSentence[i]))
                f.write("\t")
            f.write(testCL.reviewType[i])
            f.write("\n")
    f.close()


# generates prediction based on the training data using the inference Naive bayes' formula as well as UDP
def predict(name):
    print("Predicting", name)
    f = open(name, "r")
    lineList = f.readlines()
    f.close()

    predictions = []
    counter = 1
    for line in lineList:
        a = line.split("\t")

        for i in punct:
            a[0] = a[0].replace(i, "")

        a[0] = a[0].lower()
        a[0] = a[0].replace("'", "")

        clTrue = []
        clFalse = []
        for trainWord in trainVocab:
            if re.search(r"\b" + trainWord.word + r"\b", a[0]) is not None:
                clTrue.append(log10(trainWord.truetrue))
                clFalse.append(log10(trainWord.truefalse))
            else:
                clTrue.append(log10(trainWord.falsetrue))
                clFalse.append(log10(trainWord.falsefalse))

        resultTrue = log10(trainCL.probPositive) + sum(clTrue)
        resultFalse = log10(trainCL.probNegative) + sum(clFalse)

        if resultTrue > resultFalse:
            #print("prediction for sentence:", counter),
            # print("positive")
            # print(resultTrue, resultFalse)
            predictions.append('1')
        else:
            #print("prediction for sentence:", counter),
            # print("negative")
            # print(resultTrue,resultFalse)
            predictions.append('0')

        counter += 1

    f = open("results.txt", "a")

    if name == "testSet.txt":
        print("Accuracy on testSet:")
        right = 0
        for i in range(len(predictions)):
            if predictions[i] == testCL.reviewType[i]:
                right += 1
        acc = right / len(predictions)
        f.writelines("Accuracy on testSet: ")
        f.writelines(str(acc))
        f.writelines("\n")
        print(acc)

    elif name == "trainingSet.txt":
        right = 0
        for i in range(len(predictions)):
            if predictions[i] == trainCL.reviewType[i]:
                right += 1
        acc = right / len(predictions)
        f.writelines("Accuracy on trainingSet: ")
        f.writelines(str(acc))
        f.writelines("\n")
        print("Accuracy on trainingSet:")
        print(acc)


trainCL = Label()
testCL = Label()

trainVocab = preprocess("trainingSet.txt", trainCL, testCL)
testVocab = preprocess("testSet.txt", trainCL, testCL)

trainCL.probNegative = trainCL.reviewType.count("0") / len(trainCL.reviewType)  # P(CD = false)
trainCL.probPositive = trainCL.reviewType.count("1") / len(trainCL.reviewType)  # P(CD = true)

writeout("preprocessed_train.txt")
writeout("preprocessed_test.txt")

for i in trainVocab:
    for j in range(len(i.inSentence)):
        if i.inSentence[j] == 0 and trainCL.reviewType[j] == '0':
            i.falsefalse += 1
        elif i.inSentence[j] == 1 and trainCL.reviewType[j] == '0':	
            i.truefalse += 1
        elif i.inSentence[j] == 0 and trainCL.reviewType[j] == '1':
            i.falsetrue += 1
        elif i.inSentence[j] == 1 and trainCL.reviewType[j] == '1':
            i.truetrue += 1

for i in trainVocab:
    i.falsefalse = ((i.falsefalse + 1) / (trainCL.reviewType.count('0') + 2))
    i.falsetrue = ((i.falsetrue + 1) / (trainCL.reviewType.count('1') + 2))
    i.truefalse = ((i.truefalse + 1) / (trainCL.reviewType.count('0') + 2))
    i.truetrue = ((i.truetrue + 1) / (trainCL.reviewType.count('1') + 2))

predict("testSet.txt")
predict("trainingSet.txt")
