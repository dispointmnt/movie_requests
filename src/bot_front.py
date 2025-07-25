from imdb import query_movie
from discord import Embed
import csv
import datetime
from math import ceil

request_filename = "./data/req_queue_uq.csv"
archive_filename = "./data/archive.csv"

entries_pp = 10

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

def validate_request(uid, requesters) -> bool:
    return not (uid in requesters.split(";"))

def get_frequency(requests) -> int:
    return len(requests.split(";"))

def get_queue() -> dict:
    try:
        with open(request_filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            request_data = list(reader)
            sorted_data = sorted(request_data, key=lambda a: get_frequency(a["requesters"]), reverse=True)
    except:
        return 0
    
    return {"command":"queue", 
            "res":sorted_data,
            "page":0,
            "entries_pp":entries_pp}
#TODO change this to read from file
def get_archive() -> dict:
        try:
            with open(archive_filename, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                request_data = list(reader)
        except:
            return 0
        
        return {"command":"archive", 
                "res":request_data,
                "page":0,
                "entries_pp":entries_pp}

def remove_from_csv(uid: str, requesters: str) -> str:
    req_list = requesters.split(";")
    req_list.remove(uid)
    return ";".join(req_list)

def remove_from_requests(title: dict, requester: int):
    new_rows = []
    title_id = title["id"]
    try:
        with open(request_filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                if row['id'] == str(title_id):
                    if not validate_request(str(requester), row["requesters"]):
                        row['requesters'] = remove_from_csv(str(requester), row['requesters'])
                if row["requesters"] != "":
                    new_rows.append(row)
                
        with open(request_filename, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['id', 'movie_name', 'request_date', 'requesters'])
            writer.writeheader()
            writer.writerows(new_rows)
    except:
        return 0
    
    return 1

def add_to_requests(title: dict, requester: int):
    new_rows = []
    old_flag = False
    title_id = title["id"]
    try:
        with open(request_filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                if row['id'] == str(title_id):
                    if validate_request(str(requester), row["requesters"]):
                        row['requesters'] = row['requesters'] + ";" + str(requester)
                        old_flag = True
                    else:
                        return 2
                new_rows.append(row)
            if not old_flag:
                now = datetime.datetime.now()
                date_str = now.strftime("%d/%m/%Y")

                new_rows.append({'id':title["id"],
                                "movie_name":title["primaryTitle"],
                                "request_date":date_str,
                                "requesters":requester})
                
        with open(request_filename, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['id', 'movie_name', 'request_date', 'requesters'])
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
        queue = data["res"]
        page = data["page"]
        entries_pp = data["entries_pp"]

        start_index = (page*entries_pp)
        embed = Embed(
                title="Request Queue",
                description=f"{page+1}/{ceil(len(queue)/entries_pp)}",
                color=0x2f3136
                )

        for i in range(start_index, start_index+entries_pp):
            if (i >= len(queue)):
                continue
            entry = queue[i]
            embed.add_field(name=entry["movie_name"], value=f"[imdb]({'https://www.imdb.com/title/' + entry['id']}) Voters: {get_frequency(entry['requesters'])}", inline=False)

        return {"embed":embed}
    if data["command"] == "archive":

        archive = data["res"]
        page = data["page"]
        entries_pp = data["entries_pp"]

        start_index = (page*entries_pp)
        embed = Embed(
                title="Movie Archive",
                description=f"{page+1}/{ceil(len(archive)/entries_pp)}",
                color=0x2f3136
                )

        for i in range(start_index, start_index+entries_pp):
            if (i >= len(archive)):
                continue
            entry = archive[i]
            embed.add_field(name=entry["movie_name"], value=f"[imdb]({'https://www.imdb.com/title/' + entry['movie_id']}) Date watched: {entry['date_watched']}", inline=False)
        return {"embed":embed}
    if data["command"] == "watch":
        return
    
    print(f"Some error occured with rendering with data:\n{data}")
    return None



if __name__ == "__main__":
    pass