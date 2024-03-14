"""
Holds the commands for the access page layout, which lets user go to the collections page, movies page, or users page, as well as signout
@author Alex Lee
"""
import queries
from pages.interface_funtcions import *
from psycopg2._psycopg import cursor
import pages.collections
import pages.movies
import pages.users
import pages.emails

def collections_page(curs: cursor, user_id: int) -> None:
  """
  Starts up the collections pages
  """
  pages.collections.collection_start(curs, user_id)
  return

def movies(curs: cursor, user_id: int) -> None:
  """
    starts up the movies page
  """
  pages.movies.movies_start(curs, user_id)
  return

def users(curs: cursor, user_id: int) -> None:
  """
    starts up the users page
  """
  pages.users.users_start(curs, user_id)
  return


def email_page(curs: cursor, user_id: int) -> None:
  """
    starts up the email page
  """
  pages.emails.email_start(curs, user_id)
  return


def login(curs: cursor) -> int:
  """
    logs the user into the application and returns the user_id
  """

  id = 0
  while id != -1:
    bcolors.print_color("Welcome to our database! Please choose an action: \n", bcolors.CYAN)
    #print("Welcome to our database! Please choose an action: \n")
    print("login: log into an existing account")
    print("create: create a new account")
    print("quit: quit the login page")
    action = input("\nEnter desired action: ")
    if action == "login":
      username = input("Username: ")
      password = input("Password: ")

      sql = """select user_id from users where username = %s and password = %s"""
      data = (username, password)
      curs.execute(sql, data)
      info = curs.fetchone()

      if info is None:
        print("Invalid username or password!")
        continue

      user_id = info[0]

      queries.update_user_login(curs, user_id)

      return info[0]

    elif action == "create":

      username = input("Username: ")
      password = input("Password: ")
      first_name = input("First name: ")
      last_name = input("Last name: ")

      user_id = queries.create_user(curs, username, password, first_name, last_name)

      if user_id == -1:
        print("Username is unavailable!")
        continue

      queries.update_user_login(curs, user_id)

      return user_id

    elif action == "quit":
      id = -1


  return -1


def access_granted(curs: cursor) -> None:
  """
  starts up the access page which lets the user go to collections, movies, or the users page
  """

  user_id = login(curs)

  if user_id == -1:
    return

  bcolors.print_color("\nAccess Granted", bcolors.GREEN)
  while get_input(["collections", "movies", "emails", "users"], [collections_page, movies, email_page, users], (curs, user_id), (curs, user_id), (curs, user_id), (curs, user_id)):
    continue
  return