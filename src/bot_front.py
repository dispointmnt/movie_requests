from imdb import query_movie
from discord import Embed
import csv
import datetime
from math import ceil

request_filename = "./data/req_queue.csv"
archive_filename = "./data/archive.csv"

def get_query(query: str) -> dict:
    response = query_movie(query)
    titles = response["titles"]
    return {"command":"request", 
            "query_list":titles, 
            "index":0,
            "total":len(titles)-1}

test_data = [
    {
        "id": "001",
        "movie_name": "Inception",
        "request_date": "09/07/2025",
        "request_frequency": 2,
        "image_url": "https://m.media-amazon.com/images/M/MV5BNTBiYWJlMjQtOTIyMy00NTY4LWFhOWItOWZhNzc3NGMyMjc2XkEyXkFqcGc@._V1_.jpg"
    },
    {
        "id": "002",
        "movie_name": "The Matrix",
        "request_date": "11/07/2025",
        "request_frequency": 5,
        "image_url": ""
    },
    {
        "id": "003",
        "movie_name": "Interstellar",
        "request_date": "02/07/2025",
        "request_frequency": 1,
        "image_url": "https://m.media-amazon.com/images/M/MV5BNTBiYWJlMjQtOTIyMy00NTY4LWFhOWItOWZhNzc3NGMyMjc2XkEyXkFqcGc@._V1_.jpg"
    },
    {
        "id": "004",
        "movie_name": "The Dark Knight",
        "request_date": "05/07/2025",
        "request_frequency": 3,
        "image_url": ""
    },
    {
        "id": "005",
        "movie_name": "Pulp Fiction",
        "request_date": "10/07/2025",
        "request_frequency": 4,
        "image_url": ""
    },
    {
        "id": "006",
        "movie_name": "Fight Club",
        "request_date": "07/07/2025",
        "request_frequency": 2,
        "image_url": "https://m.media-amazon.com/images/M/MV5BNTBiYWJlMjQtOTIyMy00NTY4LWFhOWItOWZhNzc3NGMyMjc2XkEyXkFqcGc@._V1_.jpg"
    },
]
def get_queue() -> dict:
    try:
        with open(request_filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            request_data = list(reader)
            sorted_data = sorted(request_data, key=lambda a: int(a["request_frequency"]), reverse=True)
    except:
        return 0
    
    return {"command":"queue", 
            "queue":sorted_data,
            "page":0,
            "entries_pp":5}
#TODO change this to read from file

def add_to_requests(title: dict):
    new_rows = []
    old_flag = False
    title_id = title["id"]
    try:
        with open(request_filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                if row['id'] == str(title_id):
                    row['request_frequency'] = str(int(row['request_frequency']) + 1)
                    old_flag = True
                new_rows.append(row)
            if not old_flag:
                now = datetime.datetime.now()
                date_str = now.strftime("%d/%m/%Y")

                new_rows.append({'id':title["id"],
                                "movie_name":title["primaryTitle"],
                                "request_date":date_str,
                                "request_frequency":1,
                                "image_url":title["primaryImage"]["url"]})
                
        with open(request_filename, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['id', 'movie_name', 'request_date', 'request_frequency', 'image_url'])
            writer.writeheader()
            writer.writerows(new_rows)
    except:
        return 0
    
    return 1


def render(data: dict) -> dict:
    if data["command"] == "request":
        display_title = data["query_list"][data["index"]]
        embed = Embed(
            title=display_title["primaryTitle"],
            description="i gotta find a way to get the imdb description, hang tight",
            color=0x2f3136,
            url = "https://www.imdb.com/title/" + display_title["id"]
        )
        embed.set_author(name=f"{data['index']}/{data['total']}") #f"{data['index']}/{data['total']}"
        embed.set_footer(text=display_title["type"])
        if ("primaryImage" in display_title.keys()):
            embed.set_image(url=display_title["primaryImage"]["url"])
        return {"embed":embed}
    
    if data["command"] == "queue":
        queue = data["queue"]
        page = data["page"]
        entries_pp = data["entries_pp"]

        start_index = (page*entries_pp)
        embeds = [Embed(
                title="Request Queue",
                description=f"{page+1}/{ceil(len(queue)/entries_pp)}",
                color=0x2f3136
                )]

        for i in range(start_index, start_index+entries_pp):
            if (i >= len(queue)):
                continue
            entry = queue[i]
            embed = Embed(
                title=entry["movie_name"],
                description=f"Date Requested: {entry['request_date']}\n\# people requested: {entry['request_frequency']}",
                color=0x2f3136,
                url = "https://www.imdb.com/title/" + entry["id"]
            )
            embed.set_author(name=str(i+1))
            embed.set_thumbnail(url=entry['image_url'])

            embeds.append(embed)
        return {"embeds":embeds}
    if data["command"] == "archive":
        return
    if data["command"] == "watch":
        return
    
    print(f"Some error occured with rendering with data:\n{data}")
    return None


if __name__ == "__main__":
    add_to_requests({
      "id": "sdfsdfsdfsdf",
      "type": "movie",
      "primaryTitle": "crazy movie"})