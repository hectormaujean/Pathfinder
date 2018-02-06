# coding: utf8


from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import xlsxwriter
import re
from datetime import datetime


# Split le bloc par ligne (commun)
def splitLine(block):
    splitline = block.split("\n")
    return splitline


# Supprimme les cases vides (commun)
def cleanSplitLine(splitLine):
    liste = []
    for case in splitLine:
        if case != '':
            liste.append(case)
    return liste


#################   FONCTIONS POUR LE BLOC FORMATION (HECTOR)  #######################

# Trouve un element (hector)
def findElement(regex, splitList, tab):
    for line in splitList:
        element = re.findall(regex, line)
        tab.append(element)
    return tab


# Extrait les formations
def extractFormationDiplomes(splitline):
    listDiplome = []
    for i in range(0, len(splitline), 3):
        element = re.findall('.*(?= en )', splitline[i])
        if not element:
            element = splitline[i]
            element = element.lower().split('\n')
        for i in range(0, len(element), 1):
            if element[i] == '':
                element = filter(None, element)
        listDiplome.append(''.join(element))
    return listDiplome


# Extrait les domaines de formation
def extractFormationDomaines(splitline):
    listFormationDomaines = []
    for i in range(0, len(splitline), 3):
        element = re.findall('(?<= en ).*', splitline[i])
        if not element:
            element = 'NA'
        listFormationDomaines.append(''.join(element))
    return listFormationDomaines


# Extrait les ecoles
def extractFormationEcoles(splitline):
    listFormationEcole = []
    for i in range(1, len(splitline), 3):
        if not splitline[i]:
            splitline[i] = 'NA'
        listFormationEcole.append(splitline[i])
    return listFormationEcole


################   FONCTIONS POUR LE BLOC COMPETENCES ET INFO COMPLEMENTAIRE  (MYRVETE)  #################

# Verifie si un mot est contenu dans le fichier (myrvete)
def check(word):
    datafile = open('cv.txt', 'r')
    for line in datafile:
        if word in line:
            return True
    return False


# Vérifie si le mot dans la liste est en minuscule (myrvete)
def isLowerCase(words):
    for word in words:
        if word.isupper():
            return False
        else:
            return True


def findBlocks(file):
    skills = []
    # Genere la regex pour trouver les blocs (EXPERIENCE, FORMATION, COMPETENCES...)
    regex = "EXPÉRIENCE(?s)(.*)[^a-zA-Z]FORMATION(?s)(.*)[^a-zA-Z]"

    # S'il y a un bloc COMPETENCE et un bloc INFORMATIONS COMPLÉMENTAIRES
    if (check('COMPÉTENCE')):
        regex = regex + 'COMPÉTENCE(?s)(.*)'
        # S'il y a un bloc INFORMATIONS COMPLÉMENTAIRES
        if (check('INFORMATIONS COMPLÉMENTAIRES')):
            regex = regex + '[^a-zA-Z]INFORMATIONS COMPLÉMENTAIRES(?s)(.*)'

    # S'il y a un bloc INFORMATIONS COMPLÉMENTAIRES et pas de bloc COMPETENCE
    if (check('INFORMATIONS COMPLÉMENTAIRES') and check('COMPÉTENCE') == False):
        regex = regex + '[^a-zA-Z]INFORMATIONS COMPLÉMENTAIRES(?s)(.*)'

    # Teste la présence des blocs
    compInfos = False
    comp = False
    infoCompl = False

    if ('COMPÉTENCE' in regex and 'INFORMATIONS COMPLÉMENTAIRES' not in regex):
        comp = True

    elif ('COMPÉTENCE' in regex and 'INFORMATIONS COMPLÉMENTAIRES' in regex):
        compInfos = True

    elif ('INFORMATIONS COMPLÉMENTAIRES' in regex and 'COMPÉTENCE' not in regex):
        infoCompl = True

    # Récupère les blocs
    blocksList = re.findall(regex, file.read())

    for block in blocksList:
        experiences = block[0]
        formations = block[1]
        # S'il y a les blocs COMPÉTENCE et INFORMATIONS COMPLÉMENTAIRES
        if (compInfos):
            if (block[2] is not None):
                competences = block[2]
            if (block[3] is not None):
                infosCompl = block[3]

        # S'il y a un bloc COMPÉTENCE et pas de bloc INFORMATIONS COMPLÉMENTAIRES
        elif (comp):
            if (block[2] is not None):
                competences = block[2]

        # S'il y a un bloc INFORMATIONS COMPLÉMENTAIRES et pas de bloc COMPÉTENCE
        elif (infoCompl):
            if (block[2] is not None):
                infosCompl = block[2]

        # Bloc COMPÉTENCE ***Myrvete***

        # S'il y a un bloc COMPÉTENCE
        if (compInfos or comp):
            if (competences != ""):

                # On vérifie si le bloc contient le nom d'un autre bloc
                blockName = re.findall(
                    'LIENS|PUBLICATIONS|SERVICE MILITAIRE|DISTINCTIONS|CERTIFICATS|GROUPES|BREVETS',
                    competences)

                if (len(blockName) > 0):
                    # Suppression des blocs indesirables
                    competences = re.sub(blockName[0] + '(?s).*', '', competences)

                # On supprime tout ce qui est entre parenthèses (duree de formation...)
                cleanSkills = re.sub(r'\([^)]*\)', '', competences)

                # On récupère les compétences qui sont entre les virgules
                skills = cleanSkills.split(",")
                skillsNewList = []
                # Supprime les '\n' de la derniere case
                for skill in skills:
                    cleanSkill = re.sub('\n', '', skill)
                    # Supprime les espaces blancs avant et après la chaine
                    skillStripped = cleanSkill.strip()
                    skillsNewList.append(skillStripped)
                skills = skillsNewList
        else:
            skills = ["NA"]
    return skills, formations


################  FONCTIONS POUR LE BLOC EXPERIENCE (SAFOUEN)  #######################

# Trouve un bloc (EXPÉRIENCE)
def findBlock(regex, textFile):
    blockexp = re.findall(regex, textFile.read())
    return blockexp


# Split le bloc par ligne
def splitLine2(blockexp):
    splitline = ""
    for data in blockexp:
        splitline = data.split("\n\n")
    return splitline


# Trouve un mois dans un chaine et le converti en nombre (Safouen)
def monthToNumberOne(string):
    numberone = 0
    list = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre",
            "décembre"]
    for i in range(0, len(list), 1):
        if (list[i] ==
                re.findall(r"(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)?",
                           string)[0]):
            numberone = list.index(list[i]) + 1

    return numberone


def monthToNumberTwo(string):
    numbertwo = 0
    list = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre",
            "décembre"]
    for i in range(0, len(list), 1):
        if (list[i] ==
                re.findall(r"(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)?",
                           string)[9]):
            numbertwo = list.index(list[i]) + 1

    return numbertwo


# Extraire les expériences
def extractExperienceTitle(splitline):
    listExperienceTitle = []
    for i in range(0, len(splitline), 4):
        listExperienceTitle.append(splitline[i])
    return listExperienceTitle


def extractExperiencePlaceBrut(splitline):
    list = []
    for i in range(1, len(splitline), 4):
        list.append(splitline[i])
    return list


def extractExperienceDateBrut(splitline):
    list = []
    for i in range(2, len(splitline), 4):
        list.append(splitline[i])
    return list


def extractExperienceDateDebutDuree(splitline):
    listDateDebut = []
    listDuree = []
    for case in splitline:
        if re.findall(
                r"(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)?[ ]?[0-9]{4}[ ][-][ ](actuellement)[ ]?",
                case):
            listDateDebut.append(re.findall(r"[0-9]{4}", case)[0])
            listDuree.append(((datetime.now().year * 12) + datetime.now().month) - (
                    (int(re.findall(r"[0-9]{4}", case)[0]) * 12) + monthToNumberOne(case)) + 1)
        elif re.findall(
                r"(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)?[ ]?[0-9]{4}[ ][-][ ](janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)?[ ]?[0-9]{4}",
                case):
            listDateDebut.append(re.findall(r"[0-9]{4}", case)[0])
            listDuree.append(((((int(re.findall(r"[0-9]{4}", case)[1])) * 12) + monthToNumberTwo(case)) - (
                    (int(re.findall(r"[0-9]{4}", case)[0])) * 12) - monthToNumberOne(case)) + 1)
        elif re.findall(r"([0-9]{4})", case):
            listDateDebut.append(re.findall(r"([0-9]{4})", case)[0])
            listDuree.append("NA")
        else:
            listDateDebut.append("NA")
            listDuree.append("NA")
    return listDateDebut, listDuree


def splitLineEmp(splitline):
    for case in splitline:
        splitline[splitline.index(case)] = case.split(" - ")
    return splitline


def extractExperienceEmployer(splitline):
    listEmployer = []
    listPlaceExp = []
    for casetab in splitline:
        if (len(casetab) == 2):
            if (casetab[0] == ""):
                listEmployer.append("NA")
            else:
                listEmployer.append(casetab[0])

            if (casetab[1] == ""):
                listPlaceExp.append("NA")
            else:
                listPlaceExp.append(casetab[1])
        elif (len(casetab) == 1):
            if (re.findall(r"(, )", casetab[0])) or (re.findall(r"([0-9])", casetab[0])):
                if (re.findall(r"(, )", casetab[0])):
                    listPlaceExp.append(casetab[0])
                    listEmployer.append("NA")
                if (re.findall(r"([0-9])", casetab[0])):
                    listPlaceExp.append(casetab[0])
                    listEmployer.append("NA")
            else:
                listEmployer.append(casetab[0])
                listPlaceExp.append("NA")
    return listPlaceExp, listEmployer
