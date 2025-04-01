from flask import Flask, request, jsonify, render_template, session
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

MY_STEAM_API_ACCESS_KEY = os.getenv('STEAM_API')
STEAM_GAME_ONLY_URL = "https://api.steampowered.com/IStoreService/GetAppList/v1/"
GAME_LIST_FILE = "steam_game_list.json"


def fetch_game_list():
    """Fetch and store the complete list of games from Steam API in a JSON file incrementally."""
    params = {
        "key": MY_STEAM_API_ACCESS_KEY,
        "max_results": 49999
    }

    game_list = []
    last_appid = 0

    while True:
        if last_appid:
            params["last_appid"] = last_appid  # Add pagination parameter

        response = requests.get(STEAM_GAME_ONLY_URL, params=params)

        if response.status_code == 200:
            data = response.json()
            game_list.extend(data['response']["apps"])

            # Save the current batch to JSON file
            with open(GAME_LIST_FILE, "w") as f:
                json.dump(game_list, f, indent=4)

            # Check if there are more results
            if data['response'].get("have_more_results", False):
                last_appid = data['response'].get("last_appid", 0)
            else:
                break  # Stop when no more results

        else:
            print(f"Error fetching data: {response.status_code}")
            break

    print(f"Total games fetched: {len(game_list)}")
    return GAME_LIST_FILE


if __name__ == "__main__":
    fetch_game_list()