from flask import Flask, request, jsonify, render_template, session, make_response
import requests
import random
import os
import json
from dotenv import load_dotenv
import time
from google.cloud import bigquery
from datetime import datetime, timezone

from recommendation import recommend_games_from_model, get_genre_from_gameid

MY_STEAM_API_ACCESS_KEY = os.getenv('STEAM_API')

load_dotenv()

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')
app.config['VERSION'] = str(int(time.time()))

STEAM_APP_LIST_URL = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
STEAM_GAME_DETAILS_URL = "https://store.steampowered.com/api/appdetails"
STEAM_GAME_ONLY_URL = f"https://api.steampowered.com/IStoreService/GetAppList/v1/?key={MY_STEAM_API_ACCESS_KEY}&max_results=49999"

# GAME_LIST_FILE = "steam_game_list.json"
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
GAME_LIST_FILE = os.path.join(PROJECT_DIR, "data", "processed", "steam_game_list.json")

# Cache the game list
GAME_LIST = {}

app.secret_key = 'your_secret_key'  # Make sure to use a secure key

PROJECT_ID = "poojaproject"
BQ_TABLE_ID = f"{PROJECT_ID}.recommendation_metrics.user_feedback"

def log_user_feedback(game_ids, ratings, avg_rating):
    try:
        client = bigquery.Client(project=PROJECT_ID)
        rows_to_insert = [{
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "game_ids": str(game_ids),
            "ratings": str(ratings),
            "avg_rating": avg_rating
        }]
        errors = client.insert_rows_json(BQ_TABLE_ID, rows_to_insert)
        if errors:
            print(f"[BigQuery] Insert errors: {errors}")
        else:
            print("[BigQuery] Feedback logged successfully.")
    except Exception as e:
        print(f"[BigQuery] Feedback logging failed: {e}")


def fetch_game_list():
    """Fetch and store the list of games from Steam API"""
    global GAME_LIST
    # response = requests.get(STEAM_APP_LIST_URL)
    # if response.status_code == 200:
    #     data = response.json()
    #     GAME_LIST = {game["name"]: game["appid"] for game in data["applist"]["apps"]}


    """Load the game list from the JSON file."""
    if os.path.exists(GAME_LIST_FILE):
        with open(GAME_LIST_FILE, "r") as f:
            GAME_LIST = {game["name"]: game["appid"] for game in json.load(f)}

    return GAME_LIST

def search_steam_games(query):
    """Search for games by name"""
    if not GAME_LIST:
        fetch_game_list()
    results = []
    for name, appid in GAME_LIST.items():
        if query.lower() in name.lower():
            # game_details = get_game_details(appid)
            # if game_details and game_details.get("type") == "game":
            results.append({
                "id": appid,
                "name": name,
                "image": f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg"
            })
            if len(results) == 5:  # Return top 5 results
                break
    return results


def get_game_ids(games):






    #This is the function where you call the model to predict the games and return the game ids



    #Get game IDs from game names


    if not GAME_LIST:
        fetch_game_list() 
    
    game_ids = []
    for game_name in games:
        
        if game_name in GAME_LIST:
            game_ids.append(GAME_LIST[game_name]) 
    
    # If you want to hardcode the game id
    # game_ids = [578080,1172470,594650]
    recommended_games = recommend_games_from_model(game_ids,get_genre_from_gameid(game_ids))






    print(recommended_games)

    return recommended_games



def get_game_details_from_ids(game_ids):
    """Get game details from game IDs, including screenshots"""
    recommended_games = []
    for appid in game_ids:
        game_data = get_game_details(appid)
        if game_data:
            screenshots = game_data.get("screenshots", [])
            screenshots_urls = [screenshot["path_full"] for screenshot in screenshots]  # Collect full-size screenshot URLs
            recommended_games.append({
                "id": appid,
                "title": game_data.get("name", "Unknown"),
                "image": game_data.get("header_image", ""),
                "screenshots": screenshots_urls,  # Add screenshots array
                "description": game_data.get("short_description", "No description available."),
                "genres": ", ".join([g["description"] for g in game_data.get("genres", [])]),
                "release_date": game_data.get("release_date", {}).get("date", "Unknown"),
                "developer": ", ".join(game_data.get("developers", ["Unknown"])),
                "price": "Free to Play" if game_data.get("is_free") else f"${(game_data.get('price_overview', {}).get('final', 0) / 100):.2f}",
                "video": game_data.get("movies", [{}])[0].get("mp4", {}).get("max", None),
                "steam_link": f"https://store.steampowered.com/app/{appid}"
            })
    return recommended_games


def get_game_details(appid):
    """Get details about a specific game from Steam"""
    response = requests.get(STEAM_GAME_DETAILS_URL, params={"appids": appid})
    if response.status_code == 200:
        data = response.json()
        game_data = data.get(str(appid), {}).get("data", {})
        return game_data
    return {}


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "")
    if len(query) < 3:
        return jsonify([])
    return jsonify(search_steam_games(query))


@app.route("/", methods=["GET"])
def index():
    response = make_response(render_template("index.html"))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/recommend", methods=["POST", "GET"])
def recommend():
    """Receive selected games and return a list of recommended games"""
    
    if request.method == "POST":
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 415

        data = request.get_json()
        games = data.get("games", [])
        
        if not games:
            return jsonify({"error": "No games provided"}), 400

        print(games)
        # Step 1: Get game IDs from game names
        game_ids = get_game_ids(games)

        if not game_ids:
            return jsonify({"error": "No matching games found"}), 400

        print(game_ids)
        # Step 2: Get detailed information about the games using their IDs
        recommended_games = get_game_details_from_ids(game_ids)

        # Store recommended games in session
        session["recommended_games"] = recommended_games  
        
        # Return a JSON response indicating success
        return jsonify({"redirect": "/recommend"})

    # Handle GET request: Render recommendation.html
    recommended_games = session.get("recommended_games", [])
    return render_template("recommendation.html", games=recommended_games)

@app.route("/submit_feedback", methods=["POST"])

def submit_feedback():
    try:
        data = request.get_json()
        ratings = list(map(int, data.get("ratings", [])))
        game_ids = data.get("game_ids", [])

        if not ratings or not game_ids or len(ratings) != len(game_ids):
            return jsonify({"error": "Invalid feedback data"}), 400

        avg_rating = sum(ratings) / len(ratings)
        log_user_feedback(game_ids, ratings, avg_rating)

        return jsonify({"message": "Thanks for your feedback!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    fetch_game_list()  # Load game list on startup
    app.run(host='0.0.0.0', port=5000)
