# import requests

# STEAM_APP_LIST_URL = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"

# def fetch_game_list():
#     """Fetch and store the list of games from Steam API"""
#     response = requests.get(STEAM_APP_LIST_URL)
#     if response.status_code == 200:
#         data = response.json()
#         game_list = {game["name"].lower(): game["appid"] for game in data["applist"]["apps"]}
#         return game_list
#     return {}

# def search_steam_games(query, game_list):
#     """Search for games by name"""
#     results = [
#         {"id": appid, "name": name}
#         for name, appid in game_list.items()
#         if query.lower() in name.lower()
#     ][:5]  # Return top 5 results

#     for game in results:
#         game["image"] = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{game['id']}/header.jpg"

#     return results

# # Run test
# game_list = fetch_game_list()
# print(len(game_list))
# query = input("Enter a game name to search: ")
# results = search_steam_games(query, game_list)

# print("Search Results:")
# for game in results:
#     print(f"Name: {game['name']}, ID: {game['id']}, Image: {game['image']}")


import requests

STEAM_API_KEY = "7BCC51361EC7334C9F743AA130F32406"  # Replace with your API key
STEAM_USER_ID = "76561198842127783"  # Replace with a valid Steam64 ID

def check_steam_api(game_ids):
    url = "https://store.steampowered.com/api/appdetails"

    genre_gameid_mapping = {}

    for game_id in game_ids:
        params = {
            "appids": game_id
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            # print(data)
            # print("data is here", data[str(game_id)]["data"]["type"])
            if data[str(game_id)]["success"]:
                # genre_gameid_mapping[game_id] = 
                # print(data[str(game_id)]["data"]["genres"])
                genre_list = data[str(game_id)]["data"]["genres"]
                genres = []
                # print()
                for genre in genre_list:
                    genres.append(genre["description"])
                genre_gameid_mapping[game_id] = genres
            else:
                print("No genres found for the game id :",game_id)
        else:
            print("❌ API Key is not working. Status Code:", response.status_code)
    return list(set(genre for genres in genre_gameid_mapping.values() for genre in genres))
    return genre_gameid_mapping
if __name__ == "__main__":
    
    game_ids = [578080,2934980]
    # game_ids = [229480]
    print(check_steam_api(game_ids))
