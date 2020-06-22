
def inside_justifier(bbox_1:dict, bbox_2:dict):

    """
    Returns True if bbox_2 is inside bbox_1
    bbox_1 input format is dictionary
    bbox_1 = {'Left':0,
            'Top':0,
            'Width':10,
            'Height':10}
    bbox_2 is same as bbox_1
    """

    bbox_1_left = bbox_1['Left']
    bbox_1_top = bbox_1['Top']
    bbox_1_right = bbox_1['Left'] + bbox_1['Width']
    bbox_1_bottom = bbox_1['Top'] + bbox_1['Height']
    
    bbox_2_left = bbox_2['Left']
    bbox_2_top = bbox_2['Top']
    bbox_2_right = bbox_2['Left'] + bbox_2['Width']
    bbox_2_bottom = bbox_2['Top'] + bbox_2['Height']
    
    if (bbox_1_left <= bbox_2_left) and (bbox_1_top <= bbox_2_top):
        if (bbox_1_right >= bbox_2_right) and (bbox_1_bottom >= bbox_2_bottom):
            return True
    return False


