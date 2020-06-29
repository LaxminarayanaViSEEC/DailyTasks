import math
import re
import time
from enum import Enum

import fitz
import numpy as np
import pandas as pd

import utils.validations as val
from implementations.table_proc_impl import TableImpl
from utils.pdf_impl_utils import (dataframe_to_dictionary_maker,
                                  dictionary_generator, 
                                  font_data_assembler,
                                  get_bbox_dict, 
                                  header_footer_assigner,
                                  ord_unord_1, 
                                  relationship_establisher, 
                                  excluder,
                                  tag_assigner, 
                                  filter_df,
                                  get_space_dist,
                                  block_mergerer,
                                  block_spliter,
                                  pdf_cordinates_scalaing)
from utils.utils import (check_table_area, 
                        in_table_area)


class PdfImpl(object):
    filename: str
    NAME_LIST: str = "Order/Unorder List"
    # adding for reference to customise user output
    tags: list = ['Heading', 'Paragraph', 'Page Number', 'Header', 'Footer']

    def __init__(self, fpath: str):
        self.filename = fpath

    def is_native(self, password: str=None) -> bool:
        """is_native 
        Checks nativity of pdf by gathering fonts used across pages

        Args:
            password (str, optional): Password to decrypt the pdf. Defaults to None.

        Raises:
            PermissionError: If password is not supplied and the document is encrypted

        Returns:
            bool: True or False based on the text content available in the document
        """
        # Read and create doc object
        self.process()
        if self.doc.isEncrypted and password is None:
            raise PermissionError('Document Encrypted please supply password')
        elif password is not None:
            _ = self.doc.authenticate(password=password)
        else:
            # getting list of fonts used in each page
            non_img_pages = [self.doc.getPageFontList(pno, full=False)
                             for pno in range(self.doc.pageCount)
                             if self.doc.getPageFontList(pno, full=False)]

            pct_of_text_pages = (len(non_img_pages)/self.doc.pageCount)*100

            print(pct_of_text_pages, '% of pages have text')

        self.metadata['pdfType'] = 'Native PDF' if pct_of_text_pages else 'Scanned PDF'

        # Return True if the pdf has any text in it else False
        return True if pct_of_text_pages else False


    def process(self, **options):
        """process 
        Processes pdf path

        Raises:
            FileNotFoundError: When file is not found or corrupted
        """
        if val.check_file(self.filename):
            self.doc = fitz.Document(self.filename, filetype='pdf', **options)
            self.metadata = {
                "No of Pages": self.doc.pageCount,
                "PDF Type": None,
                "Author": self.doc.metadata['author'],
                "Creator": self.doc.metadata['creator'],
                "Producer": self.doc.metadata['producer'],
                "Creation Date": self.doc.metadata['creationDate']
            }
            
        else:
            raise FileNotFoundError('File not found or invalid', self.filename)


    def pdf_extractor(self, page_range, tbl_obj: TableImpl = None):

        image_df = []
        font_metadata = {}
        word_df_list = []
        text_df_list = []
        line_df_list = []

        for page in page_range:
            # since the input values are 1 - indexed
            page = page-1
            blocks = self.doc.loadPage(page).getText('dict')['blocks']
            words = self.doc.loadPage(page).getText('words')
            bounds =list(self.doc.loadPage(page).bound())
            width, height = pdf_cordinates_scalaing(width=(bounds[2]-bounds[0]),height=(bounds[3]-bounds[1]))

            # space_dist = get_space_dist(words)
            space_dist = 10*height # multiply with height only

            word_df = pd.DataFrame(words, columns=['bbox_left', 'bbox_top', 'bbox_right', 'bbox_bottom',
                                                    'word', 'block_no', 'line_no', 'word_no'])
            word_df = word_df.assign(page_no=page)

            # Apply table filter to Words (ie) words within detected table regions are excluded for now
            if tbl_obj:
                table_bboxes = tbl_obj.get_table_area(page)
                table_mask = word_df.apply(
                    check_table_area, axis='columns', result_type='reduce', table_bboxes=table_bboxes)
                word_df = word_df[table_mask]

            block_counter = 0
            text_df = []
            line_df = []
            for internal_block in blocks:

                if internal_block['type'] == 1:
                    print('Skipping image block')

                    '''
                    # image_bytes = internal_block['image']
                    # # nparr = np.frombuffer(image_bytes, np.uint8)
                    # img=image_bytes.decode('utf-8')
                    # image_df.append({'page_no':page,'image':img,
                    #     'bbox_top':internal_block['bbox'][1],
                    #     'bbox_left':internal_block['bbox'][0],
                    #     'bbox_bottom':internal_block['bbox'][3],
                    #     'bbox_right':internal_block['bbox'][2]})
                    '''


                # elif PdfBlockTypes(internal_block['type']) is PdfBlockTypes.NORMAL and \
                        # not any([in_table_area(t_bbox, internal_block['bbox']) for t_bbox in table_bboxes]):
                elif internal_block['type'] == 0:
                    block_text = ''
                    font_size = []
                    font_name = []
                    lines = internal_block['lines']
                    line_counter = 0

                    for line in lines:
                        # line_id = f'page{page}_block{block_counter}_line{line_counter}'
                        line_text = ''
                        spans = line['spans']
                        line_bbox = line['bbox']
                        line_font_size = []
                        line_font_name = []

                        initial_space = True

                        for span in spans:
                            text_ = span['text'].strip()
                            print(len(text_),text_)
                            if initial_space:
                                prev = span['bbox']
                                line_text = text_
                                initial_space = False
                            else:
                                curr = span['bbox']
                                dist = prev[3]-curr[1]
                                
                                if dist > space_dist:
                                    line_text = f"{line_text}{text_}"
                                else:
                                    line_text = f"{line_text}|||{text_}"
                                prev = curr

                            # to make the font information relatable while differentiating!
                            if len(text_.strip()) > 0:
                                font_size.append(span['size'])
                                font_name.append(span['font'])
                                line_font_size.append(span['size'])
                                line_font_name.append(span['font'])
                                key = f"{span['size']}"
                                if key in font_metadata.keys():
                                    font_metadata[key] += 1
                                else:
                                    font_metadata[key] = 1

                        initial_space = True
                        line_text = line_text.strip('|||').strip()
                        

                        if len(line_text) == 0:
                            line_counter += 1
                        else:

                            bbox_dict = get_bbox_dict(line_bbox)
                            line_dict = dict(
                                page_no=page,
                                block_no=block_counter,
                                line_no=line_counter,
                                # line_id=line_id,
                                line=line_text,
                                size=line_font_size,
                                font_name=line_font_name
                            )
                            # Combine bbox and line dict
                            full_line_dict = {**line_dict, **bbox_dict}

                            line_df.append(full_line_dict)
                            line_counter += 1
                        block_text = f"{block_text}|||{line_text.encode('utf-8','ignore').decode('utf-8').strip()}".strip('|||').strip()
                        # block_text = f"{block_text} {line_text.strip()}".strip(
                        # )

                    if len(block_text) == 0:
                        block_counter += 1
                    else:
                        # block_id = f'page{page}_block{block_counter}'
                       
                        bbox_dict = get_bbox_dict(internal_block['bbox'])
                        block_dict = dict(
                            page_no= page,
                            block_no= block_counter,
                            # block_id= block_id,
                            text= block_text,
                            size= font_size,
                            font_name= font_name
                        )
                        # combine block and bbox information
                        block_data = {**block_dict, **bbox_dict}
                        text_df.append(block_data)
                        block_counter += 1

            #now perform check here to merge or delete the block
            text_df = pd.DataFrame(text_df)
            line_df = pd.DataFrame(line_df)

            # --- perfrom checks --- 
            text_df, line_df, word_df = block_mergerer(text_df, line_df, word_df,width,height)
            text_df, line_df, word_df = block_spliter(text_df, line_df, word_df,width,height)

            text_df_list.append(text_df)
            line_df_list.append(line_df)
            word_df_list.append(word_df)

        text_df = pd.concat(text_df_list,ignore_index=True)
        line_df = pd.concat(line_df_list,ignore_index=True)
        image_df = pd.DataFrame(image_df)
        word_df = pd.concat(word_df_list,ignore_index=True)

        text_df_text = text_df['text'].str.replace('|||',' ',regex=False)
        line_df_line = line_df['line'].str.replace('|||',' ',regex=False)

        text_df['text'] = text_df_text
        line_df['line'] = line_df_line

        text_df = text_df.assign(child = text_df.apply(relationship_establisher,args=(line_df,
                                'page_no','block_no'),axis=1))
        line_df = line_df.assign(child = line_df.apply(relationship_establisher,args=(word_df,
                                'page_no','block_no','line_no'),axis=1))
        
        font_information = font_data_assembler(font_metadata)
        self.metadata['Font Information'] = font_information

        text_df = text_df.assign(block_type = text_df.apply(tag_assigner,
                                                            args=(font_information,'blocks'),axis=1))
        line_df = line_df.assign(block_type = line_df.apply(tag_assigner,
                                                            args=(font_information,'lines'),axis=1))
        text_df = header_footer_assigner(text_df.copy(), 'text')
        text_df = text_df.assign(block=text_df['text'].apply(ord_unord_1))

        line_df = header_footer_assigner(line_df.copy(),'line')
        line_df = line_df.assign(block=line_df['line'].apply(ord_unord_1))

        list_filt = text_df['block'] == PdfImpl.NAME_LIST

        text_df.loc[list_filt, 'block_type'] = PdfImpl.NAME_LIST

        self.image_df = image_df
        self.text_df = text_df
        self.line_df = line_df
        self.word_df = word_df
        return self



    def get_json_data(self, pages_to_extract, exclude=None):
        block_group = self.text_df.groupby(['page_no'])
        line_group = self.line_df.groupby(['page_no'])
        word_group = self.word_df.groupby(['page_no'])
        # page_no = len(list(block_group['page_no'].count()))


        pages = []
        for page_ in pages_to_extract:
            print("Page no: ", page_)
            page = {'Index': page_, 'Blocks': []}
            # Since the input list is 1-indexed
            page_ = page_-1
            block_group_df = block_group.get_group(page_)

            # For output customisation
            if exclude:
                block_group_df = filter_df(block_group_df.copy(), exclude_list=exclude)

            data = list(block_group_df.apply(dataframe_to_dictionary_maker,axis=1,args=('Yes','text','No')).values)
            page['Blocks'].extend(data)

            line_group_df = line_group.get_group(page_)
            # For output customisation
            if exclude:
                line_group_df = filter_df(line_group_df.copy(), exclude_list=exclude)

            line_data = list(line_group_df.apply(dataframe_to_dictionary_maker,axis=1,args=('Yes','line','Yes')).values)
            page['Blocks'].extend(line_data)
            try:
                word_group_df = word_group.get_group(page_)
                word_data = list(word_group_df.apply(dataframe_to_dictionary_maker,axis=1,args=('No','word','No')).values)
                page['Blocks'].extend(word_data)
                pages.append(page)
            except KeyError as e:
                print("Skipping this page: ", page_, " for word df")
                print("Error: ", e)

        json_data = {
            "Metadata": self.metadata,
            "Pages": pages
        }
        return json_data


    def get_page_data(self, pno: int, extract_type: str):
        """get_page_data 
        Get page data from the pdf according to extract_type

        Arguments:
            pno {int} -- Page no to extract
            extract_type {str} -- Type of extraction

        Returns:
            dict, list, str -- data type based on the block
        """
        page_data = self.doc.getPageText(pno, extract_type)
        return page_data


class PdfBlockTypes(Enum):
    """PdfBlockTypes 
    Block type enumerations

    Numbers representing the block types of a pdf (maping with PyMupdf)
    """
    NORMAL = 0
    IMAGE = 1
