# coding: utf8

from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
import xlsxwriter
import re
from genderize import Genderize
import enchant
from enchant.checker import SpellChecker
from googletrans import Translator
import urllib2
from urllib2 import Request
from pyPdf import PdfFileWriter, PdfFileReader
from StringIO import StringIO




# Convertit un fichier pdf en txt
def convert(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text



######fonction qui corrige les fautes en francais
def correctFR(text):
 my_dict = enchant.DictWithPWL("fr_FR", 'liste_orthographe.txt')
 chkr = enchant.checker.SpellChecker(my_dict)
 b = chkr.set_text(text)
 for err in chkr:
    # print ('erreur:', err.word)
     if not (err.suggest(b) == [] ):
         sug = err.suggest()[0]
   #      print ('suggestion:', sug)
         err.replace(sug)
 c = chkr.get_text()  # retourne le texte corrige
 return c



######fonction qui traduit les CVen francais et qui corrige. Il faut distinguer CV FR et CV EN
def correction(x):
    mot_non_traduit=['master']
    correct_list=[]
    for element in x:
        # transforme la liste en string et corrige
        listToStr=','.join(element)
#        print("***PRINT TEST***listToStr:" , listToStr)
        if listToStr not in mot_non_traduit:
            # on utilise le module translator
            translator = Translator()
            # on traduit en francais
            engToFr = translator.translate(listToStr, dest='fr')
            engToFr = engToFr.text
#            print("***PRINT TEST***translation", engToFr)
            # puis on corrige
            correct_poste = correctFR(engToFr)
#            print("***PRINT TEST***correct", correct_poste)
        else:
            # corrige
            correct_poste = correctFR(listToStr)
#            print("***PRINT TEST***correct",correct_poste)
    #transforme string en liste pour les dictionnaires
    #    correct_poste = correct_poste.split('\n')
        correct_list.append(correct_poste)
    print("poste sans faute:",correct_list)
    return correct_list


splitline2 = []

# Trouve le bloc (EXPÉRIENCE, FORMATION, COMPÉTENCES...)
def findBlock(regex, textFile):
    block = re.findall(regex, textFile.read())
    return block

# Split le bloc par ligne
def splitLine(block):
    splitline = ""
    for data in block:
        splitline = data.split("\n\n")
    return splitline

# Supprimme les cases vides
def cleanSplitLine(splitLine):
    for case in splitLine:
        if case != '':
            splitline2.append(case)
    return splitline2

# Trouve un element dans une ligne
def findElement(regex, splitList, tab):
    for line in splitList:
        element = re.findall(regex, line)
        tab.append(element)
    return tab

#Trouve un élément dans une ligne: si l'élément n'est pas trouvé, récupère la ligne entière
def findElementLine(regex, modulo, lineNumber, splitList, tab):
    count = 0
    for line in splitList:
        element = re.findall(regex, line)
        if not element:
            if count%modulo == lineNumber:
                tab.append(splitList[count])
        else:
            tab.append(element[0])
        count += 1
    return tab

def cleanWhiteSpace(tab):
    tab = filter(None, tab)
    length = len(tab)
    for i in range(length):
        tab[i] = filter(None, tab[i])
    return tab

#####fonction qui permet de connaitre le sexe
def gender():
    #On defini le prenom via une RegEx qui prend le premier mot du CV
    defPrenom = re.findall('\A[a-zA-Z{Ë, Ï, Ö, Œ, ï, ö, é,œ,â, ë}]+ ',txt)
    #On supprime l'espace
    for suppEsp in defPrenom:
        prenom = suppEsp.strip()
    #on defini le sexe a partir du prenom
    sexe = Genderize().get1(prenom)
    return sexe['gender']



#Ouverture du fichier où on stock la variable en mode lecture
path = open('output_variable.txt','rb')
#Récupération du contenu du fichier
lignes = path.readlines()
#on convertie le contenu (str) en int et on le declare dans i
for variable in lignes:
    #print variable
    i=int(variable)

b = True



while(b):
    try:
        url = "https://pixis.co/projetcv/A"+str(i)+".pdf"
        writer = PdfFileWriter()
        remoteFile = urllib2.urlopen(Request(url)).read()
        memoryFile = StringIO(remoteFile)
        pdfFile = PdfFileReader(memoryFile)

        for pageNum in xrange(pdfFile.getNumPages()):
            currentPage = pdfFile.getPage(pageNum)
            writer.addPage(currentPage)
            outputStream = open("pdfminer/samples/CV"+str(i)+".pdf","wb")
            writer.write(outputStream)
            outputStream.close()

        i += 1

    except urllib2.HTTPError as err:
        if err.code == 404:
            print("No more files")
            b = False
        else:
                raise

print('i',i)
#Ouverture du fichier où on stock la variable en mode écriture
f = open('output_variable.txt', 'w')
#on ecrit la nouvelle variable en str
f.write(str(i))
f.close()






txt = convert('pdfminer/samples/Imene-Meghoufel.pdf')
# met en miniscule
#txt = txt.lower()
#print(txt)
file = open("cv.txt", "w")
file.write(txt)

file.close()

#Reouverture du fichier pour la recherche
file=open('cv.txt','r')


print("GENDER:")
gender = gender()
print(gender)

# Bloc EXPÉRIENCE
postesList = []

print('experience')

#experience = findBlock('EXPÉRIENCE(?s)(.*)[^a-zA-Z]FORMATION', file)
#splitExperience1 = splitLine(experience)
#splitExperience2 = cleanSplitLine(splitExperience1)
#postes = findElement('', splitExperience2, postesList)

# Bloc FORMATION
formationsList = []

print('BLOC FORMATION')

formation = findBlock('FORMATION(?s)(.*)[^a-zA-Z]COMPÉTENCE', file)
splitFormation1 = splitLine(formation)
splitFormation2 = cleanSplitLine(splitFormation1)


#DIPLOMES
diplomes_list = []
diplomes = findElementLine('.*(?= en )', 3, 0, splitFormation2, formationsList)
diplomes = cleanWhiteSpace(diplomes)
for element in diplomes:
    strToList = element.lower().split('\n')
    diplomes_list.append(strToList)
print('diplomes: ', diplomes_list)
diplomes_list = correction(diplomes_list)
formationsList = []

#DOMAINES
domaines_list=[]
domaines = findElement('(?<= en ).*', splitFormation2, formationsList)
domaines = cleanWhiteSpace(domaines)
for element in domaines:
    #on convertis la liste en str pour pouvoir mettre en minuscule
    listToStr = ','.join(element)
    #puis on remet dans une liste
    strToList = listToStr.lower().split('\n')
    domaines_list.append(strToList)
print('domaines: ', domaines_list)
domaines_list = correction(domaines_list)
formationsList = []


#ECOLES
ecoles_list=[]
months = "janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre"
ecoles = findElementLine('(?!['+months+' \d]).*(?= -)', 3, 1, splitFormation2, formationsList)
ecoles = cleanWhiteSpace(ecoles)
for element in ecoles:
    strToList = element.lower()
    ecoles_list.append(strToList)
print('ecole: ', ecoles_list)
formationsList = []


#LIEUX (no need atm)
#lieux = findElement('(?<= - ).*', splitFormation2, formationsList)
#lieux = cleanWhiteSpace(lieux)
#print('lieux: ', lieux)
#formationsList = []




# on effectue la recherche du block
#experience = findBlock('expÉrience(?s)(.*)[^a-zA-Z]formation', file)
#print("exp", experience)

#splitline = ""
#splitline2 = []

#suppression des cases vides
#for case in splitline:
#    if case != '':
#        splitline2.append(case)

#postes = []
#for line in splitline2:
#    poste = re.findall('.+?(?=at )', line)
#    print(poste)
#    postes.append(poste)

#for element in postes:
#    print(element)


