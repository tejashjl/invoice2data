import glob
import logging
import os
import unittest
from controller.invoice_controller import service


def setup_logger(name, log_file, level=logging.INFO):
    if not os.path.exists("../logs"):
        os.makedirs("../logs")
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


class VerifyTotalCostTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.template_directory = "/Users/tejashl/Projects/invoice2data/invoice2data/parser/templates/"
        self.template_path = self.template_directory + "3m-rechnung-without-desc-title.yml"
        self.assertionErrors = []
        self.logger = setup_logger('invoice2data_TEST', '../logs/test_logfile.log')

    def tearDown(self):
        pass

    def test_total_net_amount_of_items_equals_total_cost(self):
        os.chdir("../../pdf_files")
        total_no_files = len(glob.glob("*.pdf"))
        for invoice_file in glob.glob("*.pdf"):
            self.logger.info('Testing %s', invoice_file)
            template = open(self.template_path, "rb")
            invoice_file_path = os.path.abspath(invoice_file)
            parsed_data = service.parse_invoice(invoice=invoice_file_path, template=template, file_type="PDF")[0]
            total_amount_untaxed = parsed_data['amount_untaxed'] if 'amount_untaxed' in parsed_data else 0.0
            if 'lines' in parsed_data:
                total_net_amount = self.get_total_net_amount(parsed_data['lines'])
            else:
                total_net_amount = 0.0
            self.logger.info('TOTAL NET AMOUNT = %s', total_net_amount)
            self.logger.info('TOTAL AMOUNT UNTAXED = %s', total_amount_untaxed)
            try:
                self.assertEqual(total_net_amount, total_amount_untaxed, "Total Net Amount Mismatch")
            except AssertionError, e:
                self.logger.error('Total Net Amount Is Not Equal')
                self.assertionErrors.append(str(e))
                # self.assertEqual(total_net_amount, total_amount_untaxed, "Total Net Amount Mismatch")
        self.logger.info('Total No Of Files = %d', total_no_files)
        self.logger.info('No Of Files Not Matched = %d', len(self.assertionErrors))

    def get_total_net_amount(self, line_items):
        total_net_amount = 0.0
        for index, line_item in enumerate(line_items):
            net_amount = float(
                line_item['net_amount'].replace(".", "").replace(",", ".")) if 'net_amount' in line_item else 0.0
            self.logger.debug('Line item[%s] net amount= %s', index, net_amount)
            total_net_amount += net_amount
        return round(total_net_amount, 2)


if __name__ == '__main__':
    unittest.main()
