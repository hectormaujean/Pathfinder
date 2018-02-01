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
import extract_from_txt



# Convertit un fichier pdf en txt
def convert(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
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
    listeortho = open('liste_orthographe.txt', 'rb')
    # Récupération du contenu du fichier
    lignes = listeortho.readlines()
    correct_list=[]
    for element in x:
        # transforme la liste en string et corrige
        listToStr=','.join(element)
#        print("***PRINT TEST***listToStr:" , listToStr)
        if listToStr not in lignes:
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
    #print("poste sans faute:",correct_list)
    return correct_list


#####fonction qui permet de connaitre le sexe
def gender():
    #On defini le prenom via une RegEx qui prend le premier mot du CV
    defPrenom = re.findall('\A[a-zA-Z{Ë, Ï, Ö, Œ, ï, ö, é,œ,â, ë, ç, ô}]+ ',txt)
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


#telecharge les cv du serveur
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

        print("------ cv " + str(i) + "------")
        txt = convert('pdfminer/samples/cv' + str(i) + '.pdf')
        # met en miniscule
        # txt = txt.lower()
        # print(txt)
        file = open("cv.txt", "w")
        file.write(txt)

        # file.close()

        # Reouverture du fichier pour la recherche
        file  = open("cv.txt", "r")

        print("GENDER:")
        #gender = gender()
        print(gender())

        skills, formations = extract_from_txt.findBlocks(file)

        splitFormation1 = extract_from_txt.splitLine(formations)
        raw = extract_from_txt.cleanSplitLine(splitFormation1)
        diplomes = extract_from_txt.extractFormationDiplomes(raw)
        domaines = extract_from_txt.extractFormationDomaines(raw)
        ecoles = extract_from_txt.extractFormationEcoles(raw)

        file = open('cv.txt', 'r')
        experience = extract_from_txt.findBlock('EXPÉRIENCE(?s)(.*)[^a-zA-Z]FORMATION', file)
        splitExperience1 = extract_from_txt.splitLine2(experience)
        splitExperience2 = extract_from_txt.cleanSplitLine(splitExperience1)
        listExperienceTitle = extract_from_txt.extractExperienceTitle(splitExperience2)
        splitExperience4 = extract_from_txt.extractExperiencePlaceBrut(splitExperience2)
        extract_from_txt.splitLineEmp(splitExperience4)
        splitLineExpPlace, splitLineExpEmp = extract_from_txt.extractExperienceEmployer(splitExperience4)
        splitExperienceDateBrut = extract_from_txt.extractExperienceDateBrut(splitExperience2)
        splitExperienceDateDebut, splitExperienceDateDuree = extract_from_txt.extractExperienceDateDebutDuree(splitExperienceDateBrut)


        print ("diplome"+str(i)+"",diplomes)
        print("-----------------------")
        print("-----------------------")
        print("-----------------------")
        print("-----------------------")
        print("-----------------------")
        print("-----------------------")

        print ("domaine"+str(i)+"",domaines)
        print("-----------------------")
        print("-----------------------")
        print("-----------------------")
        print("-----------------------")
        print("-----------------------")

        print ("ecole"+str(i)+"",ecoles)
        print("-----------------------")
        print("-----------------------")
        print("-----------------------")
        print("-----------------------")
        print("-----------------------")

        print("experience"+str(i)+"",listExperienceTitle)
        print("-----------------------")
        print("-----------------------")
        print("-----------------------")
        print("-----------------------")

        print("lieu"+str(i)+"",splitLineExpPlace)
        print("-----------------------")
        print("-----------------------")
        print("-----------------------")
        print("-----------------------")

        print("entreprise"+str(i)+"",splitLineExpEmp)
        print("-----------------------")
        print("-----------------------")
        print("-----------------------")
        print("-----------------------")

        print("date debut"+str(i)+"",splitExperienceDateDebut)
        print("-----------------------")
        print("-----------------------")
        print("-----------------------")
        print("-----------------------")

        print("duree"+str(i)+"",splitExperienceDateDuree)
        print("-----------------------")
        print("-----------------------")
        print("-----------------------")
        print("-----------------------")

        print("competence"+str(i)+"",skills)

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




