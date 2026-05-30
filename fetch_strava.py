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

# Alleen de velden bewaren die het dashboard gebruikt
clean = []
for a in activities:
    clean.append({
        "name": a.get("name"),
        "type": a.get("sport_type") or a.get("type"),
        "date": a.get("start_date_local"),
        "distance_km": round((a.get("distance") or 0) / 1000, 2),
        "moving_time_s": a.get("moving_time"),
        "elevation_m": a.get("total_elevation_gain"),
        "avg_hr": a.get("average_heartrate"),
    })

with open("activities.json", "w", encoding="utf-8") as f:
    json.dump(clean, f, ensure_ascii=False, indent=2)

print(f"Klaar. {len(clean)} activiteiten opgeslagen.")