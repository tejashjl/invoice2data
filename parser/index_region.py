class IndexRegion:
    def __init__(self, text, x, y):
        self.text = text
        self.x = x
        self.y = y

    def __repr__(self):
        return repr((self.text, self.x, self.y))
