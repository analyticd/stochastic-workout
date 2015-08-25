#!/usr/bin/env python
""" workout.py - A mindless workout or a personal trainer.

I need something to tell me what excercises to do. This is that.
"""

from os import system
from subprocess import Popen, PIPE, STDOUT
import time
from random import sample, shuffle
import sys
import yaml

NUM_SETS = 3
NUM_MOVES = 3
NUM_GROUPS = 2

DEFAULT_CONFIG = 'workouts.yaml'

def get_config(config_file=None):
    if config_file is not None:
        pass
    elif len(sys.argv) == 1:
        config_file = DEFAULT_CONFIG
    else:
        config_file = sys.argv[1]
    print "Using", config_file
    return yaml.load(open(config_file))

def format_applescript(prog):
    """ Turn proper applescript to osascript executable code.
    """
    app_prog = "/usr/bin/osascript \\ \n-e ' " + prog.replace("\n", "' \\\n-e '") + "'\n"
    app_prog = app_prog.replace("\n", " ")
    app_prog = app_prog.replace("\\", " ")
    return app_prog


def run_script(prog):
      app_prog = format_applescript(prog)
      proc = Popen(app_prog, shell=True, stdout=PIPE, stderr=STDOUT)
      res = proc.communicate()[0]
      return res.strip()


def _example_applescript():
    prog = """tell application "Spotify"
    set theVar to album of the current track
    do shell script "echo " & quoted form of theVar
    end tell """
    return run_script(prog)


def say(saying):
    print saying
    saying = saying.replace("'", "\\'")
    saying = saying.replace('"', '\\"')
    system("say " + saying)

def get_warm_ups(warmup_file=None):
    if warmup_file is not None:
        config = get_config(warmup_file)
    else:
        config = get_config()
    return filter(is_warmup, config['exercises'])


def is_warmup(exercise):
    return 'warm-up' in exercise['format']


def get_exercises():
    config = get_config()
    return filter(is_exercise, config['exercises'])


def is_exercise(exercise):
    """ If an exercise is only a warm-up, don't include it"""
    return ['warm-up'] != exercise['format']

CONFIGS = {'disable_sleep': False, 'sleep_time': 'unmodified'}

def sleep(time_to_sleep):
    """ This is a wrapper around time.sleep to disable sleeping
    for debugging"""
    if CONFIGS.get('disable_sleep'):
        return
    if CONFIGS.get('sleep_time', 'unmodified') != 'unmodified':
        time_to_sleep = CONFIGS.get('sleep_time', 'unmodified')
    time.sleep(time_to_sleep)

# Define all the workouts.
warm_up_exercises = get_warm_ups("workouts.yaml")
exercises = get_exercises()

shuffle(warm_up_exercises)
shuffle(exercises)


def announce_for_stretching(moves):
    moves = [move['name'] for move in moves]
    stretch_string = "The moves coming up are %s, %s, and %s. "
    stretch_string = stretch_string % tuple(moves)
    stretch_string += "Take 45 seconds to stretch for them. Go!"
    say(stretch_string)
    sleep(45)


def open_in_google_images(moves):
    for move in moves:
        base_url = "http://www.google.com/search?q={query}&tbm=isch"
        search_term = move['name'] + ' ' + 'exercise'
        url = base_url.format(query=search_term)
        system('open "{url}"'.format(url=url))


def is_last_group(set_num, total_num_sets):
    return set_num == total_num_sets - 1


def double_time(i, list_of_sleep_times):
    say("Doubling time on " + move)
    list_of_sleep_times[i] *= 2
    sleep(list_of_sleep_times[i])


def pause():
    say("Pausing")
    raw_input("Press enter to return to workout and continue to next move.")


def execute_move(move, sleep_time):
    split = move.get('split')
    notes = move.get('notes')
    try:
        say(move['name'])
        if notes:
            say('Note: ' + notes)
        if split:
            sleep(sleep_time/2.)
            say('Switch')
            sleep(sleep_time/2.)
        else:
            sleep(sleep_time)
    except KeyboardInterrupt:
        try:
            pause()
        except KeyboardInterrupt:
            print
            print "Thanks for the workout."
            sys.exit(1)


#==============================================

if __name__ == "__main__":
    start = time.time()

    # Aerobic Warm up
    say("Warm up time. Here we go.")

    for a_set in range(3):
        for warm_up in warm_up_exercises:
            execute_move(warm_up, 10)

    # Generic stretching
    say("Take a minute for some general stretching.")
    sleep(60)

    # Exercises
    say("Great. Let's get started.")
    for a_group in range(NUM_GROUPS):
        moves = [exercises.pop() for i in range(NUM_MOVES)]
        open_in_google_images(moves)
        announce_for_stretching(moves)

        # TODO: take sleep_times into yaml.
        sleep_times = [45, 45, 45]
        for a_set in range(NUM_SETS):
            for i, move in enumerate(moves):
                execute_move(move, sleep_times[i])

        if not is_last_group(a_group, NUM_GROUPS):
            say("15 seconds for water break.")
            sleep(15)
            say("And we're back")

    say("Done. The pain is over.")

    end = time.time()

    say("Total workout time was %d minutes" % ((end-start)//60))
