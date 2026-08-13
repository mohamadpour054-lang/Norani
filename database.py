# -*- coding: utf-8 -*-
"""
لایه‌ی دیتابیس (SQLite) — مدیریت بازیکن‌ها و اینونتوری
"""
import sqlite3
import random
from contextlib import closing

from game_data import CLASSES, ITEMS, LEVEL_UP_GROWTH, STARTING_GOLD, STARTING_ITEMS, xp_needed_for_level

DB_PATH = "eldoria.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with closing(get_conn()) as conn, conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                gender TEXT,
                class TEXT,
                level INTEGER DEFAULT 1,
                xp INTEGER DEFAULT 0,
                hp INTEGER,
                max_hp INTEGER,
                atk INTEGER,
                def INTEGER,
                gold INTEGER DEFAULT 0,
                location TEXT DEFAULT 'capital'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                item_id TEXT,
                quantity INTEGER DEFAULT 1,
                equipped INTEGER DEFAULT 0
            )
        """)


# ---------- بازیکن ----------

def player_exists(user_id: int) -> bool:
    with closing(get_conn()) as conn:
        row = conn.execute("SELECT 1 FROM players WHERE user_id=?", (user_id,)).fetchone()
        return row is not None


def create_player(user_id: int, name: str, gender: str, clas: str):
    base = CLASSES[clas]
    with closing(get_conn()) as conn, conn:
        conn.execute(
            """INSERT INTO players (user_id, name, gender, class, level, xp, hp, max_hp, atk, def, gold, location)
               VALUES (?, ?, ?, ?, 1, 0, ?, ?, ?, ?, ?, 'capital')""",
            (user_id, name, gender, clas, base["hp"], base["hp"], base["atk"], base["def"], STARTING_GOLD),
        )
    for item_id in STARTING_ITEMS:
        add_item(user_id, item_id, 1)


def get_player(user_id: int):
    with closing(get_conn()) as conn:
        row = conn.execute("SELECT * FROM players WHERE user_id=?", (user_id,)).fetchone()
        return dict(row) if row else None


def update_player(user_id: int, **fields):
    if not fields:
        return
    cols = ", ".join(f"{k}=?" for k in fields)
    values = list(fields.values()) + [user_id]
    with closing(get_conn()) as conn, conn:
        conn.execute(f"UPDATE players SET {cols} WHERE user_id=?", values)


def get_equipped_bonus(user_id: int):
    """مجموع بونوس آیتم‌های تجهیز شده (atk, def)"""
    atk_bonus, def_bonus = 0, 0
    with closing(get_conn()) as conn:
        rows = conn.execute(
            "SELECT item_id FROM inventory WHERE user_id=? AND equipped=1", (user_id,)
        ).fetchall()
    for r in rows:
        item = ITEMS.get(r["item_id"], {})
        atk_bonus += item.get("atk", 0)
        def_bonus += item.get("def", 0)
    return atk_bonus, def_bonus


def effective_stats(user_id: int):
    """آمار مؤثر بازیکن (پایه + بونوس تجهیزات)"""
    p = get_player(user_id)
    atk_bonus, def_bonus = get_equipped_bonus(user_id)
    return {
        "hp": p["hp"],
        "max_hp": p["max_hp"],
        "atk": p["atk"] + atk_bonus,
        "def": p["def"] + def_bonus,
    }


def add_xp_and_check_levelup(user_id: int, xp_gain: int):
    """تجربه اضافه می‌کنه و در صورت لازم لول‌آپ می‌کنه. لیست پیام‌های لول‌آپ رو برمی‌گردونه."""
    p = get_player(user_id)
    new_xp = p["xp"] + xp_gain
    level = p["level"]
    max_hp, atk, defense = p["max_hp"], p["atk"], p["def"]
    clas = p["class"]
    level_ups = []

    needed = xp_needed_for_level(level)
    while new_xp >= needed:
        new_xp -= needed
        level += 1
        growth = LEVEL_UP_GROWTH[clas]
        max_hp += growth["hp"]
        atk += growth["atk"]
        defense += growth["def"]
        level_ups.append(level)
        needed = xp_needed_for_level(level)

    with closing(get_conn()) as conn, conn:
        conn.execute(
            "UPDATE players SET xp=?, level=?, max_hp=?, atk=?, def=?, hp=? WHERE user_id=?",
            (new_xp, level, max_hp, atk, defense, max_hp if level_ups else p["hp"], user_id),
        )
    return level_ups


def add_gold(user_id: int, amount: int):
    with closing(get_conn()) as conn, conn:
        conn.execute("UPDATE players SET gold = gold + ? WHERE user_id=?", (amount, user_id))


def set_hp(user_id: int, hp: int):
    with closing(get_conn()) as conn, conn:
        conn.execute("UPDATE players SET hp=? WHERE user_id=?", (hp, user_id))


def set_location(user_id: int, location: str):
    with closing(get_conn()) as conn, conn:
        conn.execute("UPDATE players SET location=? WHERE user_id=?", (location, user_id))


# ---------- اینونتوری ----------

def add_item(user_id: int, item_id: str, qty: int = 1):
    with closing(get_conn()) as conn, conn:
        row = conn.execute(
            "SELECT id, quantity FROM inventory WHERE user_id=? AND item_id=? AND equipped=0",
            (user_id, item_id),
        ).fetchone()
        if row:
            conn.execute("UPDATE inventory SET quantity=? WHERE id=?", (row["quantity"] + qty, row["id"]))
        else:
            conn.execute(
                "INSERT INTO inventory (user_id, item_id, quantity, equipped) VALUES (?, ?, ?, 0)",
                (user_id, item_id, qty),
            )


def remove_item(user_id: int, item_id: str, qty: int = 1):
    with closing(get_conn()) as conn, conn:
        row = conn.execute(
            "SELECT id, quantity FROM inventory WHERE user_id=? AND item_id=? AND equipped=0",
            (user_id, item_id),
        ).fetchone()
        if not row:
            return False
        if row["quantity"] <= qty:
            conn.execute("DELETE FROM inventory WHERE id=?", (row["id"],))
        else:
            conn.execute("UPDATE inventory SET quantity=? WHERE id=?", (row["quantity"] - qty, row["id"]))
        return True


def get_inventory(user_id: int):
    with closing(get_conn()) as conn:
        rows = conn.execute(
            "SELECT * FROM inventory WHERE user_id=? ORDER BY equipped DESC, id", (user_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def equip_item(user_id: int, inventory_id: int):
    with closing(get_conn()) as conn, conn:
        row = conn.execute("SELECT * FROM inventory WHERE id=? AND user_id=?", (inventory_id, user_id)).fetchone()
        if not row:
            return False
        item = ITEMS.get(row["item_id"])
        if not item or item["type"] not in ("weapon", "armor"):
            return False
        # اول همه‌ی آیتم‌های همین نوع رو از حالت تجهیز خارج کن
        same_type_rows = conn.execute(
            "SELECT id, item_id FROM inventory WHERE user_id=? AND equipped=1", (user_id,)
        ).fetchall()
        for r in same_type_rows:
            other_item = ITEMS.get(r["item_id"])
            if other_item and other_item["type"] == item["type"]:
                conn.execute("UPDATE inventory SET equipped=0 WHERE id=?", (r["id"],))
        conn.execute("UPDATE inventory SET equipped=1 WHERE id=?", (inventory_id,))
        return True


def unequip_item(user_id: int, inventory_id: int):
    with closing(get_conn()) as conn, conn:
        conn.execute("UPDATE inventory SET equipped=0 WHERE id=? AND user_id=?", (inventory_id, user_id))
