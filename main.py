import PyPDF2
import os
import json
from sqlalchemy.orm import Session
from sqlalchemy import select

from db import db_connect, Faction, Unit

rulesList = []

fileName = "rules.json"
pvFileName = "Point Values.pdf"
pvJson = "pointValues.json"
pathToIndexes = "G:/Мій диск/Warhammer/10th"
pathToPVs = "G:/Мій диск/Warhammer/10th"


def Scan(rulesList, fileName, pathToIndexes):
    files = list(filter(lambda x: "Index" in x, os.listdir(pathToIndexes)))

    if files.count == 0:
        files = list(filter(lambda x: "Index" in x, os.listdir("/indexes")))

    for f in files:
        armyIndex = {
            "name": f.split(".")[0].replace("Index", "").strip(),
            "rules": [],
            "units": [],
        }
        reader = PyPDF2.PdfReader(pathToIndexes + "/" + f)
        numPages = len(reader.pages)
        isFront = True
        data_cards = {
            "front": {},
            "back": {},
            "name": {},
            "keywords": {},
            "points_value": [{"models": 1, "points": 1}],
        }
        for p in reader.pages:
            if p.extract_text() == "":
                print("Art Page: Skipping")
            elif "ARMOURY" in p.extract_text():
                print("Armoury Page: Skipping")
            elif p.mediabox.width < 500:
                # Rules page
                armyIndex["rules"].append(p.extract_text())
            else:
                # data card
                if isFront:
                    data_cards["front"] = p.extract_text()
                    dc_name = p.extract_text().split("KEYWORDS")[0].strip()
                    if "\n" in dc_name:
                        dc_name = dc_name.split("\n")[0]
                    data_cards["name"] = dc_name
                    print(f"Processing: {armyIndex['name']}/{data_cards['name']}")
                    isFront = not isFront
                else:
                    data_cards["back"] = p.extract_text()
                    s1 = p.extract_text().replace("\n", "")
                    s2 = s1.split("KEYWORDS")[1]
                    s3 = s2.replace(":", "")
                    s4 = s3.split("\n")[0]
                    data_cards["keywords"] = s4.replace("FACTION", "").strip()
                    isFront = not isFront
                    armyIndex["units"].append(data_cards.copy())
                    data_cards["front"] = {}
                    data_cards["back"] = {}
        rulesList.append(armyIndex)
    if os.path.exists(pvJson):
        os.remove(pvJson)
        print("File exists, replacing")
    jsonRules = open(pvJson, "x")
    jsonRules.write(
        json.dumps(rulesList, indent=4).replace("\u2013", "-").replace("\n", " ")
    )


def Upload(rulesList):
    engine = db_connect()
    with Session(engine) as session:
        for faction in rulesList:
            db_f = session.execute(
                select(Faction).where(Faction.name == faction["name"])
            ).first()

            if db_f is None:
                f = Faction(name=faction["name"])
                session.add(f)
                session.commit()
                db_f = session.execute(
                    select(Faction).where(Faction.name == faction["name"])
                ).first()
            db_f = db_f[0]

            print(f"{db_f.faction_id}. {db_f.name}")

            for unit in faction["units"]:
                db_u = session.execute(
                    select(Unit).where(Unit.name == unit["name"])
                ).first()   

                if db_u is None:
                    u = Unit(
                        name=unit["name"],
                        faction_id=db_f.faction_id,
                        keywords=unit["keywords"],
                        meta=unit["front"] + "-(|)-" + unit["back"],
                    )
                    session.add(u)
                    session.commit()


def ScanPointsValues(pathToPVs, pvFileName):
    reader = PyPDF2.PdfReader(pathToPVs + "/" + pvFileName)
    pv_list = []
    for p in reader.pages:
        pvtext = p.extract_text()
        if 'FIELD MANUAL' in pvtext:
            print('Title page: Skipping')
        else:
            values = pvtext.split('\n')
            unitPvs = {
                'faction': values[0],
                'name': '',
                'pvs': []
            }
            for record in values:
                if record == unitPvs["faction"]:
                    print(f"Faction name: " + record)
                elif 'model' not in record:
                    if unitPvs["name"] != '':
                        pv_list.append(unitPvs.copy())
                        unitPvs["pvs"] = []
                    unitPvs["name"] = record
                else:
                    unitPvs['pvs'].append(record.replace('.',''))
    
    if os.path.exists(pvFileName):
        os.remove(pvFileName)
        print("File exists, replacing")
    jsonRules = open(pvFileName, "x")
    jsonRules.write(
        json.dumps(pv_list, indent=4).replace("\u2013", "-").replace("\n", " ")
    )



sel = -1

while sel != "0":
    print("Select Mode:")
    print("1. Scan")
    print("2. Upload")
    print("3. Scan and Upload")
    print("4. Scan Points Values")
    print("0. Exit")
    sel = input("> ")
    if sel == "1":
        Scan(rulesList, fileName, pathToIndexes)
    elif sel == "2":
        if rulesList == []:
            print("Loading data from file")
            f = open(fileName, "r")
            rulesList = json.load(f)
        Upload(rulesList)
    elif sel == "3":
        Scan(rulesList, fileName, pathToIndexes)
        Upload(rulesList)
    elif sel == "4":
        ScanPointsValues(pathToPVs, pvFileName)
    elif sel == "0":
        exit
    else:
        print("Invalid Input")
    d = input("Press 'Enter' key to continue")
    os.system("cls")
