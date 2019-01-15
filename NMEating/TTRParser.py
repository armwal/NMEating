import os
import subprocess
import re
from re import sub
from decimal import Decimal
from PIL import Image
from scipy import misc
import numpy as np
import datetime

def process_file(filePath, outFolder):
    horlines,jmps = find_outline(filePath)
    tess = r'c:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
    image = Image.open(filePath)
    meals = []
    for day in range(5):
        for option in range(4):
            lines = process_sub_image(image, tess, outFolder, filePath, day, horlines[option], horlines[option+1], jmps)
            parsed, parsedcost = parse_lines(lines)
            parsed = sub('[\d\)]','',parsed).strip()
            if option == 0:
                soup = parsed
            elif option == 1:
                meal = parsed
                mealcost = parse_cost(parsedcost)
            elif option == 2:
                veg = parsed
                vegcost = parse_cost(parsedcost)
            else:
                dessert = parsed       
        meals = meals + [tuple([soup, meal, mealcost, veg, vegcost, dessert])]
    date = parse_date(filePath)
    return meals,date

def parse_date(filePath):
    match = re.match('.*KW(\d\d(-\d)?).png', filePath)
    parsed = match.groups(0)[0]
    year = 2018
    if '-' in parsed:
        year += int(parsed[-1])
    week = parsed[0:2]
    return datetime.datetime.strptime('{} {} 1'.format(year,week),'%Y %W %w')

def parse_cost(cost):
    if len(cost) == 0 or cost == '?':
        return cost
    return Decimal(sub(',','.',sub(r'[^\d.]', '', cost)))

def process_sub_image(image, tess, outFolder, filePath, day, top, bottom, jmps):
    fileName = os.path.basename(filePath)
    baseFileName,ext = fileName.split('.')
    left = jmps[day]
    width = jmps[day+1] - jmps[day]
    cropped = image.crop((left, top, left+width, bottom))
    outfilename = outFolder + baseFileName + '_' + str(day) + '.' + ext
    cropped.save(outfilename)
    tessname = outFolder + baseFileName + '_' + str(day)
    subprocess.run([tess, outfilename, tessname, '-l', 'deu'])
    f = open(tessname + '.txt', encoding='utf8')
    lines = f.readlines()
    f.close()
    os.remove(outfilename)
    os.remove(tessname + '.txt')
    return list([l.strip() for l in lines])
    
def parse_lines(lines):
    i = 0
    while len(lines[i]) == 0:
        i += 1
    meal = ''
    while sum(c.isdigit() for c in lines[i]) < 2 or len(lines[i]) > 6:
        meal += ' ' + lines[i]
        i += 1
        if i == len(lines):
            return meal, '?'
    if any(char.isdigit() for char in lines[i]):
        mealcost = lines[i]
        if '.' in mealcost:
            mealcost = mealcost.replace('.',',')
        elif ',' not in mealcost:
            mealcost = mealcost[0] + ',' + mealcost[1:]
        i += 1
    else:
        mealcost = '?'
    return meal, mealcost

def find_outline(filePath):
    im = misc.imread(filePath)
    im = np.sum(im,2)
    ver = np.sum(im,1)
    thresh = 3*150*im.shape[1]
    horlines = np.where(ver < thresh)[0]
    topline = im[horlines[0],:]
    zeros = np.where(topline < 10)[0]
    dz = np.diff(zeros)
    jmps = [zeros[0]] + np.ndarray.tolist(zeros[np.where(dz > 1)[0]]) + [im.shape[1]]
    return horlines, jmps

