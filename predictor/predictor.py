import sqlite3
import pickle
from django.conf import settings
from datetime import datetime
import os

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "cs2_predictor.db"

def get_player_stats( team_1_ids,team_2_ids, map_name, current_date, cursor):

    new_stats =[]
    all_ids = []

    for id in team_1_ids:
        all_ids.append(id)
    for id in team_2_ids:
        all_ids.append(id)


    for player_id in all_ids:
        cursor.execute("""
            SELECT
                pms.kills,
                pms.deaths,
                pms.rating
            FROM player_match_stats pms
            JOIN matches m
                ON pms.match_id = m.hltv_id
            WHERE pms.player_id = ?
            AND pms.map_name = ?
            AND m.date < ?
            ORDER BY m.date DESC
        """, (
            player_id,
            map_name,
            current_date,
        ))

        results = cursor.fetchall()
        if results:
            map_avg_kills = sum(row[0] for row in results) / len(results)
            map_avg_deaths = sum(row[1] for row in results) / len(results)
            map_avg_rating = sum(row[2] for row in results) / len(results)
        else:
            map_avg_kills = 0
            map_avg_deaths = 0
            map_avg_rating = 0

        map_exsperience = len(results)

        cursor.execute("""
            SELECT
                pms.kills,
                pms.deaths,
                pms.rating
            FROM player_match_stats pms
            JOIN matches m
                ON pms.match_id = m.hltv_id
            WHERE pms.player_id = ?
            AND pms.map_name = ?
            AND m.date < ?
            ORDER BY m.date DESC
            LIMIT 10
        """, (
            player_id,
            map_name,
            current_date,
        ))

        results = cursor.fetchall()
        if results:
            past_10_map_avg_kills = sum(row[0] for row in results) / len(results)
            past_10_map_avg_deaths = sum(row[1] for row in results) / len(results)
            past_10_map_avg_rating = sum(row[2] for row in results) / len(results)
        else: 
            past_10_map_avg_kills  = 0
            past_10_map_avg_deaths = 0
            past_10_map_avg_rating = 0
        
        cursor.execute("""
            SELECT
                pms.kills,
                pms.deaths,
                pms.rating
            FROM player_match_stats pms
            JOIN matches m
                ON pms.match_id = m.hltv_id
            WHERE pms.player_id = ?
            AND m.date < ?
            ORDER BY m.date DESC
        """, (
            player_id,
            current_date,
        ))

        results = cursor.fetchall()
        if results:
            avg_kills = sum(row[0] for row in results) / len(results)
            avg_deaths = sum(row[1] for row in results) / len(results)
            avg_rating = sum(row[2] for row in results) / len(results)
        else:
            avg_kills  = 0
            avg_deaths = 0
            avg_rating = 0

        overall_exsperience = len(results)

        cursor.execute("""
            SELECT
                pms.kills,
                pms.deaths,
                pms.rating
            FROM player_match_stats pms
            JOIN matches m
                ON pms.match_id = m.hltv_id
            WHERE pms.player_id = ?
            AND m.date < ?
            ORDER BY m.date DESC
            LIMIT 10
        """, (
            player_id,
            current_date,
        ))

        results = cursor.fetchall()
        if results:
            past_10_avg_kills = sum(row[0] for row in results) / len(results)
            past_10_avg_deaths = sum(row[1] for row in results) / len(results)
            past_10_avg_rating = sum(row[2] for row in results) / len(results)
        else:
            past_10_avg_kills  = 0
            past_10_avg_deaths = 0
            past_10_avg_rating = 0

        if map_exsperience == 0:
            map_avg_kills =  avg_kills * 0.7
            map_avg_deaths = avg_deaths / 0.7
            map_avg_rating = avg_rating * 0.7

            past_10_map_avg_kills  = past_10_avg_kills * 0.7
            past_10_map_avg_deaths = past_10_avg_deaths / 0.7
            past_10_map_avg_rating = past_10_avg_rating * 0.7

        new_stats.extend([
            map_avg_kills,
            map_avg_deaths,
            map_avg_rating,

            past_10_map_avg_kills,
            past_10_map_avg_deaths,
            past_10_map_avg_rating,

            avg_kills,
            avg_deaths,
            avg_rating,

            past_10_avg_kills,
            past_10_avg_deaths,
            past_10_avg_rating,

            map_exsperience,
            overall_exsperience
        ])

    return new_stats


def predict_map(map_name, team_1_ids, team_2_ids):
    current_date = datetime.now()

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()


    if map_name == "Mirage":
        model_file = "mirage_model.pkl"
    elif map_name == "Dust2":
         model_file = "Dust2_model.pkl"
    elif map_name == "Anubis":
        model_file = "Anubis_model.pkl"
        

    model_path = os.path.join(
        settings.BASE_DIR,
        "predictor_models",
        model_file
    )
    with open(model_path, "rb") as f:
                model = pickle.load(f)

    match_data = []



    match_data = get_player_stats(team_1_ids, team_2_ids, map_name, current_date, cursor)



    probabilities = model.predict_proba([match_data])

    team_1_probability = probabilities[0][1]
    team_2_probability = probabilities[0][0]

    return team_1_probability, team_2_probability


