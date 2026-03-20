import requests
import json




class Get_data():
    def __init__(self,handles):
        self.handle = handles

    def user_info(self):
        API_URL = f"https://codeforces.com/api/user.info?handles={self.handle}"

        response = requests.get(API_URL, timeout=30)
        if response.status_code == 200:
            handle_data = response.json()
            with open(f"{handle}.json", "w", encoding="utf-8") as f:
                json.dump(handle_data, f, indent=4)
            
            return f"Success! Data saved to '{handle}.json'"
        else:
            return f"Failed to fetch data. Status code: {response.status_code}",response.text
    
    def user_submissions(self):
        API_URL = f"https://codeforces.com/api/user.status?handle={self.handle}"

        response = requests.get(API_URL, timeout=30)
        if response.status_code == 200:
            handle_data = response.json()
            if handle_data['status'] == 'OK':
                submissions = handle_data['result']
                unique_questions = []
                for i in submissions:
                    if i['verdict'] == 'OK':
                        values = str(i['problem']['contestId']) + i['problem']['index']
                        unique_questions.append(values)
                    
                unique_questions = list(set(unique_questions))
                return unique_questions


        else:
            return f"Failed to fetch data. Status code: {response.status_code}",response.text

            


if __name__ == "__main__":
    handle = input()

    S1 = Get_data(handles=handle)
    print(S1.user_info())
    print(S1.user_submissions())
    

