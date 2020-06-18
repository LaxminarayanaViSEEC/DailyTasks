import json

def number_of_columns_calculator(data,child):
    blocks = data['Blocks']
    children = child['Child']
    column_counter = 0
    for child_ in children:
        child_list = list(filter(lambda x: (x['Id']==child_),blocks))
        for row in child_list:
            if row['RowId']==0:
                column_counter+=1
    return column_counter


#lets calculate the vertical distance
def vertical_distance(table_data):
    new_table_data =[]
    initial = True
    second_initial = True
    for data in table_data:
        if initial:
            initial = False
            prev_data = data
        else:
            curr_data = data
            prev = prev_data["BoundingBox"]["Top"]+prev_data["BoundingBox"]["Height"]
            curr = curr_data["BoundingBox"]["Top"]
            distance = curr - prev
            if distance <= 60:
                if second_initial:
                    second_initial = False
                    new_table_data.append(prev_data)
                    new_table_data.append(curr_data)
                else:
                    new_table_data.append(curr_data)
            prev_data = curr_data
    return new_table_data


def checking_horizontal_overlap(cords_1, cords_2):
    # loading the cordinates to variables
    left_1 = cords_1['Left']
    top_1 = cords_1['Top']
    right_1 = cords_1['Left'] + cords_1['Width']
    bottom_1 = cords_1['Top'] + cords_1['Height']
    width_1 = cords_1['Width']
    width_2 = cords_2['Width']
    left_2 = cords_2['Left']
    top_2 = cords_2['Top']
    right_2 = cords_2['Left'] + cords_2['Width']
    bottom_2 = cords_2['Top'] + cords_2['Height']
    
    threshold_width_1 = width_1 * 0.9
    threshold_width_2 = width_2 * 0.9
    
    #conditions for horizontal merge
    # condition-1 exact same x coordinates
    if (left_1 == left_2) and (right_1 == right_2):
        return True
    #Condition-2 widths are almost similar
    elif (width_1 >= threshold_width_2) or (width_2 >= threshold_width_1):
        return True
    #condition-3 they are truley horizonatal overlap
    elif (right_2 >= left_1 and bottom_2 >= top_1) or (right_1 >= left_2 and bottom_1 >= top_2):
        return True
    #no condition met so return "No Overlap"
    else:
        return False



def table_merger(data):
    table_child = list(filter(lambda x:(x['Type']=='Table'),data['Blocks']))
    table_child = sorted(table_child,key=lambda x :(x['BoundingBox']['Top'],x['BoundingBox']['Left']))
    
    table_child = vertical_distance(table_child)

    table_json = None
    cell_json = None
    ids_to_delete = []
    prev = None

    for block in table_child:
        if prev == None:
            prev = block
            prev_ = block
            # calculate the total number of columns
            prev_cols = number_of_columns_calculator(data,prev)
            row_no = 0 
        else:
            curr = block

            # check for horizontal overlap
            if checking_horizontal_overlap(prev_['BoundingBox'],curr['BoundingBox']):
                prev_ = curr
                # check for total number of columns
                curr_cols = number_of_columns_calculator(data,curr)
                if prev_cols == curr_cols:
                    row_no += 1
                    # merge the blocks
                    if table_json==None:  
                        cell_json = []
                        for cell in prev['Child']:
                            cell_json.extend(list(filter(lambda x:(x['Id']==cell),data['Blocks'])))

                        prev['Child'].extend(curr['Child'])
                        ids_to_delete.append(prev['Id'])
                        ids_to_delete.extend(prev['Child'])
                        table_json = {
                            'Id': prev['Id'],
                            'BoundingBox':{
                                'Left': min(prev['BoundingBox']['Left'],curr['BoundingBox']['Left']),
                                'Top' : min(prev['BoundingBox']['Top'],curr['BoundingBox']['Top']),
                                'Right': max(prev['BoundingBox']['Left']+prev['BoundingBox']['Width'],
                                             curr['BoundingBox']['Left']+curr['BoundingBox']['Width']),
                                'Bottom' : max(prev['BoundingBox']['Top']+prev['BoundingBox']['Height'],
                                               curr['BoundingBox']['Top']+curr['BoundingBox']['Height'])
                            },
                            'Type' : 'Table',
                            'Child' : prev['Child']
                                     }
                        ids_to_delete.append(curr['Id'])
                        # have to update the cell level row numbers
                        curr_cells=[]
                        for cell in curr['Child']:
                            curr_cells.extend(list(filter(lambda x:(x['Id']==cell),data['Blocks'])))
                        for cell in curr_cells:
                            cell['RowId'] = row_no
                            cell_json.append(cell)
                            ids_to_delete.append(cell['Id'])
                        prev = table_json
                    else:
                        prev['Child'].extend(curr['Child'])
                        ids_to_delete.append(curr['Id'])
                        table_json['BoundingBox']={
                                'Left': min(prev['BoundingBox']['Left'],curr['BoundingBox']['Left']),
                                'Top' : min(prev['BoundingBox']['Top'],curr['BoundingBox']['Top']),
                                'Right': max(prev['BoundingBox']['Right'],
                                             curr['BoundingBox']['Left']+curr['BoundingBox']['Width']),
                                'Bottom' : max(prev['BoundingBox']['Right'],
                                               curr['BoundingBox']['Top']+curr['BoundingBox']['Height'])
                            }
                        table_json['Child'] = prev['Child']
                        curr_cells=[]
                        for cell in curr['Child']:
                            curr_cells.extend(list(filter(lambda x:(x['Id']==cell),data['Blocks'])))
                        for cell in curr_cells:
                            cell['RowId'] = row_no
                            cell_json.append(cell)
                            ids_to_delete.append(cell['Id'])
                        prev = table_json

    #update table_json Bounding box
    bbox = table_json['BoundingBox']
    new_bbox = {'Left':bbox['Left'],
               'Top':bbox['Top'],
               'Width':bbox['Right']-bbox['Left'],
               'Height':bbox['Bottom']-bbox['Top']}
    table_json['BoundingBox'] = new_bbox

    #delete the ids in 
    final_blocks = [table_json]
    final_blocks.extend(cell_json)
    for bloc in data['Blocks']:
        if bloc['Id'] not in ids_to_delete:
            final_blocks.append(bloc)
        else:
            pass
    return final_blocks


if __name__=='__main__':
    path = r'D:\iDX\images and jsons\813b12e8-7d2f-4245-aeca-7395bb3c41a1-1.json'

    with open(path, mode = 'r') as file_:
        data=json.load(file_)
    final = table_merger(data)
    data['Blocks'] = final
    with open('newjson.json',mode = 'w') as file_:
        json.dump(data,file_)
