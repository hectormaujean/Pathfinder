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

splitline2 = []

# Trouve le bloc (EXPÉRIENCE, FORMATION, COMPÉTENCES...)
def findBlock(regex, textFile):
    block = re.findall(regex, textFile.read())
    return block

# Split le bloc par ligne
def splitLine(block):
    splitline = ""
    for data in block:
        splitline = data.split("\n")
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


txt = convert('pdfminer/samples/Nicolas-Buissart.pdf')
# met en miniscule
#txt = txt.lower()
#print(txt)
file = open("cv.txt", "w")
file.write(txt)

file.close()

#Reouverture du fichier pour la recherche
file=open('cv.txt','r')

# Bloc EXPÉRIENCE
postesList = []

print('experience')

experience = findBlock('EXPÉRIENCE(?s)(.*)[^a-zA-Z]FORMATION', file)
splitExperience1 = splitLine(experience)
splitExperience2 = cleanSplitLine(splitExperience1)
postes = findElement('', splitExperience2, postesList)

# Bloc FORMATION
formationsList = []

print('formation')

formation = findBlock('FORMATION(?s)(.*)[^a-zA-Z]COMPÉTENCE', file)
splitFormation1 = splitLine(formation)
splitFormation2 = cleanSplitLine(splitFormation1)
#mettre la regex qui recupere l'element formation
formations = findElement('', splitFormation2, formationsList)

######fonction qui permet de connaitre le sexe
def gender():
    #On defini le prenom via une RegEx qui prend le premier mot du CV
    defPrenom = re.findall('\A[a-zA-Z{Ë, Ï, Ö, Œ, ï, ö, é,œ,â, ë}]+ ',txt)
    #On supprime l'espace
    for suppEsp in defPrenom:
        prenom = suppEsp.strip()
    #on defini le sexe a partir du prenom
    sexe = Genderize().get1(prenom)
    return sexe['gender']

print("gender", gender())


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

#teste avec une liste de mot en anglais et francais en attendant les RegEx
#liste_poste correspond à postes
liste_poste=[['engineeer'], ['matheatics'], ['caissiere']]


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
correct_postes=[]
for element in liste_poste:
    # transforme la liste en string et corrige
    listToStr=','.join(element)
    print("affiche le poste d'origine:" , listToStr)
    # on utilise le module translator
    translator = Translator()
    # on traduit en francais
    engToFr = translator.translate(listToStr, dest='fr')
    engToFr = engToFr.text
    print("translation", engToFr)
    #puis on corrige
    correct_poste = correctFR(engToFr)
    print("correct",correct_poste)
#transforme string en liste pour les dictionnaires
    correct_poste = correct_poste.split('\n')
    correct_postes.append(correct_poste)

print("resultat final: poste sans faute:",correct_postes)


workbook = xlsxwriter.Workbook('cv.xlsx')
worksheet = workbook.add_worksheet()
data = open('cv.txt','r')

#count lines
linelist = data.readlines()
count = len(linelist)
print count          #check lines

#make each line and print in excel
for n in range (0, count):
    line = linelist[n]
    line = line.decode('utf8')
    splitline = line.split("\n")
    worksheet.write_row(0, n, splitline)
    n += 1

workbook.close()