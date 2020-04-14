import json

from card import *
from cards import masterCards
import random
from datetime import datetime
import csv




def blackcsv2json(csv_filename, json_filename):

    # Black cards
    with open(csv_filename, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar="\"")

        blacks_json = []
        blacks_set = set()
        id = 1
        dupes = 0

        for row in reader:
            text = row[0]
            special = row[1]
            card_set = row[2]
            sheet = row[3]

            if (text.lower() == "prompt cards"):
                continue

            if (text.strip() == ""):
                continue

            # Shorten all underscores to a single one
            text = text.strip()
            while "__" in text:
                text = text.replace("__", "_")


            if text.lower() in blacks_set:
                dupes += 1
                continue
            blacks_set.add(text.lower())


            special = special.lower().strip().replace(",", "")
            if special == "":
                answers = 1
            elif special == "pick 1":
                answers = 1
            elif special == "pick 2":
                answers = 2
            elif special == "draw 2 pick 3":
                answers = 3
            else:
                print("ERROR: Special row is '{}'".format(special))
                print(text)
                exit(0)



            j = {"id": "Q" + str(id),
                 "type": "Q",
                 "text": text,
                 "answers": answers,
                 "set": card_set.lower().strip(),
                 "sheet": sheet.lower().strip()}
            print("Done " + str(id))
            id += 1
            blacks_json.append(j)

    with open(json_filename, "w", encoding="utf-8") as json_file:
        json.dump(blacks_json, json_file, indent=2, ensure_ascii=False)

    print("Done with {} dupes".format(str(dupes)))

def whitecsv2json(csv_filename, json_filename):

    with open(csv_filename, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar="\"")

        whites_json = []
        whites_set = set()
        id = 1
        dupes = 0

        for row in reader:
            text = row[6]
            card_set = row[7]
            sheet = row[8]

            if (text.lower() == "response cards"):
                continue

            text = text.strip()
            if text == "":
                continue

            if text.lower() in whites_set:
                dupes += 1
                continue
            whites_set.add(text.lower())

            j = {"id": "A" + str(id),
                 "type": "A",
                 "text": text,
                 "set": card_set.lower().strip(),
                 "sheet": sheet.lower().strip()}
            print("Done " + str(id))
            id += 1
            whites_json.append(j)

    with open(json_filename, "w", encoding="utf-8") as json_file:
        json.dump(whites_json, json_file, indent=2, ensure_ascii=False)

    print("Done whites with {} dupes".format(str(dupes)))






