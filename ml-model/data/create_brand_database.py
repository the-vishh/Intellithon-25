"""
 50+ BRAND LOGO DATABASE
==========================

Expanding visual protection from 19 to 50+ major brands
"""

import json
import os

# 50+ Major Brands for Visual Protection
BRAND_DATABASE = {
    # Tech Giants (10)
    "google": {
        "name": "Google",
        "domains": ["google.com", "gmail.com", "drive.google.com", "youtube.com"],
        "colors": ["#4285F4", "#EA4335", "#FBBC05", "#34A853"],
        "keywords": ["google", "gmail", "drive", "search"],
    },
    "microsoft": {
        "name": "Microsoft",
        "domains": [
            "microsoft.com",
            "outlook.com",
            "office.com",
            "live.com",
            "onedrive.live.com",
        ],
        "colors": ["#F25022", "#7FBA00", "#00A4EF", "#FFB900"],
        "keywords": ["microsoft", "outlook", "office", "windows"],
    },
    "apple": {
        "name": "Apple",
        "domains": ["apple.com", "icloud.com", "me.com"],
        "colors": ["#000000", "#A6B1B7"],
        "keywords": ["apple", "icloud", "itunes", "iphone"],
    },
    "amazon": {
        "name": "Amazon",
        "domains": ["amazon.com", "aws.amazon.com", "primevideo.com"],
        "colors": ["#FF9900", "#146EB4"],
        "keywords": ["amazon", "aws", "prime"],
    },
    "facebook": {
        "name": "Facebook/Meta",
        "domains": ["facebook.com", "meta.com", "messenger.com"],
        "colors": ["#1877F2", "#4267B2"],
        "keywords": ["facebook", "meta", "messenger"],
    },
    "instagram": {
        "name": "Instagram",
        "domains": ["instagram.com"],
        "colors": ["#E4405F", "#833AB4", "#FCAF45"],
        "keywords": ["instagram", "insta"],
    },
    "twitter": {
        "name": "Twitter/X",
        "domains": ["twitter.com", "x.com"],
        "colors": ["#1DA1F2", "#14171A"],
        "keywords": ["twitter", "tweet"],
    },
    "linkedin": {
        "name": "LinkedIn",
        "domains": ["linkedin.com"],
        "colors": ["#0A66C2", "#00364D"],
        "keywords": ["linkedin"],
    },
    "github": {
        "name": "GitHub",
        "domains": ["github.com"],
        "colors": ["#181717", "#4078C0"],
        "keywords": ["github", "git"],
    },
    "adobe": {
        "name": "Adobe",
        "domains": ["adobe.com", "creative.adobe.com"],
        "colors": ["#FF0000", "#ED1C24"],
        "keywords": ["adobe", "creative cloud"],
    },
    # Financial Services (15)
    "paypal": {
        "name": "PayPal",
        "domains": ["paypal.com"],
        "colors": ["#003087", "#009CDE"],
        "keywords": ["paypal", "payment"],
    },
    "chase": {
        "name": "Chase Bank",
        "domains": ["chase.com"],
        "colors": ["#003D6A", "#0074BE"],
        "keywords": ["chase", "bank"],
    },
    "bankofamerica": {
        "name": "Bank of America",
        "domains": ["bankofamerica.com"],
        "colors": ["#002244", "#CD0000"],
        "keywords": ["bank of america", "bofa"],
    },
    "wellsfargo": {
        "name": "Wells Fargo",
        "domains": ["wellsfargo.com"],
        "colors": ["#D71E28", "#FFCD41"],
        "keywords": ["wells fargo", "wells"],
    },
    "citibank": {
        "name": "Citibank",
        "domains": ["citibank.com", "citi.com"],
        "colors": ["#003F7F", "#006FCF"],
        "keywords": ["citibank", "citi"],
    },
    "americanexpress": {
        "name": "American Express",
        "domains": ["americanexpress.com", "amex.com"],
        "colors": ["#006FCF", "#00175A"],
        "keywords": ["american express", "amex"],
    },
    "visa": {
        "name": "Visa",
        "domains": ["visa.com"],
        "colors": ["#1A1F71", "#00579F"],
        "keywords": ["visa"],
    },
    "mastercard": {
        "name": "Mastercard",
        "domains": ["mastercard.com"],
        "colors": ["#EB001B", "#F79E1B"],
        "keywords": ["mastercard"],
    },
    "stripe": {
        "name": "Stripe",
        "domains": ["stripe.com"],
        "colors": ["#635BFF", "#00D4FF"],
        "keywords": ["stripe"],
    },
    "square": {
        "name": "Square",
        "domains": ["square.com", "cash.app"],
        "colors": ["#3E4348", "#00B956"],
        "keywords": ["square", "cash app"],
    },
    "venmo": {
        "name": "Venmo",
        "domains": ["venmo.com"],
        "colors": ["#3D95CE", "#008CFF"],
        "keywords": ["venmo"],
    },
    "coinbase": {
        "name": "Coinbase",
        "domains": ["coinbase.com"],
        "colors": ["#0052FF", "#001E5C"],
        "keywords": ["coinbase", "crypto"],
    },
    "robinhood": {
        "name": "Robinhood",
        "domains": ["robinhood.com"],
        "colors": ["#00C805", "#1B1B1B"],
        "keywords": ["robinhood"],
    },
    "etrade": {
        "name": "E*TRADE",
        "domains": ["etrade.com"],
        "colors": ["#6633CC", "#000000"],
        "keywords": ["etrade", "e trade"],
    },
    "fidelity": {
        "name": "Fidelity",
        "domains": ["fidelity.com"],
        "colors": ["#009B77", "#003D4F"],
        "keywords": ["fidelity"],
    },
    # E-commerce & Retail (10)
    "ebay": {
        "name": "eBay",
        "domains": ["ebay.com"],
        "colors": ["#E53238", "#0064D2", "#F5AF02"],
        "keywords": ["ebay"],
    },
    "walmart": {
        "name": "Walmart",
        "domains": ["walmart.com"],
        "colors": ["#0071CE", "#FFC220"],
        "keywords": ["walmart"],
    },
    "target": {
        "name": "Target",
        "domains": ["target.com"],
        "colors": ["#CC0000", "#FFFFFF"],
        "keywords": ["target"],
    },
    "bestbuy": {
        "name": "Best Buy",
        "domains": ["bestbuy.com"],
        "colors": ["#0046BE", "#FFF200"],
        "keywords": ["best buy", "bestbuy"],
    },
    "homedepot": {
        "name": "Home Depot",
        "domains": ["homedepot.com"],
        "colors": ["#F96302", "#2E3A13"],
        "keywords": ["home depot"],
    },
    "etsy": {
        "name": "Etsy",
        "domains": ["etsy.com"],
        "colors": ["#F56400", "#000000"],
        "keywords": ["etsy"],
    },
    "alibaba": {
        "name": "Alibaba",
        "domains": ["alibaba.com"],
        "colors": ["#FF6A00", "#000000"],
        "keywords": ["alibaba"],
    },
    "shopify": {
        "name": "Shopify",
        "domains": ["shopify.com"],
        "colors": ["#96BF48", "#5E8E3E"],
        "keywords": ["shopify"],
    },
    "wayfair": {
        "name": "Wayfair",
        "domains": ["wayfair.com"],
        "colors": ["#7C2993", "#000000"],
        "keywords": ["wayfair"],
    },
    "overstock": {
        "name": "Overstock",
        "domains": ["overstock.com"],
        "colors": ["#DB1F26", "#000000"],
        "keywords": ["overstock"],
    },
    # Streaming & Entertainment (5)
    "netflix": {
        "name": "Netflix",
        "domains": ["netflix.com"],
        "colors": ["#E50914", "#000000"],
        "keywords": ["netflix"],
    },
    "spotify": {
        "name": "Spotify",
        "domains": ["spotify.com"],
        "colors": ["#1DB954", "#191414"],
        "keywords": ["spotify"],
    },
    "hulu": {
        "name": "Hulu",
        "domains": ["hulu.com"],
        "colors": ["#1CE783", "#0B0C0F"],
        "keywords": ["hulu"],
    },
    "disney": {
        "name": "Disney+",
        "domains": ["disneyplus.com", "disney.com"],
        "colors": ["#113CCF", "#000000"],
        "keywords": ["disney", "disney plus"],
    },
    "twitch": {
        "name": "Twitch",
        "domains": ["twitch.tv"],
        "colors": ["#9146FF", "#000000"],
        "keywords": ["twitch"],
    },
    # Cloud & Developer Tools (5)
    "dropbox": {
        "name": "Dropbox",
        "domains": ["dropbox.com"],
        "colors": ["#0061FF", "#1E1919"],
        "keywords": ["dropbox"],
    },
    "slack": {
        "name": "Slack",
        "domains": ["slack.com"],
        "colors": ["#4A154B", "#ECB22E"],
        "keywords": ["slack"],
    },
    "zoom": {
        "name": "Zoom",
        "domains": ["zoom.us"],
        "colors": ["#2D8CFF", "#000000"],
        "keywords": ["zoom"],
    },
    "atlassian": {
        "name": "Atlassian/Jira",
        "domains": ["atlassian.com", "jira.com"],
        "colors": ["#0052CC", "#DEEBFF"],
        "keywords": ["atlassian", "jira"],
    },
    "notion": {
        "name": "Notion",
        "domains": ["notion.so"],
        "colors": ["#000000", "#FFFFFF"],
        "keywords": ["notion"],
    },
    # Social & Communication (5)
    "whatsapp": {
        "name": "WhatsApp",
        "domains": ["whatsapp.com", "web.whatsapp.com"],
        "colors": ["#25D366", "#075E54"],
        "keywords": ["whatsapp"],
    },
    "telegram": {
        "name": "Telegram",
        "domains": ["telegram.org", "t.me"],
        "colors": ["#0088CC", "#FFFFFF"],
        "keywords": ["telegram"],
    },
    "discord": {
        "name": "Discord",
        "domains": ["discord.com"],
        "colors": ["#5865F2", "#404EED"],
        "keywords": ["discord"],
    },
    "reddit": {
        "name": "Reddit",
        "domains": ["reddit.com"],
        "colors": ["#FF4500", "#1A1A1B"],
        "keywords": ["reddit"],
    },
    "snapchat": {
        "name": "Snapchat",
        "domains": ["snapchat.com"],
        "colors": ["#FFFC00", "#000000"],
        "keywords": ["snapchat", "snap"],
    },
}


