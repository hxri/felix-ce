"""Outfit database with static asset URLs"""

OUTFIT_DATABASE = {
    # Tops
    'Blue T-Shirt': 'https://i.postimg.cc/Xqs7H0wD/blue_tshirt.png',
    'White Polo': 'https://i.postimg.cc/wx2vTDSp/white_polo.png',
    'Black Hoodie': 'https://i.postimg.cc/59g0N8ZW/black_hoodie.png',
    'Formal Shirt': 'https://i.postimg.cc/Wz5bWPM7/formal_shirt.png',
    
    # Bottoms
    'Khaki Shorts': 'https://i.postimg.cc/hjHHKZKB/khaki_shorts.png',
    'Black Jeans': 'https://i.postimg.cc/wvSS949K/black_jeans.png',
    'Navy Chinos': 'https://i.postimg.cc/4drrX2XT/navy_chinos.png',
    'Running Shorts': 'https://i.postimg.cc/bJG7cfcx/running_shorts.png',
    
    # Backgrounds (descriptions, not images)
    'Urban Cafe': 'Urban cafe outdoor with modern city background',
    'Office': 'Modern office interior with office chairs nearby',
    'Gym': 'Gym or outdoor fitness setting',
    'Studio': 'Clean professional studio with neutral background',
}

def get_outfit_image(outfit_name: str) -> str:
    """Get image URL or description for outfit name"""
    return OUTFIT_DATABASE.get(outfit_name, outfit_name)