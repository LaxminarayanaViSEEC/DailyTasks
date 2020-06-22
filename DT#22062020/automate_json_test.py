import json
import os
import pandas as pd

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


def table_data_validator(blocks):
    empty_cell_ids = []
    empty_sent_ids = []
    empty_word_ids = []
    cell_inside_table = []
    sent_inside_cell = []
    word_inside_sent=[]
    table_blocks = list(filter(lambda x : x['Type']=='Table',blocks))
    
    if len(table_blocks) >= 1:
        tables_found= True
        print('Tables Present!!')
        
        for t_block in table_blocks:
            child_list = t_block['Child']
            t_bbox = t_block['BoundingBox']
            
            for child in child_list:
                cell_filter = list(filter(lambda x:x['Id']==child, blocks))
                
                if len(cell_filter)>=1:
                    print('cell present!')
                    
                    for cell in cell_filter:
                        cell_child = cell['Child']
                        cell_bbox = cell['BoundingBox']
                        
                        if inside_justifier(t_bbox,cell_bbox):
                            for cell_id in cell_child:
                                sent = list(filter(lambda x:x['Id']==cell_id,blocks))

                                if len(sent) >= 1:
                                    print('Sentence present!!')

                                    for sentence in sent:
                                        sent_childs = sentence['Segments']
                                        sent_bbox = sentence['BoundingBox']
                                        if inside_justifier(cell_bbox,sent_bbox):
                                            
                                            for word_id in sent_childs:
                                                words = list(filter(lambda x:x['Id']==word_id,blocks))

                                                if len(words) >= 1:
                                                    print('words present!')
                                                    for word in words:
                                                        word_bbox = word['BoundingBox']
                                                        if inside_justifier(sent_bbox,word_bbox):
                                                            pass
                                                        else:
                                                            word_inside_sent.append(sentence)
                                                            print('%%%%%% Not inside!!',sentence)

                                                else:
                                                    empty_word_ids.append(word_id)
                                                    print('######### No words related!!',word_id)
                                        else:
                                            sent_inside_cell.append(cell_id)
                                            print('%%%%%% Not inside!!',cell_id)
                                else:
                                    empty_sent_ids.append(cell_id)
                                    print('######### No Sentences Found!!',cell_id)
                        else:
                            cell_inside_table.append(cell_child)
                            print('%%%%%% Not inside!!',cell_child)
                else:
                    empty_cell_ids.append(child)
                    print('######## No Cells Found!!',child)
    else:
        tables_found = False
        print('$$$$$$$$$$$ No Tables Found!!')
    if (len(cell_inside_table)<=0):
        cell_inside_tab =True
    else:
        cell_inside_tab = False
    if (len(sent_inside_cell)<=0):
        sent_inside_ce = True
    else:
        sent_inside_ce = False
    if (len(word_inside_sent)<=0):
        words_inside = True
    else:
        words_inside = False
    return tables_found,empty_cell_ids,empty_sent_ids,empty_word_ids,cell_inside_tab,sent_inside_ce,words_inside


def main_func(path):

    df = []

    for file_path in os.listdir(path):
        path_ = os.path.splitext(file_path)[0]
        sub_path = os.path.join(path,path_)
        for internal in os.listdir(sub_path):
            
            if os.path.splitext(internal)[1]=='.json': 
                print(os.path.join(sub_path,internal))
                with open(os.path.join(sub_path,internal),'r') as file_:
                    j = json.load(file_)['Blocks']
                    json_name = os.path.join(path_,internal)
                    try:
                        a,b,c,d,e,f,g = table_data_validator(j)
                        df.append({'JSON File Name':json_name,
                                    'Tables Found':a,
                                    'Empty cell ids':b,
                                    'Empty sent ids':c,
                                    'Empty word ids':d,
                                    'cell inside table':e,
                                    'sent inside cell':f,
                                    'words inside sent':g})
                    except:
                        df.append({'JSON File Name':json_name,
                                    'Tables Found':'ERROR',
                                    'Empty cell ids':'ERROR',
                                    'Empty sent ids':'ERROR',
                                    'Empty word ids':'ERROR',
                                    'cell inside table':'ERROR',
                                    'sent inside cell':'ERROR',
                                    'words inside sent':'ERROR'})
    return df

if __name__ == '__main__':
    path = "D:\\iDX_UNS\\idx_unstructured\\src\\outputs"
    df = main_func(path)
    df = pd.DataFrame(df)
    df.to_csv('automate_json_results.csv',index=False)