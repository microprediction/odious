from timemachines import OPTIMIZERS
import random
import os

# Select optimizers that stop after a pre-specified number of function evaluations
stopping = ['ax', 'pysot', 'optuna', 'hyperopt']
STOPPING_OPTIMIZERS = [o for o in OPTIMIZERS if any(g in o.__name__ for g in stopping)]


MATCHUPS_DIR = './matchups'


def random_json_file_name():
    return ''.join([random.choice('abcdef1234567890') for _ in range(12)]) + '.json'

