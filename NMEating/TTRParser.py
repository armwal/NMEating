import os
import subprocess
import re
from re import sub
from decimal import Decimal
from PIL import Image

def process_file(filePath, outFolder):
    tess = r'c:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
    image = Image.open(filePath)
    meals = []
    for day in range(5):
        lines = process_sub_image(image, tess, outFolder, filePath, day)
        soup, meal, mealcost, veg, vegcost, dessert = parse_lines(lines)
        mealcost = parse_cost(mealcost)
        vegcost = parse_cost(vegcost)
        meals = meals + [tuple([soup, meal, mealcost, veg, vegcost, dessert])]
    return meals

def parse_cost(cost):
    if len(cost) == 0 or cost == '?':
        return cost
    return Decimal(sub(',','.',sub(r'[^\d.]', '', cost)))

def process_sub_image(image, tess, outFolder, filePath, day):
    fileName = os.path.basename(filePath)
    baseFileName,ext = fileName.split('.')
    width = 210
    left = 154 + day*width
    top = 233
    bottom = 650
    cropped = image.crop((left, top, left+width, bottom))
    outfilename = outFolder + baseFileName + '_' + str(day) + '.' + ext
    cropped.save(outfilename)
    tessname = outFolder + baseFileName + '_' + str(day)
    subprocess.run([tess, outfilename, tessname, '-l', 'deu'])
    f = open(tessname + '.txt', encoding='utf8')
    lines = f.readlines()
    f.close()
    #os.remove(outfilename)
    #os.remove(tessname + '.txt')
    return list([l.strip() for l in lines])
    
def parse_lines(lines):
    print(lines)
    i = 0
    while len(lines[i]) == 0:
        i += 1
    soup = ''
    while len(lines[i]) > 0:
        soup += ' ' + lines[i]
        i += 1
    while len(lines[i]) == 0:
        i += 1
    meal = ''
    while len(lines[i]) > 0:
        meal += ' ' + lines[i]
        i += 1
    while len(lines[i]) == 0:
        i += 1
    if any(char.isdigit() for char in lines[i]):
        mealcost = lines[i]
        if '.' in mealcost:
            mealcost = mealcost.replace('.',',')
        elif ',' not in mealcost:
            mealcost = mealcost[0] + ',' + mealcost[1:]
        i += 1
        while len(lines[i]) == 0:
            i += 1
        veg = ''
    else:
        mealcost = '?'
        veg = lines[i]
        i += 1
    while len(lines[i]) > 0:
        veg += ' ' + lines[i]
        i += 1
    while len(lines[i]) == 0:
        i += 1
    if any(char.isdigit() for char in lines[i]):
        vegcost = lines[i]
        if '.' in vegcost:
            vegcost = vegcost.replace('.',',')
        elif not ',' in vegcost:
            vegcost = vegcost[0] + ',' + vegcost[1:]
        i += 1
        while len(lines[i]) == 0:
            i += 1
        dessert = lines[i]
    else:
        vegcost = '?'
        dessert = lines[i]
    return soup, meal, mealcost, veg, vegcost, dessert
