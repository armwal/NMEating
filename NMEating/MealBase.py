import sqlite3
import os
import NMIParser
import TTRParser

os.remove(r'i:\Repositories\NMEating\database\test.db')
conn = sqlite3.connect(r'i:\Repositories\NMEating\database\test.db')

cursor = conn.cursor()

nmi_meal_command = """
CREATE TABLE NMImeals (
    meal_number INTEGER PRIMARY KEY,
    name VARCHAR(100));"""

nmi_plan_command = """
CREATE TABLE NMIplan (
    plan_number INTEGER PRIMARY KEY,
    name VARCHAR(100),
    small INTEGER,
    large INTEGER,
    date DATE,
    year INTEGER,
    week INTEGER);"""

ttr_meal_command = """
CREATE TABLE TTRmeals (
    meal_number INTEGER PRIMARY KEY,
    name VARCHAR(100));"""

ttr_plan_command = """
CREATE TABLE TTRplan (
    plan_number INTEGER PRIMARY KEY,
    name VARCHAR(100),
    price INTEGER,
    date DATE,
    year INTEGER,
    week INTEGER);"""

cursor.execute(nmi_meal_command)
cursor.execute(nmi_plan_command)
cursor.execute(ttr_meal_command)
cursor.execute(ttr_plan_command)

folder = r'i:\Repositories\NMEating\testdata\\'
for file in os.listdir(folder):
    if not file.endswith('.pdf'):
        continue
    meals, date = NMIParser.process_file(folder + file)
    print('KW ' + str(date.isocalendar()[1]) + ' ' + str(date.year))
    print(meals)
    format_str = """INSERT INTO NMIplan (plan_number, name, small, large, date, year, week) VALUES (NULL, \"{name}\", {small}, {large}, ?, {year}, {week});"""
    for meal in meals:
        name,costs = meal
        if len(costs) == 2:
            command = format_str.format(name=name, small=int(costs[0]*100), large=int(costs[1]*100), year=date.year, week=date.isocalendar()[1])
        else:
            command = format_str.format(name=name, small=int(costs[0]*100), large=int(costs[0]*100), year=date.year, week=date.isocalendar()[1])
        cursor.execute(command, (date,))
command = """SELECT DISTINCT name FROM NMIplan;"""
cursor.execute(command)
distinct = cursor.fetchall()
for dname in distinct:
    command = """INSERT INTO NMImeals (meal_number, name) VALUES (NULL, ?);"""
    cursor.execute(command, (dname[0],))

for file in os.listdir(folder):
    if not file.endswith('.png'):
        continue
    meals, date = TTRParser.process_file(folder + file, folder)
    format_str = """INSERT INTO TTRplan (plan_number, name, price, date, year, week) VALUES (NULL, \"{name}\", {price}, ?, {year}, {week});"""
    for m in meals:
        soup, meal, mealcost, veg, vegcost, dessert = m
        if mealcost == '?':
            command = format_str.format(name=meal, price='NULL', year=date.year, week=date.isocalendar()[1])
        else:
            command = format_str.format(name=meal, price=int(mealcost), year=date.year, week=date.isocalendar()[1])
        cursor.execute(command, (date,))
command = """SELECT DISTINCT name FROM TTRplan;"""
cursor.execute(command)
distinct = cursor.fetchall()
for dname in distinct:
    command = """INSERT INTO TTRmeals (meal_number, name) VALUES (NULL, ?);"""
    cursor.execute(command, (dname[0],))
conn.commit()

conn.close()