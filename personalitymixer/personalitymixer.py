from flask import Flask, redirect, request, session, render_template
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import MemoryCacheHandler
import os
import random
from datetime import date
from pathlib import Path
from dotenv import load_dotenv
import spotipy

# Reads spotipy.env from the same folder as this script
load_dotenv(Path(__file__).parent / "spotipy.env")

personality = Flask(__name__)
personality.secret_key = os.getenv("FLASK_SECRET_KEY") or os.urandom(24)

# Credentials come from spotipy.env (next to this file), which should contain:
#   SPOTIPY_CLIENT_ID=...
#   SPOTIPY_CLIENT_SECRET=...
#   SPOTIPY_REDIRECT_URI=http://127.0.0.1:5000/callback
# Optional: FLASK_SECRET_KEY=any-long-random-string
sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:5000/callback"),
    scope="playlist-modify-public",
    cache_handler=MemoryCacheHandler(),  # tokens live in the login session, not in a .cache file
)

# ---------------------------------------------------------------------------
# Song sourcing
# ---------------------------------------------------------------------------
# Songs are pulled live from Spotify's search using the genre: filter, with a
# random genre tag, release-year window and result offset on every run so two
# quizzes rarely produce the same playlist.
#
# Spotify's Feb 2026 API changes matter here:
#   - /recommendations was removed in Nov 2024, so search is the way to go
#   - search now returns at most 10 results per request, so we make several calls

TRACKS_PER_PLAYLIST = 20   # songs in the finished playlist
MIN_WEB_TRACKS = 10        # below this, top up from the fallback lists
SEARCH_LIMIT = 10          # Spotify's per-request max for search
MAX_SEARCH_CALLS = 8       # upper bound on API calls per playlist
CANDIDATE_TARGET = 40      # stop searching once we have this many candidates
MAX_PER_ARTIST = 2         # keeps one artist from taking over the playlist
REMEMBER_LAST = 60         # how many recent songs to avoid repeating per browser

# Each bucket searches several related genre tags, plus a range of release years
GENRES = {
    "pop":   {"tags": ["pop", "dance pop", "electropop"],
              "years": (2000, date.today().year)},
    "rock":  {"tags": ["rock", "alternative rock", "classic rock", "hard rock"],
              "years": (1970, date.today().year)},
    "indie": {"tags": ["indie", "indie pop", "indie rock", "bedroom pop"],
              "years": (2005, date.today().year)},
}

# Only used if the live search fails or returns too little
FALLBACK_SONGS = {
    "pop": [
        "https://open.spotify.com/track/4LRPiXqCikLlN15c3yImP7",
        "https://open.spotify.com/track/6UelLqGlWMcVH1E5c4H7lY",
        "https://open.spotify.com/track/4ZtFanR9U6ndgddUvNcjcG",
        "https://open.spotify.com/track/463CkQjx2Zk1yXoBuierM9",
        "https://open.spotify.com/track/1cKHdTo9u0ZymJdPGSh6nq?si=4af6b3e43c9e413c",
        "https://open.spotify.com/track/7BRD7x5pt8Lqa1eGYC4dzj?si=20b319bdaf9c49ef",
        "https://open.spotify.com/track/4wTvw1dBiPXNiHTh0zzpcI?si=48deee927cfa445d",
        "https://open.spotify.com/track/0q6LuUqGLUiCPP1cbdwFs3?si=00c03813709048db",
        "https://open.spotify.com/track/69uxyAqqPIsUyTO8txoP2M?si=54e773eaceec4221",
        "https://open.spotify.com/track/0DiWol3AO6WpXZgp0goxAV?si=0ce81bdb9ba74aa8",
        "https://open.spotify.com/track/3L7RtEcu1Hw3OXrpnthngx?si=9a480eca40a84387",
        "https://open.spotify.com/track/19fKJrO9XdOf6Xla2QHecO?si=5531a0083a1c4a07",
        "https://open.spotify.com/track/5GXAXm5YOmYT0kL5jHvYBt?si=356adfd2bc584027",
        "https://open.spotify.com/track/7tr2za8SQg2CI8EDgrdtNl?si=4c2e932adabb422e",
        "https://open.spotify.com/track/7LcfRTgAVTs5pQGEQgUEzN?si=e21f30e0e2fb4f8d",
        "https://open.spotify.com/track/5JVbvCHX10U2pLa5DEqGav?si=3e72629fb64c48b9",
    ],
    "rock": [
        "https://open.spotify.com/track/7tFiyTwD0nx5a1eklYtX2J",
        "https://open.spotify.com/track/5CQ30WqJwcep0pYcV4AMNc",
        "https://open.spotify.com/track/7o2CTH4ctstm8TNelqjb51",
        "https://open.spotify.com/track/07q0QVgO56EorrSGHC48y3?si=7c8995de76c446e7",
        "https://open.spotify.com/track/34iOH7LY3vme5rQxsVILZ4?si=e129d273106d465d",
        "https://open.spotify.com/track/0YJ9FWWHn9EfnN0lHwbzvV?si=7493afcd55b54194",
        "https://open.spotify.com/track/0pQskrTITgmCMyr85tb9qq?si=4d038353f9324503",
        "https://open.spotify.com/track/4l0HxP8wm5iWHqo9myvFsm?si=7c87bf7a3927410a",
        "https://open.spotify.com/track/72Z17vmmeQKAg8bptWvpVG?si=3ce7f09f997c4c55",
        "https://open.spotify.com/track/7Jh1bpe76CNTCgdgAdBw4Z?si=68eac214d5544d3b",
        "https://open.spotify.com/track/0oxYB9GoOIDrdzniNdKC44?si=66855569d42e4fa0",
        "https://open.spotify.com/track/6JzzI3YxHCcjZ7MCQS2YS1?si=88fb7d73ec724afd",
        "https://open.spotify.com/track/2id8E4WvczfKHB4LHI7Np3?si=4edb6a5399354b95",
        "https://open.spotify.com/track/1D6NMs2Zq9PI8dgPtOGbtA?si=764aed5688d14474",
        "https://open.spotify.com/track/70LcF31zb1H0PyJoS1Sx1r?si=9cbab54a10d64ddb",
        "https://open.spotify.com/track/5GjPQ0eI7AgmOnADn1EO6Q?si=4ba1ab0e37a54147",
        "https://open.spotify.com/track/5ruzrDWcT0vuJIOMW7gMnW?si=1f44e7b4cb51432f",
        "https://open.spotify.com/track/5UWwZ5lm5PKu6eKsHAGxOk?si=f2fdb9bf50404e67",
    ],
    "indie": [
        "https://open.spotify.com/track/6K4t31amVTZDgR3sKmwUJJ?si=37bb3b0eba504fc4",
        "https://open.spotify.com/track/2tznHmp70DxMyr2XhWLOW0?si=b93a95895ba24467",
        "https://open.spotify.com/track/6dBUzqjtbnIa1TwYbyw5CM?si=8f9d4d44013c4e64",
        "https://open.spotify.com/track/37pKTyMwalomKCZjxTc2QZ?si=283dee2469f04667",
        "https://open.spotify.com/track/3xKsf9qdS1CyvXSMEid6g8?si=fe40f28aec9e4887",
        "https://open.spotify.com/track/0InIeZW4P6VO7dUGRM4AKH?si=8cd52a6c3a9e4a54",
        "https://open.spotify.com/track/45dAw6GXEsogcDF3NUgj3O?si=cd3cbd01a559483f",
        "https://open.spotify.com/track/4S4QJfBGGrC8jRIjJHf1Ka?si=4d92c421ab944736",
        "https://open.spotify.com/track/6uVZddXkgQIArp8myEHs4x?si=e48285b6c4d74c16",
        "https://open.spotify.com/track/3siwsiaEoU4Kuuc9WKMUy5?si=006186c85721490d",
        "https://open.spotify.com/track/1LzNfuep1bnAUR9skqdHCK?si=162b16458eb8440b",
        "https://open.spotify.com/track/2KufM8PiQY4i52XhRL96Fd?si=fb85c846b0ba41c9",
        "https://open.spotify.com/track/3poJLRLGViMX3gicX9UYtD?si=b08faa2b7c914844",
        "https://open.spotify.com/track/4sIFi8LpJWPvI5xviWFyA6?si=f84f55bef4f44020",
        "https://open.spotify.com/track/5TxRUOsGeWeRl3xOML59Ai?si=e80584cd964a4133",
        "https://open.spotify.com/track/0LtOwyZoSNZKJWHqjzADpW?si=1cec79f222d04529",
    ],
}

# Shown on the results page
GENRE_BLURBS = {
    "pop":   "Your answers point to pop: bright, bold and made to sing along to.",
    "rock":  "Your answers point to rock: driven, loud and full of momentum.",
    "indie": "Your answers point to indie: thoughtful, a little mysterious and made for headphones.",
}

