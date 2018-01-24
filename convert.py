# coding: utf8
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
import xlsxwriter
import re


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

txt = convert('../pdfminer/samples/Nicolas-Buissart.pdf')
#print(txt)
file = open("cv.txt", "w")
file.write(txt)

file.close()

#Reouverture du fichier pour la recherche
file=open('cv.txt','r')

# on effectue la recherche du block
experience = re.findall('EXPÉRIENCE(?s)(.*)[^a-zA-Z]FORMATION', file.read())
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