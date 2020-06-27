""" Utilities for table detection and extraction"""


def in_table_area(table_bbox: tuple, block_bbox: tuple):
    """in_table_area 
    Check if a rectangle region of text block is inside a table region

    Arguments:
        table_bbox {tuple} -- Table rectangle coordinates
        block_bbox {tuple} -- block region coordinates

    Returns:
        bool -- True if the block is inside the table rectangle else False
    """

    t_left, t_top, t_rgt, t_bot = table_bbox
    b_left, b_top, b_rgt, b_bot = block_bbox

    # Check if the rectangular shape of bbox from reader
    # is inside the table region detected by tabula
    return all((
        t_left < b_left,
        t_top < b_top,
        t_rgt > b_rgt,
        t_bot > b_bot
    ))

def check_table_area(row, table_bboxes: list):
    # function to facilitate applying table region check to word dataframe
    check_bbox = row['bbox_left'], row['bbox_top'], row['bbox_right'], row['bbox_bottom']
    return not any([in_table_area(t_bbox, check_bbox) for t_bbox in table_bboxes])