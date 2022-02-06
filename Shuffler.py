from typing import List
from random import randint
import math
import logging

class Shuffler:

    def shuffle(song_list: List, recently_played: List, debug=False) -> List:
        queue = []
        queue.extend([{'song' : song, 'score': 0, 'recently_played': None} for song in song_list])

        for i in range (0, len(recently_played)):
            for j in range(0, len(queue)):
                if recently_played[i]['track']['uri'] == queue[j]['song']['track']['uri']:
                    queue[j]['recently_played'] = i + 1
                    break

        for idx, song_dict in enumerate(queue):
            queue[idx]['score'] = Shuffler.get_score(song_dict)

        queue = sorted(queue, key= lambda x: -x['score'])

        if debug:
            with open('queue.log', 'w',encoding='utf-8') as f:
                f.write('Recently Played | Song | Artist\n')
                for thing in queue:
                    rp =  thing['recently_played']
                    if rp == None:
                        rp = "NA"
                    f.write(f'{rp} | {thing["song"]["track"]["name"]} | {thing["song"]["track"]["artists"][0]["name"]} \n')

        return [x['song'] for x in queue]

    def get_recency_bias(song_dict):
        if (song_dict['recently_played'] is None):
            return 0

        recent_idx = song_dict['recently_played']
        if recent_idx == 0:
            logging.warning('Recent Index should never be 0!')
            return 0

        bias = 250 * math.tanh(5/recent_idx) - randint(0, 100)

        if bias < 0:
            bias = 0

        return -bias

    def get_random(song_dict=None):
        return randint(0, 1000)

    def get_score(song_dict):
        score = 0

        score += Shuffler.get_recency_bias(song_dict)
        score += Shuffler.get_random(song_dict)

        return score