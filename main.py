import os
import requests
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()

# 1. Configuration
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
EPIC_API_URL = os.getenv("EPIC_API_URL")

def get_free_games():
    response = requests.get(EPIC_API_URL)
    data = response.json()
    
    games = data['data']['Catalog']['searchStore']['elements']
    free_now = []

    for game in games:
        # Check if the game is currently free (discount price is 0)
        price = game.get('price', {}).get('totalPrice', {}).get('discountPrice', 1)
        if price == 0:
            free_now.append(game['title'])
            
    return free_now

def post_to_slack(game_list):
    if not game_list:
        return

    message = "🎮 *Free Games on Epic Store This Week:* \n" + "\n".join([f"• {game}" for game in game_list])
    
    payload = {"text": message}
    requests.post(SLACK_WEBHOOK_URL, json=payload)

# Run the logic
if __name__ == "__main__":
    games = get_free_games()
    # print(games)
    post_to_slack(games) 