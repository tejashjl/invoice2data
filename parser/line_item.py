class LineItem:
    def __init__(self):
        self.description = ""
        self.catalog = ""
        self.amount = ""
        self.price_per_unit = ""
        self.discount = ""
        self.net_amount = ""
        self.ust = ""

    def set_description(self, description):
        self.description = description

    def set_catalog(self, catalog):
        self.catalog = catalog

    def set_amount(self, amount):
        self.amount = amount

    def set_price_per_unit(self, price_per_unit):
        self.price_per_unit = price_per_unit

    def set_discount(self, discount):
        self.discount = discount

    def set_net_amount(self, net_amount):
        self.net_amount = net_amount

    def set_ust(self, ust):
        self.ust = ust

    def __repr__(self):
        return repr((self.description, self.catalog, self.amount))
