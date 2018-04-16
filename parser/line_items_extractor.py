from parser.text_auto_corrector import HunSpell
from parser.text_extractor import get_word_boxes_from_image
from parser.utils import convert_pdf_to_images

hun_spell = HunSpell()
table_titles = ['Artikelbezeichnung', '3M Nr. EAN/UPC Katalog Nr. Bestelltes Produkt', 'Menge / Einheit',
                'Preis pro Einheit', 'Rabatt', 'Nettobetrag', 'USt. %']
hun_spell.add_words(table_titles)


def process_table_title():
    processed_titles = []
    for title in table_titles:
        processed_titles.extend(title.split())
    return processed_titles


def extract_line_items(invoice_file_path):
    image_file_paths = convert_pdf_to_images(invoice_file_path)
    for index, image_file_path in enumerate(image_file_paths):
        matching_word_boxes = []
        word_boxes = get_word_boxes_from_image(image_file_path)
        for word in word_boxes:
            if not hun_spell.verify_spelling(word.content):
                suggested_words = hun_spell.get_suggestions(word.content)
                auto_corrected_word = suggested_words[0] if suggested_words else ""
            else:
                auto_corrected_word = word.content
            if auto_corrected_word:
                plain_word = remove_symbols(auto_corrected_word)
            else:
                plain_word = ""
            if plain_word in table_titles:
                matching_word_boxes.append(word)

        print matching_word_boxes


def remove_symbols(word):
    symbols = u'!"#%\'()*+,-./:;<=>?@[\]^_`{|}~'
    for symbol in symbols:
        word = word.replace(symbol, "")
    return word
