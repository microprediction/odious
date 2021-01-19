# Matches and Elo ratings for optimizers against synthetic objective functions
from timemachines.optimization import optimize
from timemachines.optimizers.odious import optimizer_name
from timemachines.evaluation import EVALUATORS
from timemachines import SKATERS
from microprediction import MicroWriter
import time
import random
import json
import os
import numpy as np
from ratings.elo import elo_expected
from pprint import pprint
from odious.config import MATCHUPS_DIR, STOPPING_OPTIMIZERS, random_json_file_name
import sys

# Usage  matchup 'yourwritekkey9817239'

write_key = '235eda59cea66015679810130bd6e2de'
mw = MicroWriter(write_key=write_key)
print(mw.animal)


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
ensure_dir(MATCHUPS_DIR)


def random_optimizer_matchup(ys):
    """ Field test two optimizers and assign a win/loss/draw """

    white,black = np.random.choice(STOPPING_OPTIMIZERS, 2, replace=False)
    f = random.choice(SKATERS)
    print('Skater is '+f.__name__)
    evaluator = random.choice(EVALUATORS)

    n_trials = random.choice([10])
    n_dim = random.choice([3])
    n_burn = 50
    n = 100

    # White plays
    white_valid = False
    print('White is '+white.__name__)
    white_n = n_trials
    white_iter = 0
    while white_valid is False and white_iter<2:
        print('Starting White optimization')
        start_time = time.time()
        white_val, white_best, white_count = optimize(f=f, ys=ys, n_trials=white_n, n_dim=n_dim, n_burn=n_burn, optimizer=white, evaluator=evaluator, with_count=True)
        white_elapsed = time.time()-start_time
        white_valid = white_count < 2*n_trials+10
        white_n = int( n_trials / 2 )
        white_iter+=1

    report = {'white': optimizer_name(white),
              'black': optimizer_name(black),
              'epoch_time':time.time(),
              'f': f.__name__,
              'white_elo_stream':'optimizer_elo_' + optimizer_name(white) + '.json',
              'black_elo_stream':'optimizer_elo_' + optimizer_name(black) + '.json',
              'white_elo_stream_url': 'https://www.microprediction.org/stream_dashboard.html?stream=optimizer_elo_' + optimizer_name(white) + '.json',
              'black_elo_stream_url': 'https://www.microprediction.org/stream_dashboard.html?stream=optimizer_elo_' + optimizer_name(
                  black) + '.json',
              'evaluator': evaluator.__name__,
              'n_trials': n_trials, 'n_dim': n_dim, 'n_burn': n_burn,
              'white_elapsed':white_elapsed,
              'white_val':white_val,
              'white_best':tuple(list(white_best)),
              'white_count':white_count,
              'white_valid':white_valid,
              'white_iter':white_iter,
              }
    # Forfeit?
    if not white_valid:
        points = 0.0
        report.update({'points':points,'forfeit':1})
    else:
        report.update({'forfeit':0})
    pprint(report)
    if white_valid:
        # Black plays
        print('Black is ' + black.__name__)
        start_time = time.time()
        best_val_black, best_x_black, black_count = optimize(f=f, ys=ys, n_trials=white_count, n_dim=n_dim, n_burn=n_burn, optimizer=black, evaluator=evaluator, with_count=True)
        black_elapsed = time.time()-start_time
        valid_white = white_valid
        valid_black = black_count <= 1.2*white_count

        tol = 1e-3 * (abs(white_val) + abs(best_val_black))
        if valid_white and valid_black:
            if white_val < best_val_black - tol:
                points = 1.0
            elif best_val_black < white_val - tol:
                points = 0.0
            else:
                points = 0.5
        else:
            points = None

    report.update( {'points':points,
                    'valid_white':valid_white,
                    'valid_black':valid_black,
                    'white_elapsed':white_elapsed,
                    'black_elapsed':black_elapsed,
                    'black_count':black_count})

    return report


def current_elo_and_k(writer:MicroWriter, name:str, names:[str], initial_elo=2000):
    """ Get current elo and length of history, or initialize """
    if name in names:
        lagged = None
        while not lagged:
            lagged = mw.get_lagged_values(name=name)
            time.sleep(5)
    else:
        lagged = None

    if not lagged:
        writer.set(name=name, value=initial_elo)
        lagged = [initial_elo]

    k = 25 if len(lagged)<10 else 16

    return lagged[0], k


def elo_update(writer:MicroWriter, white_name:str,black_name:str,points:float):
    """ Updates microprediction.org streams holding the ratings """
    assert '.json' in white_name
    assert '.json' in black_name

    names = writer.get_stream_names()
    white_elo, white_k = current_elo_and_k(writer=writer, name=white_name, names=names)
    black_elo, black_k = current_elo_and_k(writer=writer, name=black_name, names=names)
    elo_diff = black_elo - white_elo
    e = elo_expected(d=elo_diff, f=400)
    w = report['points'] - e  # White's innovation
    k = min(white_k, black_k)
    white_new_elo = white_elo + k * w
    black_new_elo = black_elo - k * w
    mw.set(name=white_name, value=white_new_elo)
    mw.set(name=black_name, value=black_new_elo)


def comparison(write_key):

    # Pick a random stream
    mw = MicroWriter(write_key=write_key)
    names = mw.get_stream_names()
    n_lagged = 0
    n = 200  # Length of time series to use
    while n_lagged < n:
        name = random.choice(names)
        ys = list(reversed(mw.get_lagged_values(name=name, count=2000)))[:n]
        n_lagged = len(ys)

    # Run the comparison
    report = random_optimizer_matchup()

    # Update Elo ratings
    elo_update(writer=mw, white_name=report['white_name'],black_name=report['black_name'],points=report['points'])

    # Log result report
    match_report_log = MATCHUPS_DIR + os.path.sep + random_json_file_name()
    with open(match_report_log, 'wt') as fpt:
        json.dump(report, fpt)

    return report


if __name__=='__main__':
    write_key = sys.argv[1]
    report = comparison(write_key=write_key)
    pprint(report)





