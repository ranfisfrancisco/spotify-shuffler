# spotify-shuffler

### Description
Spotify Shuffler is a Python based program to shuffle and queue songs while keeping track of what songs were recently played to improve the shuffling.

It can be used to queue random songs from any of your playlists.

## Getting Started

### Dependencies

The Spotipy library is needed to interface with the Spotify API.

> pip install spotipy


The dotenv-python library is needed as well.

> pip install python-dotenv


### Setup

You will need to get a client ID and client secret from Spotify to be able to interact with the API. You can follow steps 1-7 here:
https://support.appreciationengine.com/article/oaNki9g06n-creating-a-spotify-application

Once you have those, create a .env file with the lines:
```
SPOTIPY_CLIENT_ID=YOUR_CLIENT_ID
SPOTIPY_CLIENT_SECRET=YOUR_CLIENT_SECRET
SPOTIPY_REDIRECT_URI='https://google.com'
```

The redirect URL can be any valid URL address, including localhost.

## Executing program

Run
> python main.py

You will be prompted to enter your username. The first time it is run, a webpage will open in your browser. You will be prompted to allow the Spotify app you created to have the necessary permissions. Upon saying yes, you will be redirected to another URL. Copy that URL into the command prompt and hit enter.

Follow the rest of the prompts to select your desired playlist and how many songs to queue.

### Command Line Arguments

You can skip the prompts that appear by passing in the necessary information as command line arguments.

**-u** : Argument after this flag is taken as the username. Program will ask for username if not provided. 
Example: python main.py -u username_here

**-p** : Argument after this flag is taken as the playlist to be queued. Program will ask for playlist name if not provided. **Case sensitive.**
Example: python main.py -p "Rock"
If the playlist name is multiple words, it MUST be surrounded by double quotes ("").
Example: python main.py -p "The best playlist of all time"
Multiple playlists can be provided.
Example: python main.py -p "Rock" -p "Pop"


**-l** : Argument after this flag is taken as the max number of songs to be queued from the selected playlist. Program will ask for limit if not provided. "inf" signifies no limit.
Example: python main.py -l 20
Example: python main.py -l inf

**-ndar**: Signfies that the shuffler should avoid having the same artist play twice in a row (no double artist)

**-ndal**: Signfies that the shuffler should avoid having the same artist play twice in a row (no double album)

**-ns**: Disables shuffling the selected playlist(s)

**-o, -offset:** Offsets start of queue by provided amount.
Example: python main.py -p "Rock" -ns -o 25

**-debug**: prints shuffled queue song names to queue.log

## Usage

You can use the script to queue random tracks from different playlists back to back, with as many as you want from each playlist.
For example, you may run this back to back and queue random songs from each of these playlists:

```
python main.py -u alan_smith -l 5 -p "Rock"
python main.py -u alan_smith -l 10 -p "Sick beats to chill/study to"
python main.py -u alan_smith -l 3 -p "my secret Imagine Dragons playlist"
```

The no-shuffle and offset flags can be used to queue songs from a playlist unshuffled starting from a specific point.

```
# Queue 10 songs from playlist "Rock" starting track 15.
python main.py -u alan_smith -l 10 -p "Rock" -o 15 -ns
```

## Troubleshooting
Make sure a device is actively connected to Spotify/playing or the queue attempt will fail. Briefly playing and then pausing will make sure the device is connected.
If two playlists have the same name, the first one will be selected. To circumvent this, do not provide a playlist name through the command line and use the prompt that shows up to select a playlist by index. Or just don't have two playlists with the same name!
