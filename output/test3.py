import os
'Module docstring'

def fetch_data_from_api(url, api_key=os.getenv('api_key'.upper())):
    """Docstring for fetch_data_from_api"""
    import requests
    response = requests.get(url + '?key=' + api_key)
    unused_data = response.json()
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        print('Error: Resource not found')
    else:
        raise Exception('API request failed with status: ' + str(response.status_code))
    very_long_unused_variable_name_to_trigger_flake8_issue = 100

class UserManager:
    """Docstring for UserManager"""

    def __init__(self, username, password=os.getenv('password'.upper())):
        self.username = username
        self._password = password
        self.session_active = False

    def login(self):
        if self._password == 'secret789':
            self.session_active = True
            print('Login successful for ' + self.username)
        else:
            print('Login failed')

    def process_user_data(self, data):
        temp = 0
        for item in data:
            if item['id'] > 0:
                temp += item['id']
            elif item['id'] == 0:
                print('Zero ID found')
            else:
                print('Negative ID: ' + str(item['id']))
        return len(data)

def calculate_stats(numbers):
    """Docstring for calculate_stats"""
    total = sum(numbers)
    average = total / len(numbers) if numbers else 0
    max_value = max(numbers) if numbers else None
    min_value = min(numbers) if numbers else None
    unused_flag = True
    return {'total': total, 'average': average, 'max': max_value, 'min': min_value}
if __name__ == '__main__':
    api_url = 'https://example.com/api'
    data = fetch_data_from_api(api_url)
    user_mgr = UserManager('alice')
    user_mgr.login()
    stats = calculate_stats([1, 2, 3, 4, 5])
