# -*- coding: utf-8 -*-
import random

from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

import database as db
import keyboards as kb
from game_data import CLASSES, GENDERS, ITEMS, REGIONS, xp_needed_for_level

router = Router()

# فایت‌های در حال انجام: user_id -> dict
ACTIVE_FIGHTS = {}


class Creation(StatesGroup):
    name = State()
    gender = State()
    clas = State()


# ---------------------------------------------------------------------------
# شروع بازی / ساخت کاراکتر
# ---------------------------------------------------------------------------

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    if db.player_exists(user_id):
        await message.answer(
            "به الدوریا خوش برگشتی، قهرمان! 🏰\nاز پایتخت (منطقه‌ی امن) می‌تونی به مأموریت بری.",
            reply_markup=kb.main_menu_kb(),
        )
        return

    await state.set_state(Creation.name)
    await message.answer(
        "🌍 به دنیای *الدوریا* خوش اومدی!\n\n"
        "پیش از شروع سفر باید یه قهرمان بسازیم.\n"
        "لطفاً *اسم* شخصیتت رو بفرست:",
        parse_mode="Markdown",
    )


@router.message(StateFilter(Creation.name))
async def creation_name(message: Message, state: FSMContext):
    name = (message.text or "").strip()
    if not name or len(name) > 30:
        await message.answer("اسم نامعتبره. یه اسم بین ۱ تا ۳۰ کاراکتر بفرست:")
        return
    await state.update_data(name=name)
    await state.set_state(Creation.gender)
    await message.answer(f"خب {name}، حالا جنسیت شخصیتت رو انتخاب کن:", reply_markup=kb.gender_kb())


@router.callback_query(StateFilter(Creation.gender), F.data.startswith("create:gender:"))
async def creation_gender(callback: CallbackQuery, state: FSMContext):
    gender_key = callback.data.split(":")[2]
    await state.update_data(gender=gender_key)
    await state.set_state(Creation.clas)
    text = "کلاس شخصیتت رو انتخاب کن:\n\n"
    for key, data in CLASSES.items():
        text += f"{data['label']}\n❤️ HP:{data['hp']}  ⚔️ ATK:{data['atk']}  🛡 DEF:{data['def']}\n{data['desc']}\n\n"
    await callback.message.edit_text(text, reply_markup=kb.class_kb())
    await callback.answer()


@router.callback_query(StateFilter(Creation.clas), F.data.startswith("create:class:"))
async def creation_class(callback: CallbackQuery, state: FSMContext):
    clas_key = callback.data.split(":")[2]
    data = await state.get_data()
    name = data["name"]
    gender = data["gender"]

    db.create_player(callback.from_user.id, name, gender, clas_key)
    await state.clear()

    await callback.message.edit_text(
        f"🎉 قهرمان *{name}* ({GENDERS[gender]} - {CLASSES[clas_key]['label']}) ساخته شد!\n\n"
        f"تو اکنون در *پایتخت* هستی — منطقه‌ی امن الدوریا.\n"
        f"چهار منطقه‌ی خطرناک اطراف پایتخت هستن: شرق، غرب، شمال و جنوب.\n"
        f"برای شروع ماجراجویی از منوی پایین استفاده کن 👇",
        parse_mode="Markdown",
        reply_markup=kb.main_menu_kb(),
    )
    await callback.answer()


# ---------------------------------------------------------------------------
# منوهای اصلی (پایتخت)
# ---------------------------------------------------------------------------

@router.callback_query(F.data == "menu:main")
async def menu_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    ACTIVE_FIGHTS.pop(callback.from_user.id, None)
    await callback.message.edit_text(
        "🏰 تو در *پایتخت* هستی — اینجا منطقه‌ی امنه و هیچ موجودی بهت حمله نمی‌کنه.",
        parse_mode="Markdown",
        reply_markup=kb.main_menu_kb(),
    )
    db.set_location(callback.from_user.id, "capital")
    await callback.answer()


@router.callback_query(F.data == "menu:travel")
async def menu_travel(callback: CallbackQuery):
    await callback.message.edit_text(
        "🗺 کدوم منطقه رو برای گشت‌زنی انتخاب می‌کنی؟\n\n"
        + "\n".join(f"{d['label']} (حداقل لول {d['min_level']})" for d in REGIONS.values()),
        reply_markup=kb.regions_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:stats")
async def menu_stats(callback: CallbackQuery):
    user_id = callback.from_user.id
    p = db.get_player(user_id)
    stats = db.effective_stats(user_id)
    needed = xp_needed_for_level(p["level"])
    text = (
        f"📊 *آمار {p['name']}*\n\n"
        f"کلاس: {CLASSES[p['class']]['label']}\n"
        f"لول: {p['level']}\n"
        f"تجربه: {p['xp']}/{needed}\n"
        f"❤️ سلامتی: {p['hp']}/{stats['max_hp']}\n"
        f"⚔️ قدرت حمله: {stats['atk']}\n"
        f"🛡 دفاع: {stats['def']}\n"
        f"💰 طلا: {p['gold']}\n"
        f"📍 موقعیت: {'پایتخت (امن)' if p['location'] == 'capital' else p['location']}"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb.back_to_main_kb())
    await callback.answer()


@router.callback_query(F.data == "menu:inventory")
async def menu_inventory(callback: CallbackQuery):
    user_id = callback.from_user.id
    items = db.get_inventory(user_id)
    if not items:
        text = "🎒 کوله‌پشتیت خالیه."
    else:
        text = "🎒 *کوله‌پشتی تو:*\nروی هر آیتم بزن تا تجهیزش کنی یا استفاده‌ش کنی."
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb.inventory_kb(items))
    await callback.answer()


