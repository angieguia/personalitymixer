from flask import Flask, redirect, request, session, render_template
from spotipy.oauth2 import SpotifyOAuth
import os
import random
from dotenv import load_dotenv
import spotipy

load_dotenv()

personality = Flask(__name__)
personality.secret_key = 'angieguia'

sp_oauth = SpotifyOAuth(
    client_id="e643469dd21b4d269e6e2d79395d957f",
    client_secret="ce33152a3b99411e9595b4a96d2f33d3",
    redirect_uri="http://127.0.0.1:5000/callback",
    scope="playlist-modify-public"
)

song_lists = {
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
    "https://open.spotify.com/track/5JVbvCHX10U2pLa5DEqGav?si=3e72629fb64c48b9"
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
        "https://open.spotify.com/track/5UWwZ5lm5PKu6eKsHAGxOk?si=f2fdb9bf50404e67"
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
        "https://open.spotify.com/track/0LtOwyZoSNZKJWHqjzADpW?si=1cec79f222d04529"
    ]
}

scores = [
    {"Energetic and bold": 4, "Calm and collective": 2, "Spontaneous and playful": 3, "Quiet and mysterious": 1},
    {"Adventure in the mountains": 4, "Exploring the city": 3, "Cozy cabin in the woods": 2, "Chill day at the beach": 1},
    {"Fire - brave and driven": 4, "Water - calm and emotional": 2, "Air - curious and free": 3, "Earth - well-balanced and thoughtful": 1},
    {"Winter - calm": 2, "Spring - vibrant and lively": 3, "Summer - bright and fun": 4, "Fall - cozy and chill": 1},
    {"Minimal and classic": 1, "Expressive and artsy": 3, "Bold and trendy": 4, "Comfy and casual": 2},
    {"Hiking": 4, "Hanging out with friends": 3, "Chill at home": 2, "Working on a project": 1},
    {"Creating something new": 4, "Exploring new places": 3, "Socializing": 2, "Watching videos": 1},
    {"Kind and reliable": 2, "Outgoing and funny": 4, "Quiet and collective": 1, "Unique and unpredictable": 3}
]

@personality.route('/')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@personality.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code, as_dict=True)
    session['token'] = token_info['access_token']
    return redirect('/index')

def calculate_score(answers):
    total = 0
    for i, (key, value) in enumerate(answers.items()):
        total += scores[i][value]
    return total

def get_tracks_for_score(score):
    if score >= 28:
        seed_genres = "pop"
    elif score >= 20:
        seed_genres = "rock"
    else:
        seed_genres = "indie"

    print(f"Generated seed genre: {seed_genres}")

    shuffled_tracks = random.sample(song_lists[seed_genres], len(song_lists[seed_genres]))

    return shuffled_tracks

def create_playlist(score):
    token = session.get('token')
    if not token:
        print("No token in session")
        return None

    sp = spotipy.Spotify(auth=token)
    user_id = sp.current_user()['id']

    try:
        playlist = sp.user_playlist_create(user=user_id, name="Your Personality Mixer", public=True)
        track_uris = get_tracks_for_score(score)

        if track_uris:
            sp.playlist_add_items(playlist_id=playlist['id'], items=track_uris)
            print("tracks added")
        else:
            print("error")
        
        return playlist
    except spotipy.SpotifyException as e:
        print("error", e)
        return None

@personality.route("/index", methods=["GET", "POST"])
def index():
    questions = [
        "Pick a vibe: ",
        "What's your ideal vacation spot? ",
        "Which element best represents you? ",
        "What's your favorite season? ",
        "Which best describes your style?",
        "Pick a weekend activity: ",
        "How do you spend your free time?",
        "How would your friends best describe you?"
    ]

    options = [
        ["Energetic and bold", "Calm and collective", "Spontaneous and playful", "Quiet and mysterious"],
        ["Adventure in the mountains", "Exploring the city", "Cozy cabin in the woods", "Chill day at the beach"],
        ["Fire - brave and driven", "Water - calm and emotional", "Air - curious and free", "Earth - well-balanced and thoughtful"],
        ["Winter - calm", "Spring - vibrant and lively", "Summer - bright and fun", "Fall - cozy and chill"],
        ["Minimal and classic", "Expressive and artsy", "Bold and trendy", "Comfy and casual"],
        ["Hiking", "Hanging out with friends", "Chill at home", "Working on a project"],
        ["Creating something new", "Exploring new places", "Socializing", "Watching videos"],
        ["Kind and reliable", "Outgoing and funny", "Quiet and collective", "Unique and unpredictable"]
    ]

    if request.method == "POST":
        answers = request.form.to_dict()
        score = calculate_score(answers)
        playlist = create_playlist(score)
        return render_template("results.html", playlist_link=playlist["external_urls"]["spotify"])

    return render_template("index.html", questions=questions, options=options)

if __name__ == '__main__':
    personality.run(debug=True)