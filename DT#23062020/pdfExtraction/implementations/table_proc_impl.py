""" pdf Table Implementation """

from tabula import read_pdf
import tabula.errors as pdf_err

from typing import Union, List

# from .import utils.validations as val
from utils import validations as val
import logging


class TableImpl(object):
    filepath: str
    table_bbox: List # List with each index specifying the tables found in each page
    page_count: int

    def __init__(self, fpath: str, page_count: int):
        self.filepath = fpath
        self.page_count = page_count
        self.table_bbox = []

    def process(self, **options):
        """process 
        Processes pdf and finds tables based on options given

        Arguments:
            options {kwargs} -- Arguements to pass to table extractor

        Raises:
            FileNotFoundError: Raises File not found error

        Returns:
            list(JSON like), pd.DataFrame -- Returns table data
        """
        # Checks file path
        if val.check_file(self.filepath):
            try:
                for page_no in range(1, self.page_count+1):
                    self.table_bbox.append(read_pdf(self.filepath, pages=[page_no], **options))
            except pdf_err.CSVParseError as e:
                logging.exception('CSV parse Error', self.filepath, e)
            except pdf_err.JavaNotFoundError as e:
                logging.exception('Java path needs to in the environment variable JAVA_HOME', e)
            except Exception as e:
                logging.exception('Exception occurred', e, self.filepath)

        else:
            raise FileNotFoundError('File not found or invalid', self.filepath)

    def get_table_area(self, page_no: int):
        """get_table_area 
        Get table regions of a particular page from pdf

        Arguments:
            page_no {int} -- page no to check

        Returns:
            list -- List of table regions as bboxes
        """

        table_data = self.table_bbox[page_no-1]

        # Return empty list if no table was found else the list of bbox coords
        if len(table_data) > 0:
            x=table_data[0]
            
            tab = [
                (table['left'], table['top'], table['right'], table['bottom']) 
                for table in table_data
            ]
            return tab
        else:
            return []
        


if __name__ == "__main__":
    # test should return a list with four empty lists
    from pprint import pprint
    pdf = TableImpl(r'data\no table.pdf', 4)
    pdf.process(output_format='json', multiple_tables=True)
    pprint(pdf.table_bbox)