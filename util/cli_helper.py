"""Util functions for the script"""
import sys
import csv


def get_all_user_from_file():
    """Returns all the usernames given as parameter"""
    usernames = []

    # display provide username
    if len(sys.argv) < 2:
        sys.exit('- Please provide at least one username!\n')

    for filename in sys.argv[1:]:
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            for user in reader:
                user = str(user)
                user = user[2:-2]
                usernames.append(user)

    return usernames
