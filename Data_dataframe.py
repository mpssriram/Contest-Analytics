import pandas as pd 
from URLextract import Get_data as gd



class Dataframe_former():
    def __init__(self,handle = ""):
        self.handle = handle

    def json_dataframe(self):

        df = pd.read_json(S1.user_info())
        df1 = pd.DataFrame(S1.user_submissions())
        df = pd.concat([df,df1],axis = 1)
        df.fillna(0,inplace=True)

        return df
    

    

if __name__ == '__main__':
    inputer = input()
    S2 = Dataframe_former(inputer)
    S1 = gd(inputer)

    print(S2.json_dataframe())
                          
    