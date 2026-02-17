import os
import requests
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()

# 1. Configuration
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
EPIC_API_URL = os.getenv("EPIC_API_URL")

def get_free_games():
    res = requests.get(EPIC_API_URL).json()
    elements = res['data']['Catalog']['searchStore']['elements']
    formatted_blocks = []

    for game in elements:
        # Check for active 100% discount
        discount_price = game.get('price', {}).get('totalPrice', {}).get('discountPrice', 1)
        if discount_price == 0:
            title = game['title']
            slug = game.get('productSlug') or game.get('catalogNs', {}).get('mappings', [{}])[0].get('pageSlug')
            url = f"https://store.epicgames.com/en-US/p/{slug}"
            
            # Find the best image (Wide landscape images look best in Slack)
            image_url = next((img['url'] for img in game['keyImages'] if img['type'] == 'Thumbnail'), None)
            
            # Create a "Block" for this game
            formatted_blocks.extend([
                {"type": "header", "text": {"type": "plain_text", "text": f"🎮 {title}"}},
                {"type": "image", "image_url": image_url, "alt_text": title} if image_url else None,
                {
                    "type": "actions",
                    "elements": [{
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Claim on Epic Games Store"},
                        "url": url,
                        "action_id": f"claim_{slug[:20]}" # Unique ID
                    }]
                },
                {"type": "divider"}
            ])
    
    # Filter out None values from missing images
    return [b for b in formatted_blocks if b]

def send_to_slack(blocks):
    if not blocks: return
    # Slack requires a 'blocks' field in the JSON payload
    payload = {"blocks": blocks}
    requests.post(SLACK_WEBHOOK_URL, json=payload)

if __name__ == "__main__":
    blocks = get_free_games()
    send_to_slack(blocks)