# ---------------------------------------------------------------------------
# Quiz content
# ---------------------------------------------------------------------------

QUESTIONS = [
    "Pick a vibe: ",
    "What's your ideal vacation spot? ",
    "Which element best represents you? ",
    "What's your favorite season? ",
    "Which best describes your style?",
    "Pick a weekend activity: ",
    "How do you spend your free time?",
    "How would your friends best describe you?",
]

OPTIONS = [
    ["Energetic and bold", "Calm and collective", "Spontaneous and playful", "Quiet and mysterious"],
    ["Adventure in the mountains", "Exploring the city", "Cozy cabin in the woods", "Chill day at the beach"],
    ["Fire - brave and driven", "Water - calm and emotional", "Air - curious and free", "Earth - well-balanced and thoughtful"],
    ["Winter - calm", "Spring - vibrant and lively", "Summer - bright and fun", "Fall - cozy and chill"],
    ["Minimal and classic", "Expressive and artsy", "Bold and trendy", "Comfy and casual"],
    ["Hiking", "Hanging out with friends", "Chill at home", "Working on a project"],
    ["Creating something new", "Exploring new places", "Socializing", "Watching videos"],
    ["Kind and reliable", "Outgoing and funny", "Quiet and collective", "Unique and unpredictable"],
]

scores = [
    {"Energetic and bold": 4, "Calm and collective": 2, "Spontaneous and playful": 3, "Quiet and mysterious": 1},
    {"Adventure in the mountains": 4, "Exploring the city": 3, "Cozy cabin in the woods": 2, "Chill day at the beach": 1},
    {"Fire - brave and driven": 4, "Water - calm and emotional": 2, "Air - curious and free": 3, "Earth - well-balanced and thoughtful": 1},
    {"Winter - calm": 2, "Spring - vibrant and lively": 3, "Summer - bright and fun": 4, "Fall - cozy and chill": 1},
    {"Minimal and classic": 1, "Expressive and artsy": 3, "Bold and trendy": 4, "Comfy and casual": 2},
    {"Hiking": 4, "Hanging out with friends": 3, "Chill at home": 2, "Working on a project": 1},
    {"Creating something new": 4, "Exploring new places": 3, "Socializing": 2, "Watching videos": 1},
    {"Kind and reliable": 2, "Outgoing and funny": 4, "Quiet and collective": 1, "Unique and unpredictable": 3},
]

# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------

@personality.route('/')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@personality.route('/callback')
def callback():
    code = request.args.get('code')
    if request.args.get('error') or not code:
        return render_template(
            "error.html",
            title="Spotify login didn't finish",
            message="We need permission to create a playlist in your account. Log in again and choose Agree.",
            retry_url="/",
            retry_label="Log in with Spotify",
        )
    token_info = sp_oauth.get_access_token(code, as_dict=True)
    session['token'] = token_info['access_token']
    return redirect('/index')

# ---------------------------------------------------------------------------
# Scoring and track selection
# ---------------------------------------------------------------------------

def calculate_score(answers):
    """answers is a list of 8 answer strings, in question order."""
    return sum(scores[i][answer] for i, answer in enumerate(answers))


def genre_for_score(score):
    if score >= 28:
        return "pop"
    elif score >= 20:
        return "rock"
    return "indie"


def url_to_uri(url):
    track_id = url.split("/track/")[1].split("?")[0]
    return f"spotify:track:{track_id}"


def fetch_tracks_from_web(sp, genre):
    """Search Spotify for tracks in this genre. Returns a list of
    (uri, track_id, artist_id) tuples, already de-duplicated."""
    config = GENRES[genre]
    first_year, last_year = config["years"]
    candidates = {}

    for _ in range(MAX_SEARCH_CALLS):
        if len(candidates) >= CANDIDATE_TARGET:
            break

        tag = random.choice(config["tags"])
        start = random.randint(first_year, last_year)
        end = min(start + random.randint(2, 6), last_year)
        query = f'genre:"{tag}" year:{start}-{end}'

        items = []
        try:
            for offset in (random.randint(0, 100), 0):
                results = sp.search(q=query, type="track", limit=SEARCH_LIMIT, offset=offset)
                items = results.get("tracks", {}).get("items", [])
                if items or offset == 0:
                    break  # got results, or already tried the start of the list
        except spotipy.SpotifyException as e:
            print("Search call failed, keeping what we have so far:", e)
            break

        for track in items:
            if not track or not track.get("uri") or not track.get("artists"):
                continue
            candidates[track["id"]] = (track["uri"], track["id"], track["artists"][0]["id"])

    return list(candidates.values())


def get_tracks_for_score(sp, score):
    genre = genre_for_score(score)
    print(f"Genre for score {score}: {genre}")

    recent = set(session.get("recent_tracks", []))

    try:
        candidates = fetch_tracks_from_web(sp, genre)
    except Exception as e:  # network trouble, rate limit, API change, etc.
        print("Live search failed, using fallback songs:", e)
        candidates = []

    # Prefer songs this person hasn't gotten recently, then cap songs per artist
    random.shuffle(candidates)
    candidates.sort(key=lambda c: c[1] in recent)  # stable sort: unseen songs first

    picked, per_artist = [], {}
    for uri, track_id, artist_id in candidates:
        if per_artist.get(artist_id, 0) >= MAX_PER_ARTIST:
            continue
        per_artist[artist_id] = per_artist.get(artist_id, 0) + 1
        picked.append((uri, track_id))
        if len(picked) == TRACKS_PER_PLAYLIST:
            break

    # If the web didn't give us enough, top up from the built-in list
    if len(picked) < MIN_WEB_TRACKS:
        print(f"Only {len(picked)} live tracks, topping up from fallback list")
        have = {uri for uri, _ in picked}
        fallback = [url_to_uri(u) for u in FALLBACK_SONGS[genre]]
        random.shuffle(fallback)
        for uri in fallback:
            if uri not in have:
                picked.append((uri, uri.split(":")[-1]))
            if len(picked) == TRACKS_PER_PLAYLIST:
                break

    # Remember these so the next quiz on this browser doesn't repeat them
    session["recent_tracks"] = (list(recent) + [tid for _, tid in picked])[-REMEMBER_LAST:]

    random.shuffle(picked)
    return [uri for uri, _ in picked]


def create_playlist(score):
    """Returns (playlist, problem). problem is None on success, otherwise
    "login" (session expired) or a message to show the user."""
    token = session.get('token')
    if not token:
        return None, "login"

    sp = spotipy.Spotify(auth=token)

    try:
        # Spotify removed POST /users/{id}/playlists and POST /playlists/{id}/tracks in
        # Feb 2026 (now /me/playlists and /playlists/{id}/items), so these two calls go
        # straight to the new endpoints instead of using spotipy's older helper methods.
        playlist = sp._post("me/playlists", payload={
            "name": "Your Personality Mixer",
            "public": True,
            "description": "Made by Personality Mixer",
        })

        track_uris = get_tracks_for_score(sp, score)
        sp._post(f"playlists/{playlist['id']}/items", payload={"uris": track_uris})
        print(f"{len(track_uris)} tracks added")

        return playlist, None
    except spotipy.SpotifyException as e:
        print("Spotify error:", e)
        if e.http_status == 401:
            return None, "login"
        if e.http_status == 403:
            return None, ("Spotify refused the request. Make sure the account you logged in with is added "
                          "under User Management in your Spotify developer dashboard, and that the app "
                          "owner has Spotify Premium.")
        return None, "Spotify had a problem creating your playlist. Try again in a moment."

# ---------------------------------------------------------------------------
# Quiz page
# ---------------------------------------------------------------------------

def render_quiz(error=None):
    return render_template("index.html", questions=QUESTIONS, options=OPTIONS, error=error)


@personality.route("/index", methods=["GET", "POST"])
def index():
    if not session.get('token'):
        return redirect('/')

    if request.method == "POST":
        # Read answers by question number so scoring never depends on form order
        answers = [request.form.get(f"q{i}") for i in range(len(scores))]
        if any(answer not in scores[i] for i, answer in enumerate(answers)):
            return render_quiz(error="Please answer every question.")

        score = calculate_score(answers)
        playlist, problem = create_playlist(score)

        if problem == "login":
            session.pop('token', None)
            return redirect('/')
        if problem:
            return render_template("error.html", message=problem)

        return render_template(
            "results.html",
            playlist_link=playlist["external_urls"]["spotify"],
            playlist_id=playlist["id"],
            blurb=GENRE_BLURBS[genre_for_score(score)],
        )

    return render_quiz()


if __name__ == '__main__':
    personality.run(debug=True)
