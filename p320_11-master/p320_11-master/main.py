"""
Starting point for database program.
Connects to starbug and if successful, begins accepting command line arguments.

@author Philip Napoli
"""
import sys

import psycopg2
from sshtunnel import SSHTunnelForwarder

import pages.access_page as access_page
import queries
import read_login


dbName = "p320_11"
hostName = "127.0.0.1"


"""
Establishes an SSH connection.
If connection is successfully established, begins the command line program.
If not, prints out an error message.
"""
def init() -> None:
    login_info = read_login.read_login()

    if login_info is not None:
        username = login_info[0]
        password = login_info[1]
    else:
        print("No login information provided!")
        return

    try:
        with SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
                                ssh_username=username,
                                ssh_password=password,
                                remote_bind_address=(hostName, 5432)) as server:
            server.start()
            print("SSH tunnel established")
            params = {
                'database': dbName,
                'user': username,
                'password': password,
                'host': hostName,
                'port': server.local_bind_port
            }

            conn = psycopg2.connect(**params)
            curs = conn.cursor()
            print("Database connection established")

            access_page.access_granted(curs)

            curs.close()
            conn.commit()
            conn.close()
    except:
        print("Connection failed")

if __name__ == '__main__':
    print("Initializing program...")
    init()
