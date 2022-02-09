import sys
import time
import spotipy
import spotipy.util as util
from dotenv import load_dotenv
from Shuffler import Shuffler

def help():
    """Returns help doc."""
    return '''Flags: \n\
    -u : Argument after this flag is taken as the username. Program will ask for username if not provided. Example: python main.py -u usernameHere
    -p : Argument after this flag is taken as the playlist to be queued. Program will as for playlist name if not provided. Example: python main.py -playlist rock
    -l : Argument after this flag is taken as the max number of songs to be queued. Program will as for limit if not provided. Example: python main.py -l 20
    -ndar: Signfies that the shuffler should avoid having the same artist play twice in a row (no double artist)
    -ndal: Signfies that the shuffler should avoid having the same artist play twice in a row (no double album)
        
Troubleshooting:
    Make sure a device is actively connected to Spotify/playing or the queue attempt will fail.'''

def get_auth(username, scope) -> spotipy.Spotify:
    """Get authentication and crate Spotify object for API interaction

    Return spotipy.Spotify object if successful, None otherwise.

    Arguments:

    username -- string containing the Spotify username
    scope -- string containing desired permissions (see Spotify API documentation)"""

    token = util.prompt_for_user_token(username, scope)

    if not token:
        return None

    sp = spotipy.Spotify(auth=token)
    return sp

def select_playlist(playlists, selected_playlist_name=None):
    """Get dictionary object for a playlist chosen by the user from a list of playlists.

    Returns dictionary with the playlist data.

    Arguments:

    playlists -- list of playlists obtained through Spotify API

    selected_playlist_name -- if the user has already entered the desired playlist name,
    this will be used to find the playlist first (default None)
    """

    if selected_playlist_name:
        for item in playlists:
            if item['name'] == selected_playlist_name:
                return item

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
            
def get_playlists(sp):
    """Gets a user's playlists.
    
    Assumes spotipy.spotify object passed in is already authenticated with a user.
    
    Arguments:
    
    sp - spotipy.Spotify object authenticated with user"""
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

    return playlists

def get_tracks_from_playlist(sp, playlist):
    """Get tracks from a given playlist
    
    Assumes spotipy.Spotify object passed in is already authenticated with a user

    Returns list of track dictionary objects from Spotify API. Returns empty list if playlist is empty
    or the playlist was not found.
    
    Arguments:
    
    sp -- spotipy.Spotify object authenticated with a user

    playlist -- dictionary object of data from Spotify API for a particular playlist"""

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
    
    return playlist_tracks

def get_queue_limit():
    '''Prompt user to enter queue limit.
    
    Returns positive integer that is the queue limit
    or None if no limit is desired or correctly entered.'''
    queue_limit = None

    entry = input('Limit number of songs queued?\nEnter number or nothing\n')
    if entry.isnumeric():
        queue_limit = int(entry)

    if queue_limit < 0:
        queue_limit = None

    return queue_limit

def parse_args(argv: list) -> tuple:
    '''Parse command line arguments and return variables and flags as necessary.
    
    Returns tuple of username, playlist_name, queue_limit, no_double_artist_flag, no_double_album_flag

    Arguments:
    
    argv -- command line arguments as list. Same as sys.argv'''
    username = None
    playlist_name = None
    queue_limit = None
    no_double_artist_flag = False
    no_double_album_flag = False

    for idx, arg in enumerate(argv):
        try:
            if arg == '-u':
                username = argv[idx+1]
            elif arg == '-p':
                playlist_name = argv[idx+1]
            elif arg == '-l':
                if not argv[idx+1].isnumeric():
                    sys.exit(f"Queue limit must be integer")

                queue_limit = int(argv[idx+1])

                if queue_limit < 1:
                    sys.exit(f"Queue limit must be greater than 0.")
            elif arg == '-ndar':
                no_double_artist_flag = True
            elif arg == '-ndal':
                no_double_album_flag = True
            elif arg == "-help" or arg == "-h":
                sys.exit(help())
        
        except IndexError:
            sys.exit(f"Each -u, -p and -l must have an argument after it.")

    return (username, playlist_name, queue_limit, no_double_artist_flag, no_double_album_flag)

def main(argv):
    '''Shuffle songs in playlist and add to user's play queue.
    
    Arguments:
    
    argv -- same as sys.argv
    
    Supports several flags through argv:
    
    -u -- argument following this is the user's username. Will be prompted for this if not provided.
    
    -p -- argument following this is the desired playlist to shuffle. Will be prompted for this if not provided.
    
    -l -- argument following this is the maximum number of songs that should be queued. Will be prompted for this if not provided
    
    -ndar -- flag that makes shuffler avoid playing the same artist twice in a row.

    -ndal -- flag that makes shuffler avoid playing the same album twice in a row.'''

    load_dotenv()

    scope = 'user-library-read user-read-recently-played playlist-read-private streaming'

    username, playlist_name, queue_limit, \
         no_double_artist_flag, no_double_album_flag = parse_args(argv)

    if username == None:
        username = input("Enter Spotify Username: ")

    sp = get_auth(username, scope)
    if not sp:
        print("Can't get token for ", username)
        sys.exit()

    # Get Recently Played
    results = sp.current_user_recently_played(limit=50)
    recent_track_list = results['items']

    # print(recent_track_list[0]['tracks'].keys()) 
    ''' dict_keys(['album', 'artists', 'available_markets',
    'disc_number', 'duration_ms', 'explicit', 'external_ids', 'external_urls', 'href', 'id', 'is_local', 'name', 'popularity', 'preview_url', 'track_number', 'type', 'uri'])'''

    # Get Playlists
    playlists = get_playlists(sp)

    # for item in playlists:
    #     print(item['name'], item['id'], item['tracks']['total'])

    # Select Playlist
    playlist = select_playlist(playlists, playlist_name)

    if queue_limit is None:
        queue_limit = get_queue_limit()

    # Get Tracks of Selected Playlist
    print("Getting Tracks from Playlist...")
    playlist_tracks = get_tracks_from_playlist(sp, playlist)
    print("Done!")

    # for item in playlist_tracks:
    #     print(item['track']['name'])

    # Get Shuffled List
    shuffled_list = Shuffler.shuffle(playlist_tracks, recent_track_list, no_double_artist=no_double_artist_flag, no_double_album=no_double_album_flag, debug=True)

    # Queue
    print("Queueing songs...")

    try:
        for idx, song in enumerate(shuffled_list):
            sp.add_to_queue(song['track']['uri'])
            if queue_limit is not None and queue_limit > 0 and idx > queue_limit:
                break
            time.sleep(0.03)
    except spotipy.exceptions.SpotifyException:
        print("ERROR: Please make sure a device is actively playing.")
        sys.exit()

    print("Done!")

if __name__ == "__main__":
    main(sys.argv)