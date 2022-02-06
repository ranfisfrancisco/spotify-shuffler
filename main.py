import enum
import re
import sys
import spotipy
import spotipy.util as util
from dotenv import load_dotenv
from Shuffler import Shuffler

def get_auth(username, scope):
    token = util.prompt_for_user_token(username, scope)

    if not token:
        return None

    sp = spotipy.Spotify(auth=token)
    return sp

def select_playlist(playlists):
    # Note: User is choosing with 1 based indexes.
    for idx, item in enumerate(playlists):
        print(f'Index {idx+1} | Name {item["name"]} | # of Tracks {item["tracks"]["total"]} ')

    entry = None
    select_flag = 0
    while select_flag == 0:
        entry = input('Select Playlist by Index or Name?\n1. Index\n2. Name\n')
        if entry.isnumeric() and int(entry) == 1:
            select_flag = 1
        elif entry.isnumeric() and int(entry) == 2:
            select_flag = 2
        else:
            print("Invalid Input")
    

    entry = None
    if select_flag == 1:
        while True:
            entry = input('Enter index: ')
            if not entry.isnumeric():
                continue

            idx = int(entry)
            if idx > len(playlists) or idx < 1:
                print("Invalid Index")
                continue
            
            return playlists[idx-1] # One-indexed

    if select_flag == 2:
        while True:
            entry = input('Enter name: ')

            for item in playlists:
                if item['name'] == entry:
                    return item

            print("Did not find name!")
            

load_dotenv()

scope = 'user-library-read user-read-recently-played playlist-read-private streaming'

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

# print(recent_track_list[0]['tracks'].keys()) 
''' dict_keys(['album', 'artists', 'available_markets',
'disc_number', 'duration_ms', 'explicit', 'external_ids', 'external_urls', 'href', 'id', 'is_local', 'name', 'popularity', 'preview_url', 'track_number', 'type', 'uri'])'''

# Get Playlists
playlists = []
offset = 0
offset_difference = 50
while True:
    results = sp.current_user_playlists(offset=offset) 
    ''' dict_keys(['collaborative', 'description', 'external_urls', 'href', 'id', 'images',
    'name', 'owner', 'primary_color', 'public', 'snapshot_id', 'tracks', 'type', 'uri'])'''

    if not results['items']:
        break

    playlists.extend(results['items'])

    if len(results['items']) < offset_difference:
        break

    offset += offset_difference

# for item in playlists:
#     print(item['name'], item['id'], item['tracks']['total'])

# Select Playlist
playlist = select_playlist(playlists)

# Get Tracks of Selected Playlist
print("Getting Tracks from Playlist...")
playlist_tracks = []
offset = 0
offset_difference = 100
while True:
    results = sp.user_playlist_tracks(playlist_id=playlist['id'], offset=offset)

    if not results['items']:
        break

    playlist_tracks.extend(results['items'])

    if len(results['items']) < offset_difference:
        break

    offset += offset_difference

print("Done!")

# for item in playlist_tracks:
#     print(item['track']['name'])

# Get Shuffled List
shuffled_list = Shuffler.shuffle(playlist_tracks, recent_track_list, debug=True)

# Queue
print("Queueing songs...")
for song in shuffled_list:
    sp.add_to_queue(song['track']['uri'])

print("Done!")
