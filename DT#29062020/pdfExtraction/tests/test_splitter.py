import unittest
import pandas as pd 
from collections import deque
import ast

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

class TestSplitter(unittest.TestCase):

    def test_split(self):
        data =[
            {'line' : 'AEGON N.V.','size' : [11.039999961853027],
            'font_name' : ['Times New Roman,Bold']},

            {'line' : '(incorporated with limited liability in The Netherlands',
            'size' : [11.039999961853027, 11.039999961853027],
            'font_name' : ['Times New Roman', 'Times New Roman,Italic']}
        ]
        df = pd.DataFrame(data)
        x,y = split_determiner(df)
        self.assertEqual((x,y),(True,deque([0])))
    
    def test_split_2(self):
        data =[
            {'line' : 'AEGON FUNDING COMPANY LLC','size' : [12.039999961853027],
            'font_name' : ['Times New Roman']},
            {'line' : '(organised under the laws of the State of Delaware, USA,','size' : [11.039999961853027, 11.039999961853027],
            'font_name' : ['Times New Roman', 'Times New Roman,Italic']}
        ]
        df = pd.DataFrame(data)
        x,y = split_determiner(df)
        self.assertEqual((x,y),(True,deque([0])))

    def test_split_3(self):
        data =[
            {'line' : 'Emerging: Technologies are more','size' : [11.039999961853027,10.0],
            'font_name' : ['Times New Roman,Bold','Times New Roman']},
            {'line' : 'organised under the laws of the State of Delaware, USA,','size' : [11.039999961853027, 11.039999961853027],
            'font_name' : ['Times New Roman', 'Times New Roman,Italic']}
        ]
        df = pd.DataFrame(data)
        x,y = split_determiner(df)
        self.assertEqual((x,y),(True,deque([0])))

    def test_split_4(self):
        data =[
            {'line' : 'Emerging: Technologies are more','size' : [11.039999961853027,10.0],
            'font_name' : ['Times New Roman,','Times New Roman']},
            {'line' : 'organised under the laws of the State of Delaware, USA,','size' : [11.039999961853027, 11.039999961853027],
            'font_name' : ['Times New Roman', 'Times New Roman,Italic']}
        ]
        df = pd.DataFrame(data)
        x,y = split_determiner(df)
        self.assertEqual((x,y),(True,deque([0])))

    def test_split_5(self):
        data =[
            {'line' : 'AEGON N.V.','size' : [12.039999961853027],
            'font_name' : ['Times New Roman,Bold']},

            {'line' : '(incorporated with limited liability in The Netherlands',
            'size' : [10.039999961853027, 10.039999961853027],
            'font_name' : ['Times New Roman', 'Times New Roman,Italic']}
        ]
        df = pd.DataFrame(data)
        x,y = split_determiner(df)
        self.assertEqual((x,y),(True,deque([0])))
    
    def test_split_6(self):
        data =[
            {'line' : 'AEGON FUNDING COMPANY LLC','size' : [13.039999961853027],
            'font_name' : ['Times New Roman']},
            {'line' : '(organised under the laws of the State of Delaware, USA,','size' : [11.039999961853027, 11.039999961853027],
            'font_name' : ['Times New Roman', 'Times New Roman,Italic']}
        ]
        df = pd.DataFrame(data)
        x,y = split_determiner(df)
        self.assertEqual((x,y),(True,deque([0])))

    def test_split_7(self):
        data =[
            {'line' : 'Emerging: Technologies are more','size' : [12.039999961853027,11.039999961853027],
            'font_name' : ['Times New Roman,Bold','Times New Roman']},
            {'line' : 'organised under the laws of the State of Delaware, USA,','size' : [11.039999961853027, 11.039999961853027],
            'font_name' : ['Times New Roman', 'Times New Roman,Italic']}
        ]
        df = pd.DataFrame(data)
        x,y = split_determiner(df)
        self.assertEqual((x,y),(True,deque([0])))

    def test_split_8(self):
        data =[
            {'line' : 'Emerging: Technologies are more','size' : [13.039999961853027,10.0],
            'font_name' : ['Times New Roman,','Times New Roman']},
            {'line' : 'organised under the laws of the State of Delaware, USA,','size' : [11.039999961853027, 11.039999961853027],
            'font_name' : ['Times New Roman', 'Times New Roman,Italic']}
        ]
        df = pd.DataFrame(data)
        x,y = split_determiner(df)
        self.assertEqual((x,y),(True,deque([0])))
    
if __name__=='__main__':
    unittest.main()