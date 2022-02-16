"""Main module."""
import sys
import spotipy
from spotipy import util
from dotenv import load_dotenv
from shuffler import Shuffler

def help_string():
    """Returns help doc."""
    return '''Options: \n\
    -u, -user : Argument after this flag is taken as the username. Program will ask for username if not provided. Example: python main.py -u usernameHere
    -p, -playlist : Argument after this flag is taken as the playlist to be queued. Program will ask for playlist name if not provided. Example: python main.py -playlist "rock"
    If the playlist name is multiple words, it MUST be surrounded by double quotes ("").
    -l, -limit : Argument after this flag is taken as the max number of songs to be queued. Program will ask for limit if not provided. "inf" signifies no limit.
    Example: python main.py -l 20
    Example: python main.py -l inf
    -ndar: Signfies that the shuffler should avoid having the same artist play twice in a row (no double artist)
    -ndal: Signfies that the shuffler should avoid having the same artist play twice in a row (no double album)
    -ns: Disables shuffling the selected playlist(s)
    -o, -offset: Offsets start of queue.
    -debug: prints shuffled queue to queue.log

Troubleshooting:
    Make sure a device is actively connected to Spotify/playing or the queue attempt will fail.
    If two playlists have the same name, the first one will be selected. To circumvent this,
    do not provide a playlist name through the command line and use the prompt that shows up to
    select a playlist by index. Or just don't have two playlists with the same name!'''

def get_auth(username, scope) -> spotipy.Spotify:
    """Get authentication and crate Spotify object for API interaction

    Return spotipy.Spotify object if successful, None otherwise.

    Arguments:

    username -- string containing the Spotify username
    scope -- string containing desired permissions (see Spotify API documentation)"""

    token = util.prompt_for_user_token(username, scope)

    if not token:
        return None

    spotify_conn = spotipy.Spotify(auth=token)
    return spotify_conn

def find_name_in_playlists(playlists, name):
    """Return playlist matching given name.
    Returns None if not found.

    Arguments:

    playlists -- list of playlists obtained through Spotify API
    name -- string that is the name of the playlist to be played."""

    for item in playlists:
        if item['name'] == name:
            return item
    return None

def prompt_for_playlist(playlists):
    """Get dictionary object for a playlist chosen by the user from a list of playlists.

    Returns dictionary with the playlist data.

    Arguments:

    playlists -- list of playlists obtained through Spotify API

    selected_playlist_name -- if the user has already entered the desired playlist name,
    this will be used to find the playlist first (default None)
    """

    entry = None
    select_flag = 0

    # Note: User is choosing with 1 based indexes.
    for idx, item in enumerate(playlists):
        print(f'Index {idx+1} | Name {item["name"]} | # of Tracks {item["tracks"]["total"]} ')

    while select_flag == 0:
        entry = input('Select Playlist by Index or Name?\n1. Index\n2. Name\n')
        if entry.isnumeric() and int(entry) in [1, 2]:
            select_flag = int(entry)
        else:
            print("Invalid Input")

    entry = None
    if select_flag == 1:
        while True:
            entry = input('Enter index: ')
            if not entry.isnumeric() or int(entry) > len(playlists) or int(entry) < 1:
                print("Invalid Index")
                continue

            idx = int(entry)
            return playlists[idx-1] # One-indexed
    elif select_flag == 2:
        while True:
            entry = input('Enter name: ')

            playlist = find_name_in_playlists(playlists, entry)
            if playlist:
                return playlist

            print("Did not find name!")

def get_playlists(spotify_conn):
    """Gets a user's playlists.

    Assumes spotipy.spotify object passed in is already authenticated with a user.

    Arguments:

    spotify_conn - spotipy.Spotify object authenticated with user"""
    playlists = []
    offset = 0
    offset_difference = 50

    while True:
        results = spotify_conn.current_user_playlists(offset=offset)

        if not results['items']:
            break

        playlists.extend(results['items'])

        if len(results['items']) < offset_difference:
            break

        offset += offset_difference

    return playlists

def get_tracks_from_playlist(spotify_conn, playlist):
    """Get tracks from a given playlist

    Assumes spotipy.Spotify object passed in is already authenticated with a user

    Returns list of track dictionary objects from Spotify API.
    Returns empty list if playlist is empty or the playlist was not found.

    Arguments:

    spotify_conn -- spotipy.Spotify object authenticated with a user

    playlist -- dictionary object of data from Spotify API for a particular playlist"""

    playlist_tracks = []
    offset = 0
    offset_difference = 100

    while True:
        results = spotify_conn.user_playlist_tracks(playlist_id=playlist['id'], offset=offset)

        if not results['items']:
            break

        playlist_tracks.extend(results['items'])

        if len(results['items']) < offset_difference:
            break

        offset += offset_difference

    return playlist_tracks

def prompt_for_queue_limit():
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

def group_quotes(argv):
    """Returm list of argv arguments where strings in quotes are grouped as a single item.
    For example: ['-p', '"my', 'awesome', 'playlist"']
    becomes ['-p', 'my awesome playlist']

    Arguments:

    argv - same as sys.argv"""

    ans = []
    in_quotes = False

    for var in argv:
        if not in_quotes:
            if var[0] == '"':
                in_quotes = True
            ans.append(var)
        else:
            ans[-1] = ans[-1] + " " + var
            if var[-1] == '"':
                in_quotes = False
        ans[-1] = ans[-1].strip('"')

    return ans

def parse_args(argv: list) -> tuple:
    '''Parse command line arguments and return variables and flags as necessary.

    Returns tuple of
    username, playlist_name, queue_limit, no_double_artist_flag, no_double_album_flag

    Arguments:

    argv -- command line arguments as list. Same as sys.argv'''

    options = {
        "username" : None,
        "playlist_name" : None,
        "queue_limit" : None,
        "no_double_artist_flag" : False,
        "no_double_album_flag" : False,
        "no_shuffle" : False,
        "offset": 0,
        "debug" : False
    }

    argv = group_quotes(argv)

    for idx, arg in enumerate(argv):
        try:
            if arg in ['-u', '-user']:
                options['username'] = argv[idx+1]
            elif arg in ['-p', '-playlist']:
                options['playlist_name'] = argv[idx+1]
            elif arg in ['-l', 'limit']:
                if argv[idx+1] == "inf":
                    options['queue_limit'] = float("inf")
                    continue

                if not argv[idx+1].isnumeric():
                    sys.exit("Queue limit must be integer or 'inf' for infinite")

                options['queue_limit'] = int(argv[idx+1])

                if options['queue_limit'] < 1:
                    sys.exit("Queue limit must be greater than 0, or inf to mean infinite.")

            elif arg == '-ndar':
                options["no_double_artist_flag"] = True
            elif arg == '-ndal':
                options["no_double_album_flag"] = True
            elif arg == '-ns':
                options["no_shuffle"] = True
            elif arg in ['-o', '-offset']:
                if not argv[idx+1].isnumeric():
                    sys.exit("Offset must be integer.")

                options["offset"] = int(argv[idx+1])

                if options['offset'] < 0:
                    sys.exit("Offset must be greater or equal to 0.")

            elif arg == "-debug":
                options["debug"] = True
            elif arg in ["-help", "-h"]:
                print(help_string())
                sys.exit()

        except IndexError:
            sys.exit("Each -u, -p -l, and -o must have an argument after it.")

    return options

def main(argv):
    '''Shuffle songs in playlist and add to user's play queue.

    Arguments:

    argv -- same as sys.argv
    Supports several flags through argv:
    -u, -user -- argument following this is the user's username.
    Will be prompted for this if not provided.
    -p, -playlist -- argument following this is the name of the playlist to shuffle.
    Will be prompted for this if not provided.
    -l, -list -- argument following this is the maximum number of songs that should be queued.
    "inf" means no limit.
    Will be prompted for this if not provided.
    -ndar -- flag that makes shuffler avoid playing the same artist twice in a row.
    -ndal -- flag that makes shuffler avoid playing the same album twice in a row.
    -ns -- flag that, if true, will disable shuffling the selected playlist.
    -o,-offset -- Offsets start of queue'''

    load_dotenv()

    scope = 'user-library-read user-read-recently-played playlist-read-private streaming'

    options = parse_args(argv)

    if options['username'] is None:
        options['username'] = input("Enter Spotify Username: ")

    spotify_conn = get_auth(options['username'], scope)
    if not spotify_conn:
        sys.exit(f"Can't get token for  {options['username']}")

    # Get Recently Played
    results = spotify_conn.current_user_recently_played(limit=50)
    recent_track_list = results['items']

    # Get Playlists
    playlists = get_playlists(spotify_conn)

    # Select Playlist
    if options["playlist_name"]:
        playlist = find_name_in_playlists(playlists, options["playlist_name"])
        if not playlist:
            sys.exit("Failed to find playlist with that name. Must match exactly!")
    else:
        playlist = prompt_for_playlist(playlists)

    if options["queue_limit"] is None:
        options["queue_limit"] = prompt_for_queue_limit()

    # Get Tracks of Selected Playlist
    print("Getting Tracks from Playlist...")
    playlist_tracks = get_tracks_from_playlist(spotify_conn, playlist)
    print("Done!")

    # Get Shuffled Queue
    if options["no_shuffle"]:
        shuffled_queue = playlist_tracks
    else:
        shuffled_queue = Shuffler.shuffle(playlist_tracks, recent_track_list,
        no_double_artist=options["no_double_artist_flag"],
        no_double_album=options["no_double_album_flag"], debug=options["debug"])

    # Offset
    shuffled_queue = shuffled_queue[options["offset"]:]

    # Queue
    print("Queueing songs...")

    try:
        for idx, song in enumerate(shuffled_queue):
            spotify_conn.add_to_queue(song['track']['uri'])
            if options["queue_limit"] is not None and idx + 1 >= options["queue_limit"]:
                break
    except spotipy.exceptions.SpotifyException:
        sys.exit("ERROR: Please make sure a device is actively playing.")

    print("Done! Exiting...")

if __name__ == "__main__":
    main(sys.argv)
