import hunspell


class HunSpell:
    hspell = hunspell.HunSpell("/Library/Spelling/index.dic", "/Library/Spelling/index.aff")

    def __init__(self):
        pass

    def add_words(self, words):
        for word in words:
            self.hspell.add(word)

    def verify_spelling(self, word):
        return self.hspell.spell(word)

    def get_suggestions(self, word):
        return self.hspell.suggest(word)
