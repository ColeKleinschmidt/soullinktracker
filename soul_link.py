#!/usr/bin/env python3
"""Real-time Soul Link tracker using websockets with a simple GUI."""

import asyncio
import json
import os
import sys
import time
from typing import List, Dict, Tuple

import websockets
import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient

TEAM_FILE = "team_data.json"
PC_FILE = "pc_data.json"
LOG_FILE = "soul_link_log.json"
MONGO_URI = (
    "mongodb+srv://kleinschmidtcole:tWJvDpWJNiC8acAX@"
    "soullinktracker.v1n8usf.mongodb.net/"
)

# Initialize MongoDB client and collections
try:
    _mongo_client = MongoClient(MONGO_URI)
    _db = _mongo_client["Pokemon"]
    _pc_collection = _db["PC"]
    _party_collection = _db["Party"]
except Exception as _e:  # pragma: no cover - best effort to connect
    print(f"MongoDB connection failed: {_e}")
    _mongo_client = None
    _pc_collection = None
    _party_collection = None
GAMES = [
    "Diamond",
    "Pearl",
    "Platinum",
    "HeartGold",
    "SoulSilver",
    "Black",
    "White",
    "Black 2",
    "White 2",
]


def read_team() -> List[Dict]:
    """Read team data from TEAM_FILE."""
    if not os.path.exists(TEAM_FILE):
        return []
    try:
        with open(TEAM_FILE, "r") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return []


def read_pc() -> List[Dict]:
    """Read PC data from PC_FILE."""
    if not os.path.exists(PC_FILE):
        return []
    try:
        with open(PC_FILE, "r") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return []


def print_team(team: List[Dict], title: str) -> None:
    print(f"== {title} ==")
    if not team:
        print("(no data)")
        return
    for idx, mon in enumerate(team, start=1):
        species = mon.get("species")
        level = mon.get("level")
        hp = mon.get("hp")
        max_hp = mon.get("max_hp")
        fainted = mon.get("fainted")
        print(
            f"{idx}. species={species} level={level} hp={hp}/{max_hp} fainted={fainted}"
        )


def apply_soul_link(our_team: List[Dict], other_team: List[Dict]) -> None:
    """If a Pokémon in our team is fainted, mark the corresponding one in the
    other team as fainted as well."""
    for i, mon in enumerate(our_team):
        if mon.get("fainted") and i < len(other_team):
            other_team[i]["fainted"] = True


def append_log(history: List[Dict], our_team: List[Dict], other_team: List[Dict]) -> None:
    history.append({
        "timestamp": time.time(),
        "our_team": our_team,
        "partner_team": other_team,
    })
    with open(LOG_FILE, "w") as f:
        json.dump(history, f, indent=2)


def update_database(pc: List[Dict], party: List[Dict]) -> None:
    """Persist PC and party data to MongoDB."""
    if _mongo_client is None:
        return
    if _pc_collection is not None:
        _pc_collection.delete_many({})
        if pc:
            _pc_collection.insert_many(pc)
    if _party_collection is not None:
        _party_collection.delete_many({})
        if party:
            _party_collection.insert_many(party)


async def run_soul_link(uri: str) -> None:
    history: List[Dict] = []
    async with websockets.connect(uri) as ws:
        other_team: List[Dict] = []
        while True:
            our_team = read_team()
            pc_data = read_pc()
            update_database(pc_data, our_team)
            await ws.send(json.dumps(our_team))
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=1)
                other_team = json.loads(msg)
            except asyncio.TimeoutError:
                # no update from partner
                pass
            apply_soul_link(our_team, other_team)
            os.system("clear")
            print_team(our_team, "Your Team")
            print()
            print_team(other_team, "Partner Team")
            append_log(history, our_team, other_team)
            await asyncio.sleep(2)


def get_user_config() -> Tuple[str, str]:
    """Display a simple Tkinter dialog to get connection code and game."""
    result: Tuple[str, str] = ("", "")

    root = tk.Tk()
    root.title("Soul Link Setup")

    tk.Label(root, text="Connection Code (5 digits):").grid(row=0, column=0, sticky="w")
    code_var = tk.StringVar()
    tk.Entry(root, textvariable=code_var).grid(row=0, column=1, padx=5, pady=5)

    tk.Label(root, text="Game:").grid(row=1, column=0, sticky="w")
    game_var = tk.StringVar(value=GAMES[0])
    ttk.Combobox(root, textvariable=game_var, values=GAMES, state="readonly").grid(
        row=1, column=1, padx=5, pady=5
    )

    def start():
        code = code_var.get()
        if not code.isdigit() or len(code) != 5:
            messagebox.showerror("Error", "Connection code must be exactly 5 digits.")
            return
        nonlocal result
        result = (code, game_var.get())
        root.destroy()

    tk.Button(root, text="Start", command=start).grid(row=2, column=0, columnspan=2, pady=10)

    root.mainloop()
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Soul Link WebSocket client")
    parser.add_argument(
        "--url",
        default="ws://localhost:8765",
        help="WebSocket server base URL",
    )
    args = parser.parse_args()

    code, game = get_user_config()
    if not code:
        print("No connection code provided, exiting.")
        sys.exit(0)

    url = args.url.rstrip("/") + "/" + code
    print(f"Connecting to {url} for {game}...")

    try:
        asyncio.run(run_soul_link(url))
    except KeyboardInterrupt:
        print("Exiting...")
