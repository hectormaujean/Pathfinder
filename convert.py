# coding: utf8

from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
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
import calcul_stat
import csv
import os

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


# *********************************** Convertit un fichier pdf en txt ************************
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


# *********************************** fonction qui corrige les fautes en francais ************************
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


# *********************************** fonction qui traduit les CVen francais et qui corrige. Il faut distinguer CV FR et CV EN ************************
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


# *********************************** fonction qui permet de connaitre le sexe ************************
def gender():
    gende=[]
    prenom = ""
    #On defini le prenom via une RegEx qui prend le premier mot du CV
    defPrenom = re.findall('\A[a-zA-Z{Ë, Ï, Ö, Œ, ï, ö, é,œ,â, ë, ç, ô, -}]+ ',txt)
    #On supprime l'espace
    for suppEsp in defPrenom:
        prenom = suppEsp.strip()
    #on defini le sexe a partir du prenom
    sexe = Genderize().get1(prenom)
    gende.append(sexe['gender'])
    return gende

  # ***********************************Functionn Writing  to CSV************************

def WriteDictToCSV(csv_file, csv_columns, Liste_CV):
    try:
        with open(csv_file, 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns, restval='NA')
            if i == 1: #on ecrit le nom des colonnes que 1x
                writer.writeheader()
            for data in Liste_CV:
                writer.writerow(data)
    except IOError as err:
        errno, strerror = err.args
        print("I/O error({0}): {1}".format(errno, strerror))
    return


csv_columns = ['ID','GENDER' , 'Poste 1', 'Entreprise 1', 'Duree 1', 'Poste 2', 'Entreprise 2', 'Duree 2',
               'Poste 3', 'Entreprise 3', 'Duree 3', 'Poste 4', 'Entreprise 4', 'Duree 4',
               'Poste 5', 'Entreprise 5', 'Duree 5', 'Poste 6', 'Entreprise 6', 'Duree 6',
               'Poste 7', 'Entreprise 7', 'Duree 7', 'Poste 8', 'Entreprise 8', 'Duree 8',
               'Poste 9', 'Entreprise 9', 'Duree 9','Poste 10', 'Entreprise 10', 'Duree 10',
                'Poste 11', 'Entreprise 11', 'Duree 11', 'Poste 12', 'Entreprise 12', 'Duree 12',
                'Poste 13', 'Entreprise 13', 'Duree 13','Poste 14', 'Entreprise 14', 'Duree 14',
               'Ecole 1', 'Diplome 1', 'Domaine 1', 'Ecole 2', 'Diplome 2', 'Domaine 2',
               'Ecole 3', 'Diplome 3', 'Domaine 3', 'Ecole 4', 'Diplome 4', 'Domaine 4',
               'Ecole 5', 'Diplome 5', 'Domaine 5',
               'Ecole 6', 'Diplome 6', 'Domaine 6',
               'Skill 1', 'Skill 2', 'Skill 3', 'Skill 4', 'Skill 5', 'Skill 6',
               'Skill 7', 'Skill 8',
               'Skill 9', 'Skill 10', 'Skill 11', 'Skill 12', 'Skill 13', 'Skill 14', 'Skill 15', 'Skill 16', 'Skill 17', 'Skill 18', 'Skill 19', 'Skill 20', 'Skill 21', 'Skill 22',
               'Skill 23', 'Skill 24', 'Skill 25','Skill 26', 'Skill 27', 'Skill 28','Skill 29', 'Skill 30', 'Skill 31','Skill 32', 'Skill 33', 'Skill 34','Skill 35', 'Skill 36', 'Skill 37']

currentPath = os.getcwd()
csv_file = currentPath + "/resultat.csv"


# *********************************** fonction pour rassembler x dictionnaires  ( a , b , c , d , e ) ************************

def merge_x_dicts(a,b,c,d,e):
    l = a.copy()   # start with l's keys and values
    l.update(b) # modifies l with b's keys and values
    m = l.copy()
    m.update(c)
    n = m.copy()
    n.update(d)
    o = n.copy()
    o.update(e)
    return o

