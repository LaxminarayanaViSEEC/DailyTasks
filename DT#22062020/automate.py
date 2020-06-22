import requests
import json
import os
import pandas as pd

def automate_function(file_name,
                      url_split='http://localhost:9082/idxocr/split-pdf',
                     url_file = 'http://localhost:9082/idxocr/find-table-structure'):
    
    df = []

    split_data = {"file_path": file_name}
    req = requests.post(url_split,data=json.dumps(split_data))
    req = json.loads(req.text)
    paths =[path['dest_path'] for path in req['paths']]

    for path in paths:
        file_data = {"file_path" : path}
        file_req = requests.post(url_file, data=json.dumps(file_data))
        df.append({'file_path':path, 'status_code':file_req.status_code})
        if file_req.status_code == 200:
            print(f'Status 200 for {file_name} in path ===> {path}')
        else:
            print(f'Error occured in {file_name} in path ===> {path}')
    print(df)
    return df

def path_parser(path_):

    df_ = []
    paths = os.listdir(path_)
    for _path_ in paths:
        if os.path.splitext(_path_)[1]== '.pdf':
            print(f'sending file {_path_} for request')
            df_.extend(automate_function(_path_))
            df = pd.DataFrame(df_,columns = ['file_path','status_code'])
            df.to_csv('test_results.csv',index=False)
    df = pd.DataFrame(df_,columns = ['file_path','status_code'])
    df.to_csv('test_results.csv',index=False)

if __name__ == '__main__':
    path_parser('D:\\iDX_UNS\\idx_unstructured\\src\\outputs')