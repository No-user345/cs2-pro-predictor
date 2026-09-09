from django.shortcuts import render
from pathlib import Path
from django.http import HttpResponse
import sqlite3

from .predictor import predict_map

# Create your views here.


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "cs2_predictor.db"



def fantasy(request):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor() 
    cursor.execute(""" 
    SELECT hltv_id, name, image_url 
    FROM players ORDER BY name """)
    players = cursor.fetchall() 
    conn.close() 
    return render(request, "fantasyPage.html", { "players": players })





def fantasy_results(request):
    team_1_ids = request.POST.getlist("team_1")
    team_2_ids = request.POST.getlist("team_2")

    # Make sure both teams have 5 players
    if len(team_1_ids) != 5 or len(team_2_ids) != 5:
        return render(request, "fantasy_results.html", {
            "error": "You must select 5 players for each team."
        })

    # Make sure no player has been selected twice
    all_players = team_1_ids + team_2_ids

    if len(set(all_players)) != 10:
        return render(request, "fantasy_results.html", {
            "error": "A player cannot be selected twice."
        })

    # =========================
    # GET PLAYERS FROM DATABASE
    # =========================

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    placeholders = ",".join("?" for _ in all_players)

    cursor.execute(f"""
        SELECT hltv_id, name, image_url
        FROM players
        WHERE hltv_id IN ({placeholders})
    """, all_players)

    players = cursor.fetchall()

    conn.close()

    # Turn players into a dictionary
    player_data = {
        str(player["hltv_id"]): player
        for player in players
    }

    # Make sure all players actually exist
    if len(player_data) != 10:
        return render(request, "fantasy_results.html", {
            "error": "One or more selected players could not be found."
        })

    # =========================
    # BUILD TEAMS
    # =========================

    team_1 = [
        player_data[player_id]
        for player_id in team_1_ids
    ]

    team_2 = [
        player_data[player_id]
        for player_id in team_2_ids
    ]

    team_1ID = [
    player_id
    for player_id in team_1_ids
    ]

    team_2ID = [
        player_id
        for player_id in team_2_ids
    ]

    # =========================
    # MAP PREDICTIONS
    # =========================

    # TEMPORARY VALUES
    # Replace this with your ML prediction script later.

    predictions = {
        "Ancient": {
            "team1": 100,
            "team2": 0
        },

        "Anubis": {
            "team1": 100,
            "team2": 0
        },

        "Dust2": {
            "team1": 100,
            "team2": 0
        },

        "Inferno": {
            "team1": 100,
            "team2": 0
        },

        "Mirage": {
            "team1": 100,
            "team2": 0
        },

        "Nuke": {
            "team1": 100,
            "team2": 0
        },

        "Overpass": {
            "team1": 100,
            "team2": 0
        }
    }


    mirage_team_1_prob , mirage_team_2_prob= predict_map("Mirage", team_1ID, team_2ID)
    predictions["Mirage"]["team1"] = float(f"{mirage_team_1_prob * 100:.3g}")
    predictions["Mirage"]["team2"] = float(f"{mirage_team_2_prob * 100:.3g}")

    #Dust2_team_1_prob , Dust2_team_2_prob= predict_map("Dust2", team_1ID, team_2ID)
    #predictions["Dust2"]["team1"] = float(f"{Dust2_team_1_prob * 100:.3g}")
    #predictions["Dust2"]["team2"] = float(f"{Dust2_team_2_prob * 100:.3g}")

    #Anubis_team_1_prob , Anubis_team_2_prob= predict_map("Anubis", team_1ID, team_2ID)
    #predictions["Dust2"]["team1"] = float(f"{Anubis_team_1_prob * 100:.3g}")
    #predictions["Dust2"]["team2"] = float(f"{Anubis_team_2_prob * 100:.3g}")
    

    # =========================
    # RESULTS PAGE
    # =========================
    return render(request, "fantasy_resultsPage.html", {
        "team_1": team_1,
        "team_2": team_2,
        "predictions": predictions,
    })



