from card import *
import random
from datetime import datetime
import tweepy
import boto3
import json

with open("twitter_keys.json", "r") as f:
    keys = json.load(f)

twitter_api = tweepy.Client(
    consumer_key=keys["apikey"],
    consumer_secret=keys["apisecret"],
    access_token=keys["accesstoken"],
    access_token_secret=keys["accesssecret"],
    return_type=dict
)


ddb = boto3.resource("dynamodb")
table = ddb.Table("CAH_combo_history")


def sort_lower(filename):
    with open(filename, "r", encoding="utf-8") as f:
        cards = json.load(f)

    for i in range(len(cards)):
        card = cards[i]
        if "change_lowercase" in card:
            continue

        print("\n\n{0}/{1}\n\n[{2}]\n\n\n\n".format(str(i + 1), str(len(cards)), card["text"]))
        user_input = input("'n' for leave alone on lowercase.")

        cards[i]["change_lowercase"] = (user_input != "n")

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(cards, f, indent=2, ensure_ascii=False)


def sort_lower_batch(filename):
    with open(filename, "r", encoding="utf-8") as f:
        cards = json.load(f)

    first_word_count = {}
    for card in cards:
        first_word = card["text"].split()[0]

        if first_word in first_word_count:
            first_word_count[first_word] += 1
        else:
            first_word_count[first_word] = 1

    first_words_m = [w for w in first_word_count.keys() if first_word_count[w] > 1]

    for i in range(len(first_words_m)):

        w = first_words_m[i]

        print("{}/{}".format(str(i + 1), str(len(first_words_m))))
        print()
        print("\n[{}]\n\n".format(w))

        u_input = input("'n' for dont change on start of sentence.")

        if u_input != "n":

            for j in range(len(cards)):
                card = cards[j]

                if "change_lowercase" in card:
                    continue

                first_word = card["text"].split()[0]

                if first_word == w:
                    cards[j]["change_lowercase"] = True

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(cards, f, indent=2, ensure_ascii=False)


def create_compact(filename):
    with open(filename, "r", encoding="utf-8") as f:
        cards = json.load(f)

    compact_cards = []
    for card in cards:

        l = 0
        if "change_lowercase" in card and card["change_lowercase"] == True:
            l = 1

        new_card = {"i": card["id"],
                    "t": card["text"],
                    "l": l}

        compact_cards.append(new_card)

    with open("compacts.json", "w", encoding="utf-8") as f:
        json.dump(compact_cards, f, ensure_ascii=False)


def getWhiteCards(filename, sheets=None):
    with open(filename, "r", encoding="utf-8") as f:
        j = json.load(f)

    if sheets is not None:
        for i in range(len(sheets)):
            sheets[i] = sheets[i].lower()

    cards = []
    for card_json in j:
        assert card_json["type"] == "A"

        sheet = card_json["sheet"]
        if sheets is not None and sheet not in sheets:
            continue

        cards.append(WhiteCard(card_json["id"],
                               card_json["text"],
                               card_json["set"],
                               sheet,
                               card_json["change_lowercase"]))
    return cards


def getBlackCards(filename, sheets=None):
    with open(filename, "r", encoding="utf-8") as f:
        j = json.load(f)

    if sheets is not None:
        for i in range(len(sheets)):
            sheets[i] = sheets[i].lower()

    cards = []
    for card_json in j:
        assert card_json["type"] == "Q"

        sheet = card_json["sheet"]
        if sheets is not None and sheet not in sheets:
            continue

        cards.append(BlackCard(card_json["id"],
                               card_json["text"],
                               card_json["answers"],
                               card_json["set"],
                               sheet))
    return cards


def random_combo(possible_blacks, possible_whites, seed=None):
    # Setup seed for random if none given
    if seed is None:
        seed = str(datetime.utcnow())
        r = random.Random(seed)
        random_number = r.randint(0, 9999999999)
        seed = str(datetime.utcnow()) + str(id(random_number)) + str(seed)
    r = random.Random(seed)

    # If black card given, use that or else pick random from given list
    if (isinstance(possible_blacks, BlackCard)):
        black = possible_blacks
    elif (isinstance(possible_blacks, list)):
        black = r.choice(possible_blacks)

    # Get random white cards to fill black cards quota
    whites = random.sample(possible_whites, black.answers)

    # Combo the cards together and return
    combo = CardCombo(black, whites)
    return combo


def add_to_history(card_combo, tweet_id=None):
    item = {"b_id": str(card_combo.black.id),
            "w_id": str(card_combo.white_id())}

    if tweet_id != None:
        item["t_id"] = str(tweet_id)

    r = table.put_item(Item=item)


def in_history(card_combo):
    item = {"b_id": str(card_combo.black.id),
            "w_id": str(card_combo.white_id())}

    r = table.get_item(Key=item)

    return "Item" in r


def get_new_combo(possible_blacks, possible_whites):
    black_card = random.choice(possible_blacks)

    attempts = 0
    done_before = True
    combo = None
    while done_before and attempts < 20:
        attempts += 1
        combo = random_combo(black_card, possible_whites)
        done_before = in_history(combo)

    if combo is None:
        raise Exception("Too many attempts to find whites that match black card {}".format(black_card.id))

    return combo


def tweet_new_combo():
    b = getBlackCards("cah_black_cards.json")
    w = getWhiteCards("cah_white_cards.json")

    combo = get_new_combo(b, w)

    tweet_text = combo.text

    resp = twitter_api.create_tweet(
        text=tweet_text
    )
    tweet_id = resp["data"]["id"]
    add_to_history(combo, tweet_id)

    return combo, tweet_id


def lambda_handler(event, context):

    combo, tweet_id = tweet_new_combo()

    return {
        'statusCode': 200,
        'body': {"combo": "{}/{}".format(combo.black.id, combo.white_id()),
                 "text": combo.text,
                 "tweet_id": tweet_id}
    }

lambda_handler(1,2)