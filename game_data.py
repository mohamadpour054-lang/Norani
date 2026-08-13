# -*- coding: utf-8 -*-
"""
داده‌های ثابت بازی الدوریا (Eldoria)
کلاس‌ها، آیتم‌ها، مناطق، مأب‌ها و باس‌ها اینجا تعریف می‌شن.
"""

GENDERS = {
    "male": "👨 مرد",
    "female": "👩 زن",
}

CLASSES = {
    "warrior": {"label": "⚔️ جنگجو", "hp": 130, "atk": 14, "def": 12,
                "desc": "بدنی قوی و دفاع بالا، مناسب مبارزه رودررو."},
    "mage":    {"label": "🔮 جادوگر", "hp": 85,  "atk": 20, "def": 6,
                "desc": "حمله ویرانگر ولی بدن ضعیف."},
    "archer":  {"label": "🏹 کماندار", "hp": 105, "atk": 17, "def": 8,
                "desc": "تعادل بین حمله و دفاع، چابک."},
}

# ضریب رشد آمار در هر لول‌آپ (بر اساس کلاس)
LEVEL_UP_GROWTH = {
    "warrior": {"hp": 18, "atk": 3, "def": 3},
    "mage":    {"hp": 10, "atk": 5, "def": 1},
    "archer":  {"hp": 13, "atk": 4, "def": 2},
}

# آیتم‌ها
ITEMS = {
    "potion_small": {"name": "🧪 معجون کوچک سلامتی", "type": "potion", "heal": 30, "buy_price": 15},
    "potion_big":   {"name": "🧴 معجون بزرگ سلامتی", "type": "potion", "heal": 70, "buy_price": 35},

    "rusty_sword":  {"name": "🗡 شمشیر زنگ‌زده", "type": "weapon", "atk": 3},
    "iron_sword":   {"name": "⚔️ شمشیر آهنی", "type": "weapon", "atk": 7},
    "scimitar":     {"name": "🔪 شمشیر خمیده کویری", "type": "weapon", "atk": 9},
    "frost_blade":  {"name": "❄️ تیغه یخ‌زده", "type": "weapon", "atk": 12},
    "venom_dagger": {"name": "🗡 خنجر زهرآلود", "type": "weapon", "atk": 11},

    "wooden_shield":{"name": "🛡 سپر چوبی", "type": "armor", "def": 3},
    "iron_armor":   {"name": "🥋 زره آهنی", "type": "armor", "def": 6},
    "desert_cloak": {"name": "🧥 ردای کویری", "type": "armor", "def": 7},
    "frost_plate":  {"name": "🛡 زره یخی", "type": "armor", "def": 10},
    "swamp_hide":   {"name": "🐊 پوستین باتلاقی", "type": "armor", "def": 8},

    "wolf_king_trophy":  {"name": "👑 دندان پادشاه گرگ‌ها", "type": "trophy"},
    "desert_serpent_trophy": {"name": "💎 پوست مار افسانه‌ای", "type": "trophy"},
    "ice_giant_trophy":  {"name": "🧊 قلب غول یخی", "type": "trophy"},
    "swamp_lord_trophy": {"name": "🧟 طلسم ارباب باتلاق", "type": "trophy"},
}

# مناطق چهارگانه‌ی خطرناک اطراف پایتخت
REGIONS = {
    "east": {
        "label": "🌅 شرق - جنگل مه‌آلود",
        "min_level": 1,
        "mobs": [
            {"name": "🐺 گرگ وحشی", "hp": 40, "atk": 8, "def": 2,
             "xp": 15, "gold": (5, 10), "drop": [("potion_small", 0.4)]},
            {"name": "🗡 دزد جنگل", "hp": 55, "atk": 10, "def": 3,
             "xp": 22, "gold": (8, 15), "drop": [("rusty_sword", 0.25), ("potion_small", 0.3)]},
        ],
        "boss": {"name": "👑 پادشاه گرگ‌ها", "hp": 220, "atk": 18, "def": 8,
                 "xp": 150, "gold": (80, 120), "drop": [("iron_sword", 1.0), ("wolf_king_trophy", 1.0)],
                 "min_level": 5},
    },
    "west": {
        "label": "🏜 غرب - کویر سوزان",
        "min_level": 3,
        "mobs": [
            {"name": "🦂 عقرب غول‌پیکر", "hp": 60, "atk": 12, "def": 4,
             "xp": 28, "gold": (10, 18), "drop": [("potion_small", 0.35)]},
            {"name": "🏴 راهزن کویر", "hp": 75, "atk": 14, "def": 5,
             "xp": 35, "gold": (15, 25), "drop": [("desert_cloak", 0.2), ("potion_big", 0.25)]},
        ],
        "boss": {"name": "🐍 مار افسانه‌ای کویر", "hp": 320, "atk": 24, "def": 10,
                 "xp": 260, "gold": (140, 200), "drop": [("scimitar", 1.0), ("desert_serpent_trophy", 1.0)],
                 "min_level": 9},
    },
    "north": {
        "label": "🏔 شمال - کوهستان یخ‌زده",
        "min_level": 6,
        "mobs": [
            {"name": "🐺 گرگ برفی", "hp": 90, "atk": 16, "def": 6,
             "xp": 42, "gold": (18, 28), "drop": [("potion_big", 0.3)]},
            {"name": "🧊 غول یخی کوچک", "hp": 110, "atk": 18, "def": 8,
             "xp": 55, "gold": (25, 40), "drop": [("frost_plate", 0.2)]},
        ],
        "boss": {"name": "❄️ غول یخی بزرگ", "hp": 450, "atk": 30, "def": 14,
                 "xp": 400, "gold": (220, 320), "drop": [("frost_blade", 1.0), ("ice_giant_trophy", 1.0)],
                 "min_level": 13},
    },
    "south": {
        "label": "🐊 جنوب - باتلاق نفرین‌شده",
        "min_level": 9,
        "mobs": [
            {"name": "🐍 مار باتلاقی", "hp": 130, "atk": 20, "def": 9,
             "xp": 65, "gold": (30, 45), "drop": [("swamp_hide", 0.2)]},
            {"name": "🧟 زامبی باتلاق", "hp": 150, "atk": 22, "def": 10,
             "xp": 78, "gold": (35, 55), "drop": [("venom_dagger", 0.2), ("potion_big", 0.35)]},
        ],
        "boss": {"name": "🧟‍♂️ ارباب باتلاق", "hp": 600, "atk": 38, "def": 18,
                 "xp": 600, "gold": (350, 500), "drop": [("venom_dagger", 1.0), ("swamp_lord_trophy", 1.0)],
                 "min_level": 17},
    },
}

STARTING_GOLD = 25
STARTING_ITEMS = ["potion_small"]


def xp_needed_for_level(level: int) -> int:
    """مقدار تجربه‌ی لازم برای رسیدن به لول بعدی"""
    return 80 + (level - 1) * 45
