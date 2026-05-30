import os, json, requests

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["REFRESH_TOKEN"]

# Verse toegang ophalen met de refresh token
token_resp = requests.post("https://www.strava.com/oauth/token", data={
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "refresh_token": REFRESH_TOKEN,
    "grant_type": "refresh_token",
})
token_resp.raise_for_status()
access_token = token_resp.json()["access_token"]

new_refresh = token_resp.json().get("refresh_token")
if new_refresh and new_refresh != REFRESH_TOKEN:
    print("LET OP: refresh token is veranderd. Zet deze in je GitHub Secret:", new_refresh)

headers = {"Authorization": f"Bearer {access_token}"}

# Alle activiteiten ophalen, 200 per pagina
activities = []
page = 1
while True:
    r = requests.get(
        "https://www.strava.com/api/v3/athlete/activities",
        headers=headers,
        params={"per_page": 200, "page": page},
    )
    r.raise_for_status()
    batch = r.json()
    if not batch:
        break
    activities.extend(batch)
    page += 1

# Alleen hardloopactiviteiten bewaren
RUN_TYPES = {"Run", "TrailRun", "VirtualRun"}

clean = []
for a in activities:
    sport = a.get("sport_type") or a.get("type")
    if sport not in RUN_TYPES:
        continue
    m = a.get("map") or {}
    clean.append({
        "id": a.get("id"),
        "name": a.get("name"),
        "type": sport,
        "date": a.get("start_date_local"),
        "distance_km": round((a.get("distance") or 0) / 1000, 3),
        "moving_time_s": a.get("moving_time"),
        "elapsed_time_s": a.get("elapsed_time"),
        "elevation_m": a.get("total_elevation_gain"),
        "avg_hr": a.get("average_heartrate"),
        "max_hr": a.get("max_heartrate"),
        "avg_speed": a.get("average_speed"),      # meter per seconde
        "max_speed": a.get("max_speed"),
        "avg_cadence": a.get("average_cadence"),  # voor runs: stappen per been per minuut
        "kudos": a.get("kudos_count"),
        "prs": a.get("pr_count"),
        "achievements": a.get("achievement_count"),
        "effort": a.get("suffer_score"),          # Relative Effort
        "polyline": m.get("summary_polyline"),
        "start_latlng": a.get("start_latlng"),
    })

with open("activities.json", "w", encoding="utf-8") as f:
    json.dump(clean, f, ensure_ascii=False, indent=2)

print(f"Klaar. {len(clean)} hardloopactiviteiten opgeslagen.")
