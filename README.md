Personality Mixer is a small Flask web app. You log in with Spotify, take a short quiz about your vibe, favorite season, weekend plans and more, and the app creates a new public playlist in your Spotify account. Songs are searched live on Spotify each time so you'll get a completely unique playlist

Setup
1. Get the code and install the packages

Open the project folder in a terminal (in VS Code: Terminal, then New Terminal) and run:

pip install -r requirements.txt

On Mac or Linux you may need pip3 instead of pip.

2. Create a Spotify developer app
Go to https://developer.spotify.com/dashboard and create an app.
In the app's settings, add this Redirect URI exactly as written:
   http://127.0.0.1:5000/callback
Under User Management, add the name and email of every Spotify account that will log in to the app, including your own. Accounts that aren't on this list get a 403 error.
Copy the Client ID and Client Secret from the app's settings page.
3. Add your credentials

Copy spotipy.env.example to a new file named spotipy.env in the same folder, then fill it in:

SPOTIPY_CLIENT_ID=your_client_id_here
SPOTIPY_CLIENT_SECRET=your_client_secret_here
SPOTIPY_REDIRECT_URI=http://127.0.0.1:5000/callback
FLASK_SECRET_KEY=any-long-random-string
No spaces around = and no quotes.
FLASK_SECRET_KEY is optional. Without it, the app makes a random one each time it starts.
On Windows, make sure the file is really named spotipy.env and not spotipy.env.txt (in File Explorer: View, then Show, then File name extensions).
Never upload spotipy.env to GitHub. It's already listed in .gitignore.
4. Run it
python personalitymixer.py

Then open http://127.0.0.1:5000 in your browser. Use 127.0.0.1 and not localhost, or the Spotify login may not match your Redirect URI.

You'll be sent to Spotify to log in, then land on the quiz. Press Ctrl+C in the terminal to stop the server.
