import pandas as pd
from difflib import SequenceMatcher


# DETECT ecole
def detectEcole(case, ecole):
    isecole = False
    for i in range(44, 62, 3):
        if (ecole in case[i]):
            isecole = True
            break
    return isecole


# DETECT poste
def detectPoste(case, poste):
    isposte = False
    for i in range(2, 32, 3):
        if (poste in case[i]):
            isposte = True
            break
    return isposte


# Extraire postes
def ExtractPostesWithEcole(tuples, ecole):
    listePostes = []
    for case in tuples:
        if (detectEcole(case, ecole)):
            for i in range(2, 32, 3):
                if case[i] != "empty":
                    listePostes.append((case[i]))
    return listePostes


# Extraire ecoles
def extractEcolesWithPoste(tuples, poste):
    listeEcoles = []
    for case in tuples:
        if (detectPoste(case, poste)):
            for i in range(44, 62, 3):
                if case[i] != "empty":
                    listeEcoles.append((case[i]))
    return listeEcoles


# Extraire skills
def extraireSkills(tuples):
    listeSkills = []
    for case in tuples:
        for i in range(62, 75, 1):
            if case[i] != "empty":
                listeSkills.append(case[i])
    return listeSkills


# similar strings
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


# GET unique list from list (HOMOGENE)
def getCleanList(listfirst, param):
    listSimilar = []
    copyList = list(listfirst)
    for i in range(0, len(listfirst), 1):
        s = i + 1
        for j in range(s, len(listfirst), 1):
            if (similar(listfirst[i], listfirst[j]) > param) and (listfirst[i] in copyList):
                copyList.remove(listfirst[i])

    return copyList


# STAT
def getStat(liste, cleanList, param):
    statList = []
    for case in cleanList:
        i = 0
        for casetwo in liste:
            if (similar(case, casetwo) > param):
                i = i + 1
        statList.append([case, i])
    total = 0
    for case in statList:
        total = total + case[1]
    dataStat = pd.DataFrame(statList)
    dataStat = dataStat.sort_values(by=[1], ascending=False)
    return dataStat, total





















