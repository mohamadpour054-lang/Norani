# -*- coding: utf-8 -*-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from game_data import GENDERS, CLASSES, REGIONS, ITEMS


def gender_kb():
    b = InlineKeyboardBuilder()
    for key, label in GENDERS.items():
        b.button(text=label, callback_data=f"create:gender:{key}")
    b.adjust(2)
    return b.as_markup()


def class_kb():
    b = InlineKeyboardBuilder()
    for key, data in CLASSES.items():
        b.button(text=data["label"], callback_data=f"create:class:{key}")
    b.adjust(1)
    return b.as_markup()


def main_menu_kb():
    b = InlineKeyboardBuilder()
    b.button(text="🗺 سفر به مناطق", callback_data="menu:travel")
    b.button(text="🎒 کوله‌پشتی", callback_data="menu:inventory")
    b.button(text="📊 آمار من", callback_data="menu:stats")
    b.adjust(1)
    return b.as_markup()


def regions_kb():
    b = InlineKeyboardBuilder()
    for key, data in REGIONS.items():
        b.button(text=data["label"], callback_data=f"region:{key}")
    b.button(text="🏰 بازگشت به پایتخت", callback_data="menu:main")
    b.adjust(1)
    return b.as_markup()


def region_menu_kb(region_key: str):
    b = InlineKeyboardBuilder()
    b.button(text="⚔️ گشت‌زنی (نبرد تصادفی)", callback_data=f"explore:{region_key}")
    b.button(text="👹 مبارزه با باس منطقه", callback_data=f"boss:{region_key}")
    b.button(text="🗺 بازگشت به مناطق", callback_data="menu:travel")
    b.button(text="🏰 بازگشت به پایتخت", callback_data="menu:main")
    b.adjust(1)
    return b.as_markup()


def combat_kb(has_potion: bool):
    b = InlineKeyboardBuilder()
    b.button(text="🗡 حمله", callback_data="fight:attack")
    b.button(text="🛡 دفاع", callback_data="fight:defend")
    if has_potion:
        b.button(text="🧪 استفاده از معجون", callback_data="fight:item")
    b.button(text="🏃 فرار", callback_data="fight:flee")
    b.adjust(2)
    return b.as_markup()


def inventory_kb(items):
    b = InlineKeyboardBuilder()
    for it in items:
        item_def = ITEMS.get(it["item_id"], {})
        name = item_def.get("name", it["item_id"])
        qty = it["quantity"]
        equipped_tag = " ✅" if it["equipped"] else ""
        text = f"{name} ×{qty}{equipped_tag}"
        if item_def.get("type") in ("weapon", "armor"):
            action = "unequip" if it["equipped"] else "equip"
            b.button(text=text, callback_data=f"inv:{action}:{it['id']}")
        elif item_def.get("type") == "potion":
            b.button(text=text, callback_data=f"inv:usepotion:{it['id']}")
        else:
            b.button(text=text, callback_data="inv:noop")
    b.button(text="🏰 بازگشت", callback_data="menu:main")
    b.adjust(1)
    return b.as_markup()


def back_to_main_kb():
    b = InlineKeyboardBuilder()
    b.button(text="🏰 بازگشت به پایتخت", callback_data="menu:main")
    return b.as_markup()


def region_result_kb(region_key: str):
    b = InlineKeyboardBuilder()
    b.button(text="⚔️ ادامه گشت‌زنی", callback_data=f"explore:{region_key}")
    b.button(text="🗺 بازگشت به مناطق", callback_data="menu:travel")
    b.button(text="🏰 بازگشت به پایتخت", callback_data="menu:main")
    b.adjust(1)
    return b.as_markup()