def save_brand_database():
    """Save brand database to JSON"""
    output_dir = "data/brands"
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "brand_database_50plus.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(BRAND_DATABASE, f, indent=2, ensure_ascii=False)

    print(f" Saved {len(BRAND_DATABASE)} brands to {output_file}")

    # Print summary
    print(f"\n Brand Database Summary:")
    print(f"   Total Brands: {len(BRAND_DATABASE)}")
    print(
        f"   Total Domains: {sum(len(b['domains']) for b in BRAND_DATABASE.values())}"
    )

    # Count by category
    categories = {
        "Tech Giants": 10,
        "Financial Services": 15,
        "E-commerce & Retail": 10,
        "Streaming & Entertainment": 5,
        "Cloud & Developer Tools": 5,
        "Social & Communication": 5,
    }

    print(f"\n By Category:")
    for cat, count in categories.items():
        print(f"   {cat}: {count} brands")

    print(f"\n Top 10 Most Targeted Brands:")
    top_brands = [
        "PayPal",
        "Amazon",
        "Microsoft",
        "Apple",
        "Google",
        "Facebook",
        "Chase",
        "Bank of America",
        "Netflix",
        "Instagram",
    ]
    for i, brand in enumerate(top_brands, 1):
        print(f"   {i}. {brand}")


if __name__ == "__main__":
    print("=" * 80)
    print(" CREATING 50+ BRAND DATABASE")
    print("=" * 80)

    save_brand_database()

    print("\n" + "=" * 80)
    print(" 50+ BRAND DATABASE COMPLETE!")
    print("=" * 80)
    print("\n We now protect 50+ brands (vs competitors' ~10-20)")
    print("=" * 80)
