import requests
import json


class Get_data:
    def __init__(self, handles):
        self.handle = handles

    def user_info(self):
        API_URL = f"https://codeforces.com/api/user.info?handles={self.handle}"
        response = requests.get(API_URL, timeout=30)

        if response.status_code == 200:
            handle_data = response.json()
            if handle_data['status'] == 'OK':
                with open(f"{self.handle}.json", "w", encoding="utf-8") as f:
                    json.dump(handle_data['result'], f, indent=4)
                return f"{self.handle}.json"
        else:
            return f"Failed to fetch data. Status code: {response.status_code}", response.text
    
    def user_data_set(self):
        API_URL = f"https://codeforces.com/api/user.status?handle={self.handle}"
        response = requests.get(API_URL, timeout=30)

        if response.status_code == 200:
            handle_data = response.json()
            if handle_data['status'] == 'OK':
                with open(f"{self.handle}.json", "w", encoding="utf-8") as f:
                    json.dump(handle_data['result'], f, indent=4)
                return f"{self.handle}.json"
        else:
            return f"Failed to fetch data. Status code: {response.status_code}", response.text


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
                        value = str(i['problem']['contestId']) + i['problem']['index']
                        if value not in unique_questions:
                            unique_questions.append(value)

                return unique_questions
        else:
            return f"Failed to fetch data. Status code: {response.status_code}", response.text

    def question_tags(self):
        API_URL = f"https://codeforces.com/api/user.status?handle={self.handle}"
        response = requests.get(API_URL, timeout=30)

        if response.status_code == 200:
            handle_data = response.json()
            if handle_data['status'] == 'OK':
                submissions = handle_data['result']
                question_to_tags = {}

                for i in submissions:
                    if i['verdict'] == 'OK':
                        qname = str(i['problem']['contestId']) + i['problem']['index']
                        tags = i['problem']['tags']

                        if qname not in question_to_tags:
                            question_to_tags[qname] = tags

                unique_questions = list(question_to_tags.keys())
                unique_tags = list(question_to_tags.values())

                return unique_questions, unique_tags

        else:
            return f"Failed to fetch data. Status code: {response.status_code}", response.text
        
    def unsolved_questions():
        API_URL = f"https://codeforces.com/api/user.status?handle={self.handle}"
        response = requests.get(API_URL, timeout=30)

        if response.status_code == 200:
            handle_data = response.json()
            if handle_data['status'] == 'OK':
                submissions = handle_data['result']
                unique_questions = []

                for i in submissions:
                    
                    value = str(i['problem']['contestId']) + i['problem']['index']
                    if value not in unique_questions:
                        unique_questions.append(value)

                


                
                return unique_questions
        else:
            return f"Failed to fetch data. Status code: {response.status_code}", response.text




if __name__ == "__main__":
    handle = input()
    S1 = Get_data(handles=handle)
    print(S1.user_data_set())
    print(S1.user_submissions())
    print(S1.question_tags())
    

