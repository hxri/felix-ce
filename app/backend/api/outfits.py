"""Outfit database with static asset URLs"""

OUTFIT_DATABASE = {
    # Tops
    'Blue T-Shirt': 'https://i.postimg.cc/Xqs7H0wD/blue_tshirt.png',
    'White Polo': 'https://i.postimg.cc/wx2vTDSp/white_polo.png',
    'Black Hoodie': 'https://i.postimg.cc/59g0N8ZW/black_hoodie.png',
    'Formal Shirt': 'https://i.postimg.cc/Wz5bWPM7/formal_shirt.png',
    'Black Crop Top': 'https://i.postimg.cc/G21bRt2d/black_crop_top.png',
    'White Tank': 'https://i.postimg.cc/JnWR80n7/white_tank.png',
    'Pink Blouse': 'https://i.postimg.cc/B6GJ3b6b/pink_blouse.png',
    'Formal Dress': 'https://i.postimg.cc/V6czwvNh/formal_dress.png',
    
    # Bottoms
    'Khaki Shorts': 'https://i.postimg.cc/hjHHKZKB/khaki_shorts.png',
    'Black Jeans': 'https://i.postimg.cc/wvSS949K/black_jeans.png',
    'Navy Chinos': 'https://i.postimg.cc/4drrX2XT/navy_chinos.png',
    'Running Shorts': 'https://i.postimg.cc/bJG7cfcx/running_shorts.png',
    'Denim Shorts': 'https://i.postimg.cc/LXMmS5sc/denim_shorts.png',
    'Black Skirt': 'https://i.postimg.cc/9Mjc20fS/black_skirt.png',
    'Casual Leggings': 'https://i.postimg.cc/V6czwvNH/casual_leggings.png',
    'Summer Dress': 'https://i.postimg.cc/0NS9hD9J/summer_dress.png',
    
    # Backgrounds (descriptions, not images)
    'Urban Cafe': 'Urban cafe outdoor with modern city background.',
    'Office': 'Modern office interior with office chairs nearby',
    'Gym': 'Gym or outdoor fitness setting',
    'Studio': 'Clean professional studio with neutral background',
}

def get_outfit_image(outfit_name: str) -> str:
    """Get image URL or description for outfit name"""
    return OUTFIT_DATABASE.get(outfit_name, outfit_name)