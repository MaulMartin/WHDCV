import PyPDF2
import os
import re  # re.search(string, text)
import json
from sqlalchemy.orm import Session
from sqlalchemy import select

from db import db_connect, Faction, Unit

rulesList = []

fileName = "rules.json"
pathToIndexes = "G:/Мій диск/Warhammer/10th"

files = list(filter(lambda x: "Index" in x, os.listdir(pathToIndexes)))

for f in files:
    armyIndex = {"name": f.split('.')[0], "rules": [], "units": []}
    reader = PyPDF2.PdfReader(pathToIndexes + "/" + f)
    numPages = len(reader.pages)
    isFront = True
    data_cards = {"front": {}, "back": {}, "name": {}, "keywords": {}, "points_value": [{"models": 1, "points": 1}]}
    for p in reader.pages:
        if p.extract_text() == '':
            print("Art Page: Skipping")
        elif 'ARMOURY' in p.extract_text():
            print("Armoury Page: Skipping")
        elif p.mediabox.width < 500:
            # Rules page
            armyIndex["rules"].append(p.extract_text())
        else:
            # data card
            if isFront:
                data_cards["front"] = p.extract_text()
                dc_name = p.extract_text().split('KEYWORDS')[0].strip()
                if '\n' in dc_name:
                    dc_name = dc_name.split('\n')[0]
                data_cards["name"] = dc_name
                print(f"Processing: {armyIndex['name']}/{data_cards['name']}")
                isFront = not isFront
            else:
                data_cards["back"] = p.extract_text()
                s1 = p.extract_text()
                s2 = s1.split('KEYWORDS')[1]
                s3 = s2.replace(':','')
                s4 = s3.split('\n')[0]
                data_cards["keywords"] = s4.replace('FACTION','').strip()
                isFront = not isFront
                armyIndex["units"].append(data_cards.copy())
                data_cards["front"] = {}
                data_cards["back"] = {}
    rulesList.append(armyIndex)

if os.path.exists(fileName):
    os.remove(fileName)
    print('File exists, replacing')

jsonRules = open(fileName, "x")
jsonRules.write(json.dumps(rulesList, indent=4).replace('\u2013', '-').replace('\n', ' '))
 
# engine = db_connect()
# with Session(engine) as session:
#     for faction in rulesList:
#         f = Faction(z
#         )

#         session.add(f)

#         db_f = select(Faction).where(Faction.name == faction.name)

#         units_list = []

#         for unit in faction.units:
#             units_list.append(Unit(
#                 __name__ = ''
#             ))





print("Finished")