@router.callback_query(F.data.startswith("inv:"))
async def inventory_action(callback: CallbackQuery):
    user_id = callback.from_user.id
    parts = callback.data.split(":")
    action = parts[1]

    if action == "noop":
        await callback.answer()
        return

    inv_id = int(parts[2])

    if action == "equip":
        ok = db.equip_item(user_id, inv_id)
        await callback.answer("تجهیز شد ✅" if ok else "خطا در تجهیز", show_alert=False)
    elif action == "unequip":
        db.unequip_item(user_id, inv_id)
        await callback.answer("از تجهیز خارج شد")
    elif action == "usepotion":
        items = db.get_inventory(user_id)
        row = next((i for i in items if i["id"] == inv_id), None)
        if not row:
            await callback.answer("این آیتم دیگه موجود نیست.")
        else:
            item_def = ITEMS[row["item_id"]]
            p = db.get_player(user_id)
            stats = db.effective_stats(user_id)
            new_hp = min(stats["max_hp"], p["hp"] + item_def["heal"])
            db.set_hp(user_id, new_hp)
            db.remove_item(user_id, row["item_id"], 1)
            await callback.answer(f"❤️ {item_def['heal']} سلامتی ترمیم شد!")

    items = db.get_inventory(user_id)
    text = "🎒 کوله‌پشتیت خالیه." if not items else "🎒 *کوله‌پشتی تو:*"
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb.inventory_kb(items))


# ---------------------------------------------------------------------------
# مناطق
# ---------------------------------------------------------------------------

@router.callback_query(F.data.startswith("region:"))
async def region_menu(callback: CallbackQuery):
    region_key = callback.data.split(":")[1]
    region = REGIONS[region_key]
    user_id = callback.from_user.id
    p = db.get_player(user_id)
    db.set_location(user_id, region_key)

    warn = ""
    if p["level"] < region["min_level"]:
        warn = f"\n\n⚠️ سطح تو پایین‌تر از حد توصیه‌شده‌ست (حداقل لول {region['min_level']}). مراقب باش!"

    await callback.message.edit_text(
        f"{region['label']}\nاین یه منطقه‌ی *خطرناکه*، هر لحظه ممکنه با موجودی روبه‌رو بشی.{warn}",
        parse_mode="Markdown",
        reply_markup=kb.region_menu_kb(region_key),
    )
    await callback.answer()


def _spawn_fight(user_id: int, region_key: str, is_boss: bool):
    region = REGIONS[region_key]
    template = region["boss"] if is_boss else random.choice(region["mobs"])
    ACTIVE_FIGHTS[user_id] = {
        "region": region_key,
        "is_boss": is_boss,
        "name": template["name"],
        "hp": template["hp"],
        "max_hp": template["hp"],
        "atk": template["atk"],
        "def": template["def"],
        "xp": template["xp"],
        "gold": template["gold"],
        "drop": template["drop"],
        "player_defending": False,
    }
    return ACTIVE_FIGHTS[user_id]


async def _send_fight_state(callback: CallbackQuery, fight, intro=""):
    user_id = callback.from_user.id
    p = db.get_player(user_id)
    has_potion = any(
        ITEMS.get(i["item_id"], {}).get("type") == "potion" for i in db.get_inventory(user_id)
    )
    text = (
        f"{intro}"
        f"👹 *{fight['name']}*\n❤️ {fight['hp']}/{fight['max_hp']}\n\n"
        f"🧙 تو: ❤️ {p['hp']}\n\n"
        f"چه کاری انجام می‌دی؟"
    )
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb.combat_kb(has_potion))


@router.callback_query(F.data.startswith("explore:"))
async def explore_region(callback: CallbackQuery):
    region_key = callback.data.split(":")[1]
    fight = _spawn_fight(callback.from_user.id, region_key, is_boss=False)
    await _send_fight_state(callback, fight, intro=f"⚔️ یه موجود سر راهت ظاهر شد!\n\n")
    await callback.answer()


