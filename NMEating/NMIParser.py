import re
import datetime
from decimal import Decimal

from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine

def process_file(filename):
    text = extract_text_from_pdf(filename)
    meals = parse_meal_text(text)
    date = parse_date(text)
    return meals,date

def parse_cost_line(line):
    money = re.compile('[0-9]+,[0-9][0-9] EUR')
    found = money.findall(line)
    return list([Decimal(re.sub(',','.',re.sub('[^\d,]','',f))) for f in found])

def parse_meal_text(text):
    daysOfWeek = ['Montag','Dienstag','Mittwoch','Donnerstag','Freitag']
    currentDay = 0
    lines = text.splitlines()
    meals = []
    for i in range(len(lines)):
        line = lines[i]
        if line.strip() == daysOfWeek[currentDay]:
            currentDay += 1
            meal = lines[i+1].strip().strip('1234567890,').strip().strip('1234567890,')
            cost = lines[i+2].strip()
            if any(char.isdigit() for char in cost):
                # probably a meal
                costs = parse_cost_line(cost)
                meals = meals + [tuple([meal, costs])]
            elif any(char.isdigit() for char in lines[i+3].strip()):
                # probably two-line meal
                meal += ' ' + cost.strip().strip('1234567890,').strip().strip('1234567890,')
                cost = lines[i+3].strip()
                costs = parse_cost_line(cost)
                meals = meals + [tuple([meal, costs])]
            if currentDay == len(daysOfWeek):
                break

    return meals

def parse_date(text):
    lines = text.splitlines()
    date = re.compile(r'.*([0-3][0-9]\.[0-1][0-9]\.20[0-9][0-9])')
    for line in lines:
        if 'Woche vom' in line:
            match = date.match(line)
            if match:
                return datetime.datetime.strptime(match.group(1),'%d.%m.%Y')


def extract_text_from_pdf(filename):
    fp = open(filename, 'rb')
    parser = PDFParser(fp)
    doc = PDFDocument()
    parser.set_document(doc)
    doc.set_parser(parser)
    doc.initialize('')
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    text = ""
    # Process each page contained in the document.
    for page in doc.get_pages():
        interpreter.process_page(page)
        layout = device.get_result()
        for lt_obj in layout:
            if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                text += lt_obj.get_text()
    return text
