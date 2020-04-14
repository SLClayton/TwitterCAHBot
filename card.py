

chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
bold_chars = "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵"
bold_dict = {"Ü": "𝗨̈",
             "à": "𝗮̀",
             "é": "𝗲́",
             "ñ": "𝗻̃",
             "ö": "𝗼̈"}
for i in range(len(chars)):
    bold_dict[chars[i]] = bold_chars[i]


def bold(input):
    s = ""
    for c in input:
        try:
            s += bold_dict[c]
        except KeyError:
            s += c
    return s



class Card:
    def __init__(self, id, text, set, sheet):
        self.id = id
        self.text = text
        self.set = set
        self.sheet = sheet

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.text


class WhiteCard(Card):
    def __init__(self, id, text, set, sheet, change_lowercase):
        Card.__init__(self, id, text, set, sheet)
        self.change_lowercase = change_lowercase


    def getText(self, start, end):

        text = self.text

        if not start and self.change_lowercase:
            text = text[0].lower() + text[1:]


        if not end and text[-1] == ".":
            text = text[:-1]


        return text



class BlackCard(Card):
    def __init__(self, id, text, answers, set, sheet):
        Card.__init__(self, id, text, set, sheet)
        self.answers = answers


    def getText(self):
        return self.text


class CardCombo():


    def __init__(self, black, whites):

        self.black = black
        self.whites = whites
        self.answers = black.answers
        self.text = black.text

        w = whites.copy()

        # Replace gaps in black card text with white card text
        while "_" in self.text:

            if len(w) > 0:
                start = False
                if self.text.startswith("_"):
                    start = True
                white_text = bold(w.pop(0).getText(start=start, end=False))

            self.text = self.text.replace("_", white_text, 1)


        # If more whites to go, then generate an answer list to go after.
        first = True
        if (len(w) > 0):
            self.text += "\n\n"

            while len(w) > 2:
                self.text += bold(w.pop(0).getText(start=first, end=False)) + ", "
                first = False

            if len(w) > 1:
                self.text += bold(w.pop(0).getText(start=first, end=False)) + ", and "
                first = False

            if (len(w) == 1):
                self.text += bold(w.pop(0).getText(start=first, end=True))
                if (self.text[-1] not in ".!?…"):
                    self.text += "."



    def __repr__(self):
        return self.text


    def __str__(self):
        return self.text


    def white_id(self):
        wids = []
        for c in self.whites:
            wids.append(c.id)
        return "/".join(wids)