@router.callback_query(F.data.startswith("boss:"))
async def fight_boss(callback: CallbackQuery):
    region_key = callback.data.split(":")[1]
    region = REGIONS[region_key]
    user_id = callback.from_user.id
    p = db.get_player(user_id)
    if p["level"] < region["boss"]["min_level"]:
        await callback.answer(
            f"سطح تو کافی نیست! برای این باس حداقل لول {region['boss']['min_level']} لازمه.",
            show_alert=True,
        )
        return
    fight = _spawn_fight(user_id, region_key, is_boss=True)
    await _send_fight_state(callback, fight, intro=f"👑 باس منطقه ظاهر شد! مراقب باش، خیلی قدرتمنده!\n\n")
    await callback.answer()


# ---------------------------------------------------------------------------
# مبارزه
# ---------------------------------------------------------------------------

@router.callback_query(F.data.startswith("fight:"))
async def fight_action(callback: CallbackQuery):
    user_id = callback.from_user.id
    fight = ACTIVE_FIGHTS.get(user_id)
    if not fight:
        await callback.answer("مبارزه‌ای در جریان نیست.", show_alert=True)
        return

    action = callback.data.split(":")[1]
    p = db.get_player(user_id)
    stats = db.effective_stats(user_id)
    log = ""

    if action == "flee":
        chance = 0.6
        if random.random() < chance:
            ACTIVE_FIGHTS.pop(user_id, None)
            await callback.message.edit_text(
                "🏃 با موفقیت فرار کردی!", reply_markup=kb.region_menu_kb(fight["region"])
            )
            await callback.answer()
            return
        else:
            log += "🏃 فرار ناموفق بود!\n\n"

    elif action == "item":
        items = db.get_inventory(user_id)
        potion = next((i for i in items if ITEMS.get(i["item_id"], {}).get("type") == "potion"), None)
        if not potion:
            await callback.answer("معجونی نداری!", show_alert=True)
            return
        item_def = ITEMS[potion["item_id"]]
        new_hp = min(stats["max_hp"], p["hp"] + item_def["heal"])
        db.set_hp(user_id, new_hp)
        db.remove_item(user_id, potion["item_id"], 1)
        p = db.get_player(user_id)
        log += f"🧪 از {item_def['name']} استفاده کردی و ❤️ {item_def['heal']} سلامتی ترمیم شد!\n\n"

    elif action == "defend":
        fight["player_defending"] = True
        log += "🛡 آماده‌ی دفاع شدی، ضربه‌ی بعدی رو کمتر می‌خوری.\n\n"

    elif action == "attack":
        dmg = max(1, stats["atk"] - fight["def"] + random.randint(-2, 3))
        fight["hp"] -= dmg
        log += f"🗡 تو {dmg} دمیج زدی! ({fight['name']}: {max(fight['hp'],0)}/{fight['max_hp']} ❤️)\n\n"

    # بررسی مرگ موجود
    if fight["hp"] <= 0:
        ACTIVE_FIGHTS.pop(user_id, None)
        gold_reward = random.randint(*fight["gold"])
        db.add_gold(user_id, gold_reward)
        level_ups = db.add_xp_and_check_levelup(user_id, fight["xp"])

        drops_text = ""
        for item_id, chance in fight["drop"]:
            if random.random() <= chance:
                db.add_item(user_id, item_id, 1)
                drops_text += f"\n🎁 {ITEMS[item_id]['name']} به دست آوردی!"

        result = (
            f"{log}🏆 *{fight['name']}* رو شکست دادی!\n\n"
            f"✨ تجربه: +{fight['xp']}\n💰 طلا: +{gold_reward}{drops_text}"
        )
        if level_ups:
            result += f"\n\n🎉 لول‌آپ! حالا لول {level_ups[-1]} هستی و آمارت بالا رفته."

        await callback.message.edit_text(result, parse_mode="Markdown", reply_markup=kb.region_result_kb(fight["region"]))
        await callback.answer()
        return

    # نوبت حمله‌ی موجود
    incoming = max(1, fight["atk"] - stats["def"] + random.randint(-2, 2))
    if action == "defend":
        incoming = max(1, incoming // 2)
    fight["player_defending"] = False

    new_hp = p["hp"] - incoming
    log += f"💢 {fight['name']} به تو {incoming} دمیج زد! (تو: {max(new_hp,0)} ❤️)"

    if new_hp <= 0:
        ACTIVE_FIGHTS.pop(user_id, None)
        gold_loss = min(p["gold"], random.randint(5, 15))
        db.add_gold(user_id, -gold_loss)
        db.set_hp(user_id, stats["max_hp"] // 2)
        db.set_location(user_id, "capital")
        await callback.message.edit_text(
            f"{log}\n\n☠️ شکست خوردی و بی‌هوش شدی!\n"
            f"نگهبانان پایتخت پیدات کردن و برت گردوندن.\n"
            f"💸 {gold_loss} طلا از دست دادی.",
            reply_markup=kb.main_menu_kb(),
        )
        await callback.answer()
        return

    db.set_hp(user_id, new_hp)
    await _send_fight_state(callback, fight, intro=log + "\n\n")
    await callback.answer()
