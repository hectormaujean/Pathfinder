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

txt = convert('pdfminer/samples/Nicolas-Buissart.pdf')
# met en miniscule
txt = txt.lower()
print(txt)
file = open("cv.txt", "w")
file.write(txt)

file.close()

#Reouverture du fichier pour la recherche
file=open('cv.txt','r')


#fonction qui permet de connaitre le sexe
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
experience = re.findall('expÉrience(?s)(.*)[^a-zA-Z]formation', file.read())
print(experience)

splitline = ""
splitline2 = []

#suppression des cases vides
for case in splitline:
    if case != '':
        splitline2.append(case)

postes = []
for line in splitline2:
    poste = re.findall('.+?(?=at )', line)
    print(poste)
    postes.append(poste)

for element in postes:
    print(element)



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