from pdf_extractor import extract_data
import argparse
import json
import sys

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help="Give path to extract pdf file", type=str)
    parser.add_argument("op_path", help="Give path to save txt with pdf output", type=str)
    args = parser.parse_args()


    json_data = extract_data(file_path=args.file_path,
                                pages='1',
                                password=None,
                                exclude_type='')

    with open(args.op_path, 'w',encoding='utf-16') as file_:
        json.dump(json_data,file_)
