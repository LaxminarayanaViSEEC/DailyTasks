import json
import logging

import fitz
from implementations.pdf_reader_impl import PdfImpl
from implementations.table_proc_impl import TableImpl
from utils.pdf_impl_utils import get_pages_to_read, page_range_checker


def check_is_native(pdf_path: str, pwd: str=None) -> str:
    """check_is_native 
    Checks nativity with PdfImpl methods

    Args:
        pdf_path (str): Path to pdf
        pwd (str, optional): Password if file needs to be decrypted. Defaults to None.

    Returns:
        Union[bool, None]: Returns True or False, if it is able
                           to read the file else returns None
    """
    pdf_file = PdfImpl(pdf_path)
    try:
        nativity: bool = pdf_file.is_native(password=pwd)
    except PermissionError as identifier:
        nativity: None = None
        print(identifier)

    return nativity


# filepath (str) – Filepath or URL of the PDF file.
# pages (str, optional (default: '1')) – Comma-separated page numbers. Example: ‘1,3,4’ or ‘1,4-end’ or ‘all’.
# password (str, optional (default: None)) – Password for decryption.
# exclude_type (list, optional (default: None)) – ['table','page_header','page_footer','paragraph','ord_list']

def extract_data(file_path: str, pages: str='1', password: str=None, exclude_type: str = '') -> dict:
    """extract_data 
    Extracts data from pdf

    Args:
        file_path (str): Path to pdf file
        pages (str, optional): Pages or page ranges to get from pdf (eg). '1', '1,2,5', '1-5, 6-10, 20-25', Defaults to '1'.
        password (str, optional): [description]. Defaults to None.
        exclude_type (str, optional): Comma seperated string of tags to include. Defaults to ''.

    Raises:
        IndexError: [description]

    Returns:
        dict: [description]
    """
    pdf_obj = PdfImpl(fpath=file_path)
    pdf_obj.process()

    # Get the list of page numbers to process
    if pages == 'all':
        pages_to_extract = [page_+1 for page_ in range(pdf_obj.doc.pageCount)]
    else:
        pages_to_extract = get_pages_to_read(pages)
    
    print(pages_to_extract)
    # Get page numbers which exceed the page count
    inv_pages: list = [pgno for pgno in pages_to_extract if pgno > pdf_obj.doc.pageCount]

    if inv_pages:
        raise IndexError('Page numbers: ', ','.join(inv_pages), ' does not exist in the document')
    else:
        tbl_obj = None
        if 'Tables' in exclude_type or 'Table' in exclude_type:
            tbl_obj = TableImpl(fpath=file_path, page_count=pdf_obj.doc.pageCount)
            tbl_obj.process(output_format='json',multiple_tables=True) 

        pdf_obj.pdf_extractor(pages_to_extract, tbl_obj=tbl_obj)
        json_data = pdf_obj.get_json_data(exclude=exclude_type.split(','), pages_to_extract=pages_to_extract)

    return json_data