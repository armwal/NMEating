import NMIParser
import TTRParser
import os

# folder = r'i:\Repositories\NMEating\testdata\\'
# for file in os.listdir(folder):
#     meals, date = NMIParser.process_file(folder + file)
#     print('KW ' + str(date.isocalendar()[1]) + ' ' + str(date.year))
#     print(meals)
meals = TTRParser.process_file(r'i:\Repositories\NMEating\testdata\Speiseplan_TTR_KW03-1.png',r'i:\Repositories\NMEating\testdata\\')
print(meals)