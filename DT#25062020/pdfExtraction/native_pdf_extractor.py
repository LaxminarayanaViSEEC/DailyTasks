import logging
from implementations.table_proc_impl import TableImpl
from implementations.pdf_reader_impl import PdfImpl
from implementations.pdf_reader_impl import PdfBlockTypes
from utils.utils import in_table_area
from utils.pdf_impl_utils import get_pages_to_read,page_range_checker
import json

def extract_texts_without_table(pdf_path, op_path, pages_required='all'):
    """
    Extracts texts without table text
    """
    
    pdf_obj = PdfImpl(fpath=pdf_path)
    pdf_obj.process()
    if pages_required == 'all':
        pages_to_extract = [page_+1 for page_ in range(pdf_obj.doc.pageCount)]
    else:
        pages_to_extract = get_pages_to_read(pages_required)
    value = page_range_checker(pdf_obj.doc.pageCount,pages_to_extract)
    if value:
    # tbl_obj = TableImpl(fpath = pdf_path, page_count = pdf_obj.doc.pageCount)
    # tbl_obj.process(output_format='json',multiple_tables=True)

        pdf_obj.pdf_extractor(pages_to_extract)
        test=pdf_obj.get_json_data(pages_to_extract)
        
        with open(op_path, 'w') as file_:
            json.dump(test,file_)
    else:
        raise Exception('Pages range provided is out of pdf page range scope!!')


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help="Give path to extract pdf file", type=str)
    parser.add_argument("op_path", help="Give path to save txt with pdf output", type=str)
    # parser.add_argument("pages", help="Give range of pages or number of pages with comma seperated ",default= 'all', type=str)

    args = parser.parse_args()

    # get texts and write output
    extract_texts_without_table(args.file_path, args.op_path, pages_required='all')
