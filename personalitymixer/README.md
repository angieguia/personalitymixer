# Personality Mixer

Answer 8 quick questions and get a Spotify playlist that matches your personality.
Songs are searched live on Spotify by genre (pop, rock or indie), so playlists change from run to run.

## Setup

1. Install the packages:

   ```
   pip install -r requirements.txt
   ```

2. Create an app at https://developer.spotify.com/dashboard and add this Redirect URI:

   ```
   http://127.0.0.1:5000/callback
   ```

   In the app's User Management, add the email of every Spotify account that will log in
   (development-mode apps only work for allowlisted users, and the app owner needs Spotify Premium).

3. Copy `spotipy.env.example` to `spotipy.env` and fill in your Client ID and Client Secret.
   Never commit `spotipy.env`.

4. Run it:

   ```
   python personalitymixer.py
   ```

   Then open http://127.0.0.1:5000

## Project layout

```
personalitymixer.py     Flask app: login, scoring, song search, playlist creation
templates/              base.html, index.html (quiz), results.html, error.html
spotipy.env.example     template for your credentials
```
