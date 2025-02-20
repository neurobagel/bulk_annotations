import requests
import json

def fetch_assessments(api_url, output_file):
    response = requests.get(api_url)
    if response.status_code == 200:
        with open(output_file, 'w') as f:
            json.dump(response.json(), f, indent=2)
    else:
        print(f"Error fetching data: {response.status_code}")

if __name__ == "__main__":
    API_URL = "https://api.neurobagel.org/assessments/"  # Replace with your API URL
    OUTPUT_FILE = "assessments.json"
    fetch_assessments(API_URL, OUTPUT_FILE)