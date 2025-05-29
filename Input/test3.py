def fetch_data_from_api(url, api_key="abc123"):
    import requests
    response = requests.get(url + "?key=" + api_key)
    unused_data = response.json()
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        print("Error: Resource not found")
    else:
        raise Exception("API request failed with status: " + str(response.status_code))
