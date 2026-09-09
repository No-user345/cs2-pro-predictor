import sqlite3
import pickle
from django.conf import settings
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
                AVG(kills),
                AVG(deaths),
                AVG(rating),
                COUNT(*)
            FROM player_match_stats 
            WHERE player_id = ?
            AND map_name = ?
        """, (
            player_id,
            map_name,
        ))

        map_avg_kills, map_avg_deaths, map_avg_rating, map_experience = cursor.fetchone()

        map_avg_kills = map_avg_kills or 0
        map_avg_deaths = map_avg_deaths or 0
        map_avg_rating = map_avg_rating or 0


        cursor.execute("""
            SELECT
                AVG(kills),
                AVG(deaths),
                AVG(rating)
            FROM (
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
            )
        """, (
            player_id,
            map_name,
            current_date,
        ))

        past_10_map_avg_kills, past_10_map_avg_deaths, past_10_map_avg_rating = cursor.fetchone()

        past_10_map_avg_kills = past_10_map_avg_kills or 0
        past_10_map_avg_deaths = past_10_map_avg_deaths or 0
        past_10_map_avg_rating = past_10_map_avg_rating or 0
        
        cursor.execute("""
            SELECT
                AVG(kills),
                AVG(deaths),
                AVG(rating),
                COUNT(*)
            FROM player_match_stats 
            WHERE player_id = ?
        """, (
            player_id,
        ))

        avg_kills, avg_deaths, avg_rating, overall_experience = cursor.fetchone()

        avg_kills = avg_kills or 0
        avg_deaths = avg_deaths or 0
        avg_rating = avg_rating or 0


        cursor.execute("""
            SELECT
                AVG(kills),
                AVG(deaths),
                AVG(rating)
            FROM (
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
            )
        """, (
            player_id,
            current_date,
        ))

        past_10_avg_kills, past_10_avg_deaths, past_10_avg_rating = cursor.fetchone()

        past_10_avg_kills = past_10_avg_kills or 0
        past_10_avg_deaths = past_10_avg_deaths or 0
        past_10_avg_rating = past_10_avg_rating or 0

        if map_experience == 0:
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

            map_experience,
            overall_experience
        ])

    return new_stats


def predict_map(map_name, team_1_ids, team_2_ids):

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



    match_data = get_player_stats(team_1_ids, team_2_ids, map_name,  cursor)


    probabilities = model.predict_proba([match_data])

    team_1_probability = probabilities[0][1]
    team_2_probability = probabilities[0][0]

    connection.close()

    return team_1_probability, team_2_probability




