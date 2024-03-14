"""
Holds the content of the users and user related functions
@author Alex Lee
"""
import queries
from pages.interface_funtcions import *
from psycopg2._psycopg import cursor
import queries as que

def following(curs: cursor, user_id: int) -> None:
  """
  displays everyone your following
  Args:
      curs (object): _description_
  """
  print("showing your followers")

  query = "SELECT username FROM users JOIN followers AS fol ON \
    users.user_id = fol.followed_id AND fol.follower_id = '%s'" % (user_id)
  
  results = DataStream(curs, query)

  if results.peek() is None:
    bcolors.print_color("You're not following anyone", bcolors.CYAN)


  while results.peek() is not None:
    bcolors.print_color(results.next()[0], bcolors.CYAN)
  return 

def followers(curs: cursor, user_id: int) -> None:
  """
  displays everyone following you

  Args:
      curs (object): _description_
  """

  query = "SELECT username FROM users JOIN followers AS fol ON \
    users.user_id = fol.follower_id AND fol.followed_id = '%s'" % (user_id)
  
  results = DataStream(curs, query)

  if results.peek() is None:
    bcolors.print_color("No followers", bcolors.CYAN)


  while results.peek() is not None:
    bcolors.print_color(results.next()[0], bcolors.CYAN)

  return

def unfollow_user(curs: cursor, user_id: int, followed_id: int) -> None:
  # check to see if the person is already following
  query = "SELECT * FROM followers WHERE follower_id = '%s' AND followed_id = '%s'" % (user_id, followed_id)

  # check to make sure theyre not following eachother
  if (DataStream(curs, query).peek() is None): 
    bcolors.print_color("You are not following this user", bcolors.RED)
    return

  # if they are unfollow them
  que.unfollow_user(curs, user_id, followed_id)
  bcolors.print_color("User unfollowed", bcolors.GREEN)

  return

def follow_user(curs: cursor, user_id: int, other_id: int) -> None:
  # check to see if the person is already following
  query = "SELECT * FROM followers WHERE follower_id = '%s' AND followed_id = '%s'" % (user_id, other_id)

  # actually follow the user
  if (DataStream(curs, query).peek() is not None): 
    bcolors.print_color("You are already following this user", bcolors.RED)
    return

  # if they arent, add a followed
  que.follow_user(curs, user_id, other_id)
  bcolors.print_color("You are now following this user", bcolors.GREEN)

  return

  
def search_user(curs: cursor, user_id: int) -> None:
  while True:
    # should also check emails to get the users
    bcolors.print_color("Cancel anytime with '0'", bcolors.YELLOW)
    user_query = input("Username/email: ")

    if user_query == "0":
      return

    # check for the user name 
    users = DataStream(curs, "SELECT user_id FROM users WHERE username = '%s'", (user_query))

    # check for the email
    emails = DataStream(curs, "SELECT user_id FROM emails WHERE email_address = '%s'" % user_query)


    if users.peek() is None and emails.peek() is None:
      bcolors.print_color("User not found", bcolors.RED)
      continue
    
    other_id = users.peek()[0] if users.peek() is not None else emails.peek()[0]

    if str(user_id) == str(other_id):
      bcolors.print_color("You can't search for yourself", bcolors.RED)
      continue
    
    get_input(["follow", "unfollow"], [follow_user, unfollow_user], (curs, user_id, other_id), (curs, user_id, other_id))
    return


def follower_count(curs: cursor, user_id: int) -> None:
  count = queries.get_follower_count(curs, user_id)

  print("You are being followed by", count, "user(s)!")

def following_count(curs: cursor, user_id: int) -> None:
  count = queries.get_following_count(curs, user_id)

  print("You are following", count, "user(s)!")

def users_start(curs: cursor, user_id: int) -> None:
  bcolors.print_color("\nWelcome to users", bcolors.GREEN)

  while get_input(["search", "followers", "followercount", "following", "followingcount"],
                  [search_user, followers, follower_count, following, following_count],
                  (curs, user_id), (curs, user_id), (curs, user_id), (curs, user_id), (curs, user_id)): continue

  return