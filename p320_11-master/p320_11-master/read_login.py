"""
Contains methods for reading in login information from a file to log in to the database.

@author Philip Napoli
"""

def read_login() -> list[str]:
    with open("logins.txt", encoding="utf-8") as file:
        for line in file:
            lines_split = line.split(' ')
            name = lines_split[0]
            return lines_split

    return []
