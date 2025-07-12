import requests
import urllib.parse

def query_movie(query: str) -> dict:
    clean_query = urllib.parse.quote_plus(query)
    api_url = 'https://api.imdbapi.dev/search/titles?query=' + clean_query

    response = requests.get(api_url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    # print(json_converter(test_json)["titles"][1])
    print(query_movie("the good the bad"))