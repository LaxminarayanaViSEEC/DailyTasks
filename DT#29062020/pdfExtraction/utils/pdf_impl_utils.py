from typing import Union
from itertools import chain
from statistics import mean
from operator import itemgetter
import random
import numpy as np
import re
import pandas as pd
from collections import deque
import ast

def font_data_assembler(font_size: dict) -> dict:
    paragraph = max(list(font_size.values()))
    paragraph_key = list(font_size.values()).index(paragraph)
    paragraph = float(list(font_size.keys())[paragraph_key])
    font_keys = list(map(lambda x: float(x),
                            list(font_size.keys())))

    main_header = max(font_keys)
    output_fonts = {
        'Heading_1': main_header,
        'Paragraph': paragraph
    }

    subscript, headings = [], []
    for font in font_keys:
        if font < paragraph:
            subscript.append(font)
        elif font > paragraph:
            headings.append(font)

    subscript = sorted(subscript, reverse=True)
    headings = sorted(headings, reverse=True)

    for val, subspt in enumerate(subscript):
        output_fonts[f'Subscript_{val+1}'] = subspt
    val = 2

    for head in headings:
        if head in output_fonts.values():
            continue
        else:
            output_fonts[f'Heading_{val}'] = head
            val += 1
    return output_fonts

def relationship_establisher(row,df,*args):
    page_no=row['page_no']
    block_no=row['block_no']
    group_data = df.groupby(list(args))
    if len(args) == 2:
        filtered = list(group_data.get_group((page_no,block_no))['line_no'])
        return [f'page{page_no}_block{block_no}_line{i}' for i in filtered]
    elif len(args) == 3:
        line_no = row['line_no']
        try:
            filtered = list(group_data.get_group((page_no,block_no,line_no))['word_no'])
            return [f'page{page_no}_block{block_no}_line{line_no}_word{i}' for i in filtered]
        except:
            return []

def tag_assigner(data_dict, font_kind, dataframe_of):
    if dataframe_of == 'blocks':
        text = data_dict['text']
    elif dataframe_of == 'lines':
        text = data_dict['line']
    font_size = data_dict['size']
    paragraph_size = font_kind['Paragraph']
    font_type = data_dict['font_name']
    

    size = max(set(font_size), key=font_size.count)
    most_occuring_font = max(set(font_type), key=font_type.count)

    if 'bold' in most_occuring_font.lower() and len(text.split(' ')) < 13:
        return 'Heading'
    elif size > paragraph_size:
        return 'Heading'
    else:
        return 'Paragraph'

def ord_unord(x):
    if any([
        # for sentence (a.) (a)
        re.search(
            r"^[\(][a-zA-Z0-9][\. a-zA-Z0-9\)][\. \\a-zA-Z\)][\\n\w \)\.].*", x),
        # 1.\nhell0
        re.search(r"^[a-z0-9][\. a-zA-Z0-9][\\][\\n\w ].*", x),
        # 1. hello
        re.search(r"^[0-9a-z][\.].*", x),
        # \u2014.kinda text
        re.search(
            r"^[\\\(][0-9\\\\u][0-9\\u][0-9][0-9][0-9][ 0-9\.\\][\w \)].*", x),
        # \u2014 kinda text
        re.search(r"^[\\\(][\\u\\][A-Za-z0-9\\u]{4}.*", x),
        # if the bullet character comes in front of text
        re.search(r"^.*", x)
    ]):
        x = "Order/Unorder List"
    else:
        x = np.nan
    return x


def page_number_checker(text):
    # 1
    # 1/7
    # iv
    # IV
    search = re.search(r"^\b[a-zA-Z0-9_/-]+\b$", text)
    try:
        if search.string == text:
            if any(map(str.isdigit, text)):
                return True
            elif any([('i' in text.lower()),('v' in text.lower()),('x' in text.lower())]):
                if len(text)<=4:
                    return True
        else:
            return False
    except:
        # page 5 0f 100
        if 'page' in text.lower():
            if any(map(str.isdigit, text)):
                if len(text.split(' ')) <= 5:
                    return True
        # - 65 -
        search = re.search(r"^[-][ ]\b[a-zA-Z0-9_/-]+[ ][-]", text)
        try:
            if search.string == text:
                return True
        except:
            return False


def header_footer_assigner(dataframe,column_name):
    """Assigns Header and footer for the given dataframe

    Arguments:
        dataframe {pd.DataFrame} -- dataframe should contain page_no and Text columns
    """
    group = dataframe.groupby('page_no')
    header = []
    footer = []
    h_initial = True
    f_initial = True

    refrence_checker_header = []
    refrence_checker_footer = []
    header_index = []
    footer_index = []
    page_number_index = []

    for i, j in group:
        j = j.sort_values(by=['bbox_left', 'bbox_top'])

        head = list(j.index[:3])
        foot = sorted(list(j.index[-3:]), reverse=True)

        if len(header) == 0 and len(footer) == 0:

            header = [(j.loc[i, 'bbox_left'], j.loc[i, 'bbox_top'],
                        j.loc[i, 'bbox_right'], j.loc[i, 'bbox_bottom']) for i in head]
            page_number_head = [j.loc[i,column_name] for i in head]
            page_number_foot = [j.loc[i,column_name] for i in foot]
            footer = [(j.loc[i, 'bbox_left'], j.loc[i, 'bbox_top'],
                        j.loc[i, 'bbox_right'], j.loc[i, 'bbox_bottom']) for i in foot]

            header_initial_index = head
            footer_initial_index = foot

            for page_check_text in page_number_head:
                val = page_number_checker(page_check_text)
                if val:
                    ind_=page_number_head.index(page_check_text)
                    page_number_index.append(header_initial_index[ind_])

            for page_check_text in page_number_foot:
                val = page_number_checker(page_check_text)
                if val:
                    ind_=page_number_foot.index(page_check_text)
                    page_number_index.append(footer_initial_index[ind_])
        else:
            head_ = [(j.loc[i, 'bbox_left'], j.loc[i, 'bbox_top'],
                        j.loc[i, 'bbox_right'], j.loc[i, 'bbox_bottom']) for i in head]
            page_number_head_ = [j.loc[i,column_name] for i in head]
            
            page_number_foot_ = [j.loc[i,column_name] for i in foot]
        
            foot_ = [(j.loc[i, 'bbox_left'], j.loc[i, 'bbox_top'],
                        j.loc[i, 'bbox_right'], j.loc[i, 'bbox_bottom']) for i in foot]

            for page_check_text in page_number_head_:
                val = page_number_checker(page_check_text)
                if val:
                    ind_=page_number_head_.index(page_check_text)
                    page_number_index.append(head[ind_])
            
            for page_check_text in page_number_foot_:
                val = page_number_checker(page_check_text)
                if val:
                    ind_=page_number_foot_.index(page_check_text)
                    page_number_index.append(foot[ind_])

            for check_head in header:
                if check_head in head_:
                    refrence_checker_header.append(True)
                    h_index = head_.index(check_head)
                    real_h_index = head[h_index]
                        
                    # dataframe.loc[real_h_index, 'block_type'] = 'Header'
                    header_index.append(real_h_index)
                    if h_initial:
                        h_index = header.index(check_head)
                        real_h_index = header_initial_index[h_index]
                        
                        # dataframe.loc[real_h_index,
                        #                 'block_type'] = 'Header'
                        header_index.append(real_h_index)
                        h_initial = False
                else:
                    refrence_checker_header.append(False)

            for check_foot in footer:
                if check_foot in foot_:
                    refrence_checker_footer.append(True)
                    f_index = foot_.index(check_foot)
                    real_f_index = foot[f_index]
                    # dataframe.loc[real_f_index, 'block_type'] = 'Footer'
                    footer_index.append(real_f_index)
                    
                    if f_initial:
                        f_index = footer.index(check_foot)
                        real_f_index = footer_initial_index[f_index]
                        # dataframe.loc[real_f_index,
                        #                 'block_type'] = 'Footer'
                        footer_index.append(real_f_index)
                        
                        f_initial = False
                else:
                    refrence_checker_footer.append(False)
    dataframe.loc[page_number_index,'block_type'] = 'Page Number'
    if all(refrence_checker_header):
        dataframe.loc[header_index,'block_type'] = 'Header'
    if all(refrence_checker_footer):
        dataframe.loc[footer_index,'block_type'] = 'Footer'

    return dataframe

def dictionary_generator(**kwargs):
    return kwargs


def get_bbox_dict(bbox):
    return dict(bbox_left=bbox[0],
                bbox_top=bbox[1],
                bbox_right=bbox[2],
                bbox_bottom=bbox[3])


def excluder(row: pd.Series, exclude_list: list):
    """excluder 
    Function to be applied to filter dataframe before output gen

    Args:
        row (pd.Series): Row to check
        exclude_list (list): List of tags to exclude

    Returns:
        bool: Boolean if the row should be present in output or not
    """
    return row['block_type'] not in exclude_list


def filter_df(df: pd.DataFrame, exclude_list: list) -> pd.DataFrame:
    """filter_df 
    Filters dataframe for output generation

    Args:
        df (pd.DataFrame): Dataframe to filter
        exclude_list (list): List of tags to exclude

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    block_types_to_consider = df.apply(excluder, axis=1, exclude_list=exclude_list)
    df = df[block_types_to_consider]
    return df

def dataframe_to_dictionary_maker(block,*args):
    word_type = args[0]
    if word_type == 'Yes':
        data = {'Type': block['block_type']}
    else:
        data = {'Type': 'Word'}
    key=args[1]
    data['Text'] = block[key]
    data['BoundingBox'] = {
                    'Width':  block['bbox_right']-block['bbox_left'],
                    'Height': block['bbox_bottom']-block['bbox_top'],
                    'Left': block['bbox_left'],
                    'Top': block['bbox_top'],
                }
    if word_type == 'Yes':
        line = args[2]
        if line=='Yes':
            data['ID'] = f"page{block['page_no']}_block{block['block_no']}_line{block['line_no']}"
                # block['line_id']
        else:
            data['ID'] = f"page{block['page_no']}_block{block['block_no']}"
                # block['block_id']
        # data['Font Size'] = block['size']
        # data['Font Type'] = block['font_name']
        data['Child'] = block['child']
    else:
        data['ID'] = f"page{block['page_no']}_block{block['block_no']}_line{block['line_no']}_word{block['word_no']}"
    return data

def ord_unord_1(x: str) -> Union[float, str]:
    """ord_unord_1 
    Function which tests if a string is part of a ordered or unordered list

    Arguments:
        x {str} -- String to test

    Returns:
        Union[float, str] -- Returns string if the string is part of a list else nan
    """    
    negative_pattern1 = r"""
    ^               # Match at beginning of the string
    [0-9a-zA-Z]+    # Match alphanumeric characters one or more times
    \ +             # Match space one or more times
    """

    # for matching list like indications with open and close paranthesis
    # eg. (the one which got away), (the) xyaasdf, etc.
    negative_pattern2 = r"""
    ^               # Match at beginning of the string
    \(              # Open paranthesis
    .{4,}          # Any alpha numeric text
    \)              # Close parathesis
    """

    # ^                   # Match at beginning of the string
    # [0-9a-zA-z]{0,1}    # Match any alphanumeric character once
    # \({0,1}             # Match an open paranthesis character 0 or 1 time
    # (                   # Start group
    #     [0-9]{1,2}|     # 2 numbers or 
    #     [iIvVxX]{1,3}|  # three most used roman numeral characters in both cases(up and low) or
    #     [a-zA-Z]{1}     # for alphabet ordered list (a), (x) ...
    # )                   # End group
    # \){0,1}\.{1}\ +     # Match a close paranthesis character followed by '.' 1 time and followed by 1 or more space(s)
    # regex Explanation above

    positive_pattern1 = r"^[0-9a-zA-z]{0,1}\({0,1}([0-9]{1,2}|[iIvVxX]{1,3}|[a-zA-Z]{1})\){0,1}\.{0,1}\ +"
    
    # 1.1, 1.1.1.1 etc.
    positive_pattern4 = r"(?:\.\d{1,3}){0,4}"

    # positive_pattern1 = r"\((?={exp}\))|{exp}".format(exp=p1)

    # numex = r"""^(?:
    #     \d{1,3}                 # 1, 2, 3
    #         (?:\.\d{1,3}){0,4}  # 1.1, 1.1.1.1
    #     | [B-H] | [J-Z]         # A, B - Z caps at 26.
    #     | [AI](?!\s)            # Note: "A" and "I" can properly start non-lists
    #     | [a-z]                 # a - z
    #     | [ivxcl]{1,6}          # Roman ii, etc
    #     | [IVXCL]{1,6}          # Roman IV, etc.
    #     )
    #     """
    # positive_pattern1 = r'^\s*(\(?%s\)|%s\.?)\s+(.*)'% (numex, numex)


    # positive_pattern1 = r"""
    # ^                   # Match at beginning of the string
    # [0-9a-zA-z]{1,2}    # Match any alphanumeric character once or twice
    # \){0,1}             # Match an close paranthesis character 0 or 1 time
    # \.{1}               # Match a full stop once
    # \ +                 # Match a whitespace once
    # """

    # Matches unviewable unicode string patterns like \u2043 \u2044 ...
    positive_pattern2 = r"^\\uf[a-z0-9]{3}\ +"

    # Match at beginning of the string, below symbols which may come as bullets
    # unsupported chars(4), right sided arrows etc.
    # BULLET
    # HYPHEN
    # FIGURE DASH
    # NON-BREAKING HYPHEN
    # EN DASH
    # BLACK CIRCLE
    # BLACK SMALL SQUARE
    # BLACK DIAMOND MINUS WHITE X
    # HEAVY CHECK MARK

    positive_pattern3 = r"""^[•‐‒‑–●▪❖✔]{1,2}\ +"""

    # compile regexes with verbose syntax
    pve_pttrn = re.compile('|'.join([positive_pattern1, positive_pattern2, positive_pattern3]), re.X)

    neg_pttrn = re.compile('|'.join([negative_pattern1, negative_pattern2]), re.X)

    if neg_pttrn.match(x) is None and pve_pttrn.match(x):
        res = "Order/Unorder List"
    else:
        res = np.nan

    return res


def is_overlap(*ranges) -> bool:
    """Function to check overlap is present between two range objects"""
    ovr_lap = []
    if ranges:
        # Form a set from first range object
        first_range = set(ranges[0])

        # Form a set from other ranges by combining with chain and
        # find intersection between them

        ovr_lap = first_range.intersection(set(chain(*ranges[1:])))
    return bool(ovr_lap)

def range_inc_last(start: int, end: int, step: int = 1) -> range:
    """range_inc_last 
    Return range including the end number specified
    range_inc_last(1, 5) => range(1, 6)
    Arguments:
        start {int} -- Starting number
        end {int} -- ending number
        step {int} -- Optional step (default=1)

    Returns:
        range -- Range object including the end number
    """
    return range(start, end+1, step)

def get_pages_to_read(page_range_str: str) -> list:
    """get_pages_to_read
    Get page numbers as chain generator object
    from strings like '1-5,8-10,20-24'
    Arguments:
        page_range_str {str} -- String specifying page numbers
    Raises:
        IndexError: When there is an overlap with page numbers
    Returns:
        list -- Returns page numbers as a list
    >>> from utils.pdf_impl_utils import get_pages_to_read as gpr
    >>> gpr('1')
    [1]
    >>> gpr('1,2')
    [1, 2]
    >>> gpr('1,2,5')
    [1, 2, 5]
    >>> gpr('1-5, 6-10')
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    >>> gpr('1-5, 6-10, 20-25'))
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 21, 22, 23, 24, 25]
    >>> gpr('1,3,5, 10-15')
    [1, 3, 5, 10, 11, 12, 13, 14, 15]
    """
    range_seperator = '-'
    option_seperator = ','
    
    # Get the page ranges from the string by splitting if range_seperator in page_range_str else 
    pages = [
        # Use range if it has a range seperator
        range_inc_last(*[int(num) for num in rng.split(range_seperator)])
        if range_seperator in rng
        # or normally convert to int
        else int(rng)
        for rng in page_range_str.split(option_seperator)
    ]

    # Normal page numbers
    page_nos = [p for p in pages if not isinstance(p, range)]
    # Page ranges like 5-10, 6-40 etc.
    page_ranges = [p for p in pages if isinstance(p, range)]

    # Check overlap in range objects
    if is_overlap(*page_ranges):
        print("Page numbers are overlapping, Please check "
              "{range_str}".format(range_str=page_range_str))
    
    # Make a single iterable from all objects
    p_nos = list(chain(*page_ranges))
    p_nos.extend(page_nos)

    # Deduplicate and return
    return list(set(p_nos))

def page_range_checker(pagecount, page_range):
    for page in page_range:
        if page <= pagecount:
            pass_or_break = False
        else:
            pass_or_break = True
            break
    if pass_or_break:
        return False
    else:
        return True

def get_space_dist(words:list):
    words = sorted(words,key=itemgetter(1,0))
    length = len(words)
    choices_words = random.choices(words,k=10)
    calc = []
    for choice in choices_words:
        index_1 = words.index(choice)
        #checking the index present in the list
        if index_1+1 < length:
            calc.append((index_1,index_1+1))
    dist=[]
    for i in calc:
        ele_1 = words[i[0]]
        ele_2 = words[i[1]]
        if ele_1[1]==ele_2[1]:
            dist.append(ele_1[3]-ele_2[1])
    return mean(dist)


def block_merge_determiner(previous_block, current_block,width,height):
    threshold_width = 2.5*width
    threshold_height = 2.5*height
    prev_y2 = previous_block[3]
    prev_x2 = previous_block[2]
    curr_y1 = current_block[1]
    curr_x1 = current_block[0]
    vertical_difference = curr_y1 - prev_y2
    horizontal_difference = curr_x1 - prev_x2
    # print(prev_y2,curr_y1,vertical_difference,horizontal_difference)
    if (vertical_difference <= threshold_height) and (horizontal_difference <= threshold_width) :
        return True
    else:
        return False

def assign_neccesary_columns_merge(df,df_type='block'):
    df = df.assign(bbox_left_merge=np.nan)
    df = df.assign(bbox_top_merge=np.nan)
    df = df.assign(bbox_right_merge=np.nan)
    df = df.assign(bbox_bottom_merge=np.nan)
    df = df.assign(size_merge=np.nan)
    df = df.astype({'size_merge':'string'})
    df = df.assign(text_merge=np.nan)
    df = df.assign(font_name_merge=np.nan)
    df = df.astype({'font_name_merge':'string'})
    df = df.assign(block_no_merge=np.nan)
    if df_type=='line':
        df = df.assign(line_no_merge=np.nan)
    elif df_type=='word':
        df = df.assign(line_no_merge=np.nan)
        df = df.assign(word_no_merge=np.nan)
    return df


def block_mergerer_2(block : pd.DataFrame,
                   line : pd.DataFrame,
                   word : pd.DataFrame,width,height):
    block = block.sort_values(by=['bbox_top', 'bbox_left'])
    block.reset_index(inplace=True,drop=True)

    block = assign_neccesary_columns_merge(block)
    line = assign_neccesary_columns_merge(line, df_type='line')
    word = assign_neccesary_columns_merge(word, df_type='word')

    for index,row in block.iterrows():
        if index==0:
            prev_index = index
            prev_block = (row['bbox_left'],
                        row['bbox_top'],
                        row['bbox_right'],
                        row['bbox_bottom'])
        else:
            curr_index = index
            curr_block = (row['bbox_left'],
                        row['bbox_top'],
                        row['bbox_right'],
                        row['bbox_bottom'])
            if block_merge_determiner(prev_block,curr_block,width,height):

                curr_block_no = row['block_no']
                prev_block_no = block.loc[prev_index,'block_no']
                
                #lets update coordinates
                left = min(block.loc[prev_index,'bbox_left'],row['bbox_left'])
                top = min(block.loc[prev_index,'bbox_top'],row['bbox_top'])
                right = max(block.loc[prev_index,'bbox_right'],row['bbox_right'])
                bottom = max(block.loc[prev_index,'bbox_bottom'],row['bbox_bottom'])
                block.loc[prev_index,'bbox_left_merge'] = left
                block.loc[prev_index,'bbox_top_merge'] = top
                block.loc[prev_index,'bbox_right_merge'] = right
                block.loc[prev_index,'bbox_bottom_merge'] = bottom
                
                #lets update the size
                size = block.loc[prev_index,'size']
                size.extend(row['size'])
                block.at[prev_index,'size_merge'] = str(size)
                
                #lets update the text
                block.loc[prev_index,'text_merge'] = f"{block.loc[prev_index,'text']} {row['text']}"
                
                #lets update the font_name
                font = block.loc[prev_index,'font_name']
                font.extend(row['font_name'])
                block.at[prev_index,'font_name_merge'] = str(font)
                
                #finally drop the row from block

                # block.drop(index=curr_index, inplace = True)
                
                #lets update the same in line and word dataframe
                
                indexes_line = list(line[line['block_no']==curr_block_no].index)
                indexes_word = list(word[word['block_no']==curr_block_no].index)

                maximum_line = line[line['block_no']==prev_block_no].max(axis=0)['line_no']
                maximum_word = word[word['block_no']==prev_block_no].max(axis=0)['word_no']
                
                line.loc[indexes_line,'line_no_merge'] = maximum_line + 1 + line['line_no']
                word.loc[indexes_word,'line_no_merge'] = maximum_line + 1 + word['line_no']
                word.loc[indexes_word,'word_no_merge'] = maximum_word + 1 + word['word_no']

                line.loc[indexes_line,'block_no_merge'] = prev_block_no
                word.loc[indexes_word,'block_no_merge'] = prev_block_no

                prev_block = (left, top, right, bottom)
            else:
                prev_index = curr_index
                prev_block = curr_block
    block.to_csv('block_test.csv',index=False)
    line.to_csv('line_test.csv',index=False)
    word.to_csv('word_test.csv',index=False)
    return block, line, word

def pdf_cordinates_scalaing(width,height):
    our_cordinates_width = 595
    our_cordinates_height = 842
    width_ = width/our_cordinates_width
    height_ = height/our_cordinates_height
    return width_,height_


def split_determiner(df):
    initial = True
    ind_list= deque()
    for ind,row in df.iterrows():
        if initial:
            initial=False
            if type(row['font_name']) == list:
                prev_size = row['size']
                prev_font_name = row['font_name']
            else:
                prev_size = ast.literal_eval(row['size'])
                prev_font_name = ast.literal_eval(row['font_name'])
            prev_line = row['line']
            ind_list.append(ind)
        else:
            if type(row['font_name']) == list:
                curr_size = row['size']
                curr_font_name = row['font_name']
            else:
                curr_size = ast.literal_eval(row['size'])
                curr_font_name = ast.literal_eval(row['font_name'])
            curr_line = row['line']

            if prev_font_name==curr_font_name:
                ind_list.append(ind)

            elif all([prev_size!=curr_size,prev_font_name!=curr_font_name]):
                if (len(prev_font_name)==1) and (len(list(filter(lambda x: 'bold' in x.lower(),prev_font_name)))>=1):
                    return True,ind_list

                elif len(list(filter(lambda x: 'bold' in x.lower(),prev_font_name)))>=1 and 'bold' in prev_font_name[0].lower() \
                                and ':' in prev_line.lower():
                    return True,ind_list

                elif  len(prev_size)>=1 and ':' in prev_line.lower():
                    if len(set(prev_size))>=2:
                        prev_set_size = sorted(set(prev_size),reverse=True)
                        if prev_size[0]==prev_set_size[0]:
                            return True,ind_list

                elif len(set(prev_size))>=1:
                    prev_set_size = sorted(set(prev_size),reverse=True)
                    if prev_set_size[0] > sorted(curr_size,reverse=True)[0]:
                         return True,ind_list
            elif prev_font_name!=curr_font_name and (len(list(filter(lambda x: 'bold' in x.lower(),prev_font_name)))>=1):
                return True,ind_list

            prev_line = curr_line
            prev_size = curr_size
            prev_font_name = curr_font_name
    return False,None


def block_spliter(block : pd.DataFrame,
                line : pd.DataFrame,
                word : pd.DataFrame,width,height):

    block = block.sort_values(by=['bbox_top', 'bbox_left'])
    block.reset_index(inplace=True,drop=True)
    # aim is to see whether if a complete line cotains one kinda font
    line = line.sort_values(by=['bbox_top', 'bbox_left'])
    line.reset_index(inplace=True,drop=True)

    line_group = line.groupby(by=['block_no'])
    block_counter = -1
    block_index_list = []
    block_data = []
    for group_no , group_df in line_group:
        decider,index_list = split_determiner(group_df)
        if decider:
            # design block bbox coordinates
            #split bbox cordinates
            bbox_left = min(line.loc[index_list,'bbox_left'])
            bbox_top = min(line.loc[index_list,'bbox_top'])
            bbox_right = max(line.loc[index_list,'bbox_right'])
            bbox_bottom = max(line.loc[index_list,'bbox_bottom'])
            ########### WORK AROUND HERE FOR CHANGES

            #other split bbox coordinates right and bottom is same so working on left and top
            
            block_index = block[(block['block_no']==group_no)].index
            block_index_list.append(block_index)
            left_bbox_block = bbox_left
            top_bbox_block = bbox_bottom + (1*height)
            text = block.loc[block_index,'text'].values.tolist()[0].split('|||') #.str.split('|||')

            # print('$$$$$$$$',text)
            data = {
                'page_no': line.at[0,'page_no'],
                'block_no': block_counter,
                'text': ' '.join(text[:len(index_list)]),
                'size' : block.loc[block_index,'size'].values.tolist()[0][:len(index_list)],
                'font_name' : block.loc[block_index,'font_name'].values.tolist()[0][:len(index_list)],
                'bbox_left':bbox_left,
                'bbox_top':bbox_top,
                'bbox_right': bbox_right,
                'bbox_bottom': bbox_bottom
            }
            
            #update other block info in block df
            try:
                size_ = block.loc[block_index,'size'].values.tolist()[0][len(index_list):]
                font_ = block.loc[block_index,'font_name'].values.tolist()[0][len(index_list):]
            except Exception:
                size_ = block.loc[block_index,'size']
                font_ = block.loc[block_index,'font_name']
            data_2 = {
                'page_no': line.at[0,'page_no'],
                'block_no': block.loc[block_index,'block_no'].values.tolist()[0],
                'text': ' '.join(text[len(index_list):]),
                'size' : size_,
                'font_name' : font_,
                'bbox_left':left_bbox_block,
                'bbox_top':top_bbox_block,
                'bbox_right': block.loc[block_index,'bbox_right'].values.tolist()[0],
                'bbox_bottom': block.loc[block_index,'bbox_bottom'].values.tolist()[0]
            }
            #append new block to block df
            block_data.append(data)
            block_data.append(data_2)
            
            ###########
            #rename the block_no in line dataframe
            line.loc[index_list,'block_no'] = block_counter
            
            #get the line numbers from dataframe
            line_no_ = deque(line.loc[index_list,'line_no'])
            # update the block number in words
            for _line_ in line_no_:
                word_index = deque(word[(word['block_no']==group_no) & (word['line_no']==_line_)].index)
                word.loc[word_index,'block_no'] = block_counter
            # increment the block counter    
            block_counter -= 1
            block.drop(index=block_index, inplace = True)
    
    df = pd.DataFrame(block_data)
    block = block.append(df,ignore_index=True)

    block.to_csv('block_aegon_2.csv',index=False)
    line.to_csv('line_aegon_2.csv',index=False)
    word.to_csv('word_aegon_2.csv',index=False)     
            
    return block, line, word



def block_mergerer(block : pd.DataFrame,
                   line : pd.DataFrame,
                   word : pd.DataFrame,width,height):
    block = block.sort_values(by=['bbox_top', 'bbox_left'])
    block.reset_index(inplace=True,drop=True)

    # block = assign_neccesary_columns_merge(block)
    # line = assign_neccesary_columns_merge(line, df_type='line')
    # word = assign_neccesary_columns_merge(word, df_type='word')

    for index,row in block.iterrows():
        if index==0:
            prev_index = index
            prev_block = (row['bbox_left'],
                        row['bbox_top'],
                        row['bbox_right'],
                        row['bbox_bottom'])
        else:
            curr_index = index
            curr_block = (row['bbox_left'],
                        row['bbox_top'],
                        row['bbox_right'],
                        row['bbox_bottom'])
            if block_merge_determiner(prev_block,curr_block,width,height):

                curr_block_no = row['block_no']
                prev_block_no = block.loc[prev_index,'block_no']
                
                #lets update coordinates
                left = min(block.loc[prev_index,'bbox_left'],row['bbox_left'])
                top = min(block.loc[prev_index,'bbox_top'],row['bbox_top'])
                right = max(block.loc[prev_index,'bbox_right'],row['bbox_right'])
                bottom = max(block.loc[prev_index,'bbox_bottom'],row['bbox_bottom'])
                block.loc[prev_index,'bbox_left'] = left
                block.loc[prev_index,'bbox_top'] = top
                block.loc[prev_index,'bbox_right'] = right
                block.loc[prev_index,'bbox_bottom'] = bottom
                
                #lets update the size
                size = block.loc[prev_index,'size']
                size.extend(row['size'])
                block.at[prev_index,'size'] = size 
                
                #lets update the text
                block.loc[prev_index,'text'] = f"{block.loc[prev_index,'text']}|||{row['text']}"
                
                #lets update the font_name
                font = block.loc[prev_index,'font_name']
                font.extend(row['font_name'])
                block.at[prev_index,'font_name'] = font
                
                #finally drop the row from block
                block.drop(index=curr_index, inplace = True)
                
                #lets update the same in line and word dataframe
                
                indexes_line = list(line[line['block_no']==curr_block_no].index)
                indexes_word = list(word[word['block_no']==curr_block_no].index)

                maximum_line = line[line['block_no']==prev_block_no].max(axis=0)['line_no']
                maximum_word = word[word['block_no']==prev_block_no].max(axis=0)['word_no']
                
                line.loc[indexes_line,'line_no'] = maximum_line + 1 + line['line_no']
                word.loc[indexes_word,'line_no'] = maximum_line + 1 + word['line_no']
                word.loc[indexes_word,'word_no'] = maximum_word + 1 + word['word_no']

                line.loc[indexes_line,'block_no'] = prev_block_no
                word.loc[indexes_word,'block_no'] = prev_block_no

                prev_block = (left, top, right, bottom)
            else:
                prev_index = curr_index
                prev_block = curr_block
    block.to_csv('block_voda.csv',index=False)
    line.to_csv('line_voda.csv',index=False)
    word.to_csv('word_voda.csv',index=False)
    return block, line, word