# *********************************** fonction pour supprimer les accents ************************



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

        url = "https://pixis.co/projetcv/CV"+str(i)+".pdf"
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
        txt = convert('pdfminer/samples/CV'+str(i)+'.pdf')
        #txt = supprime_accent(txt1)
        
        # ouverture du fichier en mode ecriture
        file = open("cv.txt", "w")
        file.write(txt)

        # file.close()

        # ouverture du fichier pour la recherche en mode lecture
        file = open("cv.txt", "r")


        # Appels des fonctions regex
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
        print (splitExperience2)
        listExperienceTitle = extract_from_txt.extractExperienceTitle(splitExperience2)
        splitExperience4 = extract_from_txt.extractExperiencePlaceBrut(splitExperience2)
        extract_from_txt.splitLineEmp(splitExperience4)
        splitLineExpPlace, splitLineExpEmp = extract_from_txt.extractExperienceEmployer(splitExperience4)
        splitExperienceDateBrut = extract_from_txt.extractExperienceDateBrut(splitExperience2)
        splitExperienceDateDebut, splitExperienceDateDuree = extract_from_txt.extractExperienceDateDebutDuree(splitExperienceDateBrut)


        #print ("gender", gender())
        print ("diplome:"+str(i)+"",diplomes)
        print ("domaine:"+str(i)+"",domaines)
        print ("ecole:"+str(i)+"",ecoles)
        print("experience:"+str(i)+"",listExperienceTitle)
        print("entreprise:"+str(i)+"",splitLineExpEmp)
        print("duree:"+str(i)+"",splitExperienceDateDuree)
        print("competence:"+str(i)+"",skills)


        # ****************Dictionnaire: id *****************

        my_dict_id = {}
        id = []

        keys_id = ["ID"]
        id = [str(i)]
        my_dict_id.update(dict(zip(keys_id,id)))

        # ****************Dictionnaire: gender *****************
        my_dict_gender = {}
        gende = []

        keys_gender = ['GENDER']
        gende = gender()

        my_dict_gender.update(dict(zip(keys_gender, gende)))

        # ****************Dictionnaire:liste des experiences professionelles( intitulÈ du poste; nom de l'entrperie; durÈe)*********


        my_dict_Exp = {}
        Experience = []

        for k in range(0, (len(listExperienceTitle)), 1):
            try:
                keys_Exp = ["Poste " + str(k+1), "Entreprise " + str(k+1), "Duree " + str(k+1)]
                Experience = [listExperienceTitle[k], splitLineExpEmp[k], splitExperienceDateDuree[k]]
                my_dict_Exp.update(dict(zip(keys_Exp, Experience)))

            except KeyError as e:
                print ('I got a KeyError - reason "%s"' % str(e))


        # ****************Dictionnaire:liste des formations acadÈmique**************

        Formation = []
        my_dict_Formation = {}

        for k in range(0, len(diplomes), 1):
            try:
                # increment i+1 to get "ECOLE1" since we started from i in range 0
                keys_Formation = ["Ecole " + str(k + 1), "Diplome " + str(k + 1), "Domaine " + str(k + 1)]
                Formation = [ecoles[k], diplomes[k], domaines[k]]
                my_dict_Formation.update(dict(zip(keys_Formation, Formation)))

            except KeyError as e:
                print ('I got a KeyError - reason "%s"' % str(e))


        # *****************************Dictionnaire: Liste des CompÈtence*****************************

        skills_list = []
        my_dict_Skills = {}

        for k in range(0, (len(skills)), 1):
            try:
                # increment i+1 to get "ECOLE1" since we started from i in range 0
                keys_Skills = ["Skill " + str(k+1)]
                skills_list = [skills[k]]
                my_dict_Skills.update(dict(zip(keys_Skills, skills_list)))

            except KeyError as e:
                print ('I got a KeyError - reason "%s"' % str(e))


        # ************************************************** Liste_CV =[Liste_Experience,Liste_Formation]
        print("******Liste CV"+str(i)+"*******")

        my_dict = {}
        Liste_CV = []
        print("poste", my_dict_Exp)
        print("formation",my_dict_Formation)
        print("skills", my_dict_Skills)
        my_dict = merge_x_dicts(my_dict_id, my_dict_gender, my_dict_Exp, my_dict_Formation, my_dict_Skills)
        #my_dict = merge_x_dicts(my_dict_id, my_dict_Exp, my_dict_Formation, my_dict_Skills)
        Liste_CV.append(my_dict)
        print(Liste_CV)

        WriteDictToCSV(csv_file, csv_columns, Liste_CV)


        i += 1
        #os.remove('pdfminer/samples/CV"+str(i)+".pdf')

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


