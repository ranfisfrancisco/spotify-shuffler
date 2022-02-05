import sys
import spotipy
import spotipy.util as util
from dotenv import load_dotenv

def get_auth(username, scope):
    token = util.prompt_for_user_token(username, scope)

    if not token:
        return None

    sp = spotipy.Spotify(auth=token)
    return sp
    
load_dotenv()

scope = 'user-library-read user-read-recently-played'

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print("Usage: %s username" % (sys.argv[0],))
    sys.exit()

sp = get_auth(username, scope)
if not sp:
    print("Can't get token for", username)
    sys.exit()

# Get Recently Played
results = sp.current_user_recently_played(limit=50)
recent_track_list = results['items']

# print(recent_track_list[0]['tracks].keys()) 
''' dict_keys(['album', 'artists', 'available_markets',
'disc_number', 'duration_ms', 'explicit', 'external_ids', 'external_urls', 'href', 'id', 'is_local', 'name', 'popularity', 'preview_url', 'track_number', 'type', 'uri'])'''

# Get Playlists
results = sp.current_user_playlists() 
''' dict_keys(['collaborative', 'description', 'external_urls', 'href', 'id', 'images',
  'name', 'owner', 'primary_color', 'public', 'snapshot_id', 'tracks', 'type', 'uri'])'''
playlists = results['items']

# for item in playlists:
#     print(item['name'], item['id'], item['tracks']['total'])

results = sp.user_playlist_tracks(playlist_id=playlists[0]['id'])
x = results['items']

for item in x:
    print(item['track']['name'])
