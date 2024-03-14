"""
Holds the commands for the movie page in which the user can interact with
movies in the database. 

@author Alex Lee
"""

from pages.interface_funtcions import *
import queries
from psycopg2._psycopg import cursor

def display_movie(curs: cursor, data: tuple[object], movie_num: int) -> None:
  """
  Displays a movie to the user via the console

  Pre-req:
    Data is in the form {movie_id, title, length, mpaa_rating, first_name, last_name, rating}

  Args:
      curs (cursor): cursor connected to the database
      data (tuple[object]): the movie to display
      movie_num (int): the index of the movie being displayed (used to pick color of printing)
  """
  color = bcolors.CYAN if movie_num % 2 == 0 else bcolors.PINK
  bcolors.print_color(str(movie_num) + ")", color)
  bcolors.print_color("Name: " + data[1], color)
  bcolors.print_color("Cast members:", color)
  cast = DataStream(curs, "SELECT first_name, last_name FROM person \
  WHERE person_id IN ( \
    SELECT person_id FROM cast_member_movie \
                     WHERE movie_id = '%s');" % data[0])
  while cast.peek() is not None:
    member = cast.next()
    bcolors.print_color(member[0] + " " + member[1], color)
  bcolors.print_color("Director: " + str(data[4]) + " " + str(data[5]) + "\nLength: " + str(data[2]), color)
  bcolors.print_color("Global Rating: " + str(data[3]) + "\nYour rating: " + str(data[6]), color)
  return

def generate_search_where(attribute: str, parameter: str) -> str:
  """
  Generates the Where statement for generating the movie search

  Args:
      attribute (str): the type of search
      parameter (str): the input from the user

  Returns:
      str: the where statement
  """
  if (attribute.lower() == 'name'):
    return "WHERE LOWER(title) = '%s'" % parameter

  if (attribute.lower() == "cast_member"):
    parameter = parameter.split(" ")
    return "WHERE M.movie_id IN  (\
    SELECT movie_id FROM cast_member_movie WHERE person_id IN\
    ( SELECT person_id FROM person\
        WHERE LOWER(first_name) = '%s' AND LOWER(last_name) = '%s'))" % (parameter[0], parameter[1])
  
  if (attribute.lower() == "studio"):
    return "WHERE M.movie_id IN ( \
    SELECT SM.movie_id FROM studio_movie AS SM \
    WHERE SM.studio_id IN ( \
        SELECT S.studio_id FROM studio as S \
        WHERE LOWER(S.name) = '%s' ) )" % parameter
  
  if (attribute.lower() == "genre"):
    return "WHERE M.movie_id IN ( \
    SELECT GM.movie_id FROM genre_movie AS GM \
    WHERE GM.genre_id IN ( \
        SELECT G.genre_id FROM genre as G \
        WHERE LOWER(G.genre_category) = '%s'))" % parameter
  
  if (attribute.lower() == "date"):
    return "WHERE M.movie_id IN ( \
      SELECT RM.movie_id FROM release_platform_movie AS RM \
      WHERE RM.release_date = '%s' \
    )" % parameter

  return None

def generate_search_sort() -> str:
  """
  Generates the sort statement for the movie search using user input

  Returns:
      str: the sort statement
  """
  result = None
  while True:
    sort_method = input(bcolors.generate_string("Sort types: (ASC | DESC) (Name | Studio | Genre | Date):\n", bcolors.YELLOW))
    sort_method = sort_method.split(" ")

    if len(sort_method) != 2:
      bcolors.print_color("Invalid Search", bcolors.RED)
      continue

    order = sort_method[0]
    sort_class = sort_method[1]

    if order != "ASC" and order != "DESC":
      bcolors.print_color("Invalid search", bcolors.RED)
      continue

    # G.genre_category, S.name, RD.release_date

    if sort_class.lower() == 'name':
      return "ORDER BY M.title %s" % order
    
    if sort_class.lower() == 'studio':
      return "ORDER BY S.name %s" % order

    if sort_class.lower() == 'genre':
      return "ORDER BY G.genre_category %s" % order
    
    if sort_class.lower() == 'date':
      return "ORDER BY RD.release_date %s" % order

    break
  return result

def rate_movie(curs: cursor, movie: tuple[object], user_id: int):
  """
  Lets the user rate a movie

  Pre-req:
    Data is in the form {movie_id, title, length, mpaa_rating, first_name, last_name, rating}
  
  Args:
      curs (cursor): cursor connected with the database
      movie (tuple[object]): the movie the user selected
      user_id (int): the id of the user
  """
  while True:
    print("-1 to go back")
    rating = input("Rating: ")

    if rating == "-1":
      break

    if not rating.isnumeric():
      bcolors.print_color("Must be a numeric number", bcolors.RED)
      continue
    
    rating = int(rating)

    if rating < 0 or rating > 5:
      bcolors.print_color("Must be between 0 and 5", bcolors.RED)
      continue

    # check to see if the user already has a rating
    if DataStream(curs, "SELECT * FROM rated WHERE movie_id = '%s' AND user_id = '%s'" % (movie[0], user_id)).get_size() >= 1:
      # the user already has a rating, update it.
      queries.update_movie_rating(curs, user_id, movie[0], rating)
      break

    # the user has not rated it before
    bcolors.print_color("You rated the movie " + movie[1], bcolors.GREEN)
    queries.rate_movie(curs, user_id, movie[0], rating)
    break

  return

def remove_movie_from_collection(curs: cursor, movie: tuple[object], user_id: int) -> None:
  while True:
    bcolors.print_color("0 is go back", bcolors.YELLOW)
    collection_name = input(bcolors.generate_string("Collection Name: ", bcolors.YELLOW))

    if collection_name == "0":
      return

    query_results = DataStream(curs, "SELECT collection_id FROM collection WHERE name = '%s' AND user_id = '%s';"
                                % (collection_name, user_id))
    
    if query_results.peek() == None:
      bcolors.print_color("Collection not found", bcolors.RED)
      continue

    collection_id = query_results.next()[0]
    bcolors.print_color("Movie removed", bcolors.GREEN)
    if DataStream(curs, "SELECT * FROM collection_movie WHERE movie_id = '%s' AND collection_id = '%s'" % (movie[0], collection_id)).peek() is not None:
      queries.remove_movie_from_collection(curs, movie[0], collection_id)
    break
  return

def add_movie_to_collection(curs: cursor, movie: tuple[object], user_id: int) -> None:
  while True:
    bcolors.print_color("0 is go back", bcolors.YELLOW)
    collection_name = input(bcolors.generate_string("Collection Name: ", bcolors.YELLOW))

    if collection_name == "0":
      return

    query_results = DataStream(curs, "SELECT collection_id FROM collection WHERE name = '%s' AND user_id = '%s';"
                                % (collection_name, user_id))
    if query_results.peek() == None:
      bcolors.print_color("Collection not found", bcolors.RED)
      continue

    collection_id = query_results.next()[0]
    bcolors.print_color("Movie added", bcolors.GREEN)
    if DataStream(curs, "SELECT * FROM collection_movie WHERE movie_id = '%s' AND collection_id = '%s'" % (movie[0], collection_id)).peek() is None:
      queries.add_movie_to_collection(curs, movie[0], collection_id)
    break
  return

def watch_movie(curs: cursor, movie: tuple[object], user_id: int) -> None:
  bcolors.print_color("Watched movie", bcolors.GREEN)
  queries.watch_movie(curs, user_id, movie[0])
  return

def pick_movie(curs: cursor, results: list[tuple[object]], user_id: int) -> None:
  """
  lets the user pick a movie based on an index

  Pre-req:
    Data is in the form {movie_id, title, length, mpaa_rating, first_name, last_name, rating}

  Args:
      curs (cursor): cursor connected to the database
      results (list[tuple[object]]): an array of movies for the user to pick
      user_id (int): the id of the user
  """
  while True:
    bcolors.print_color("0 to go back", bcolors.YELLOW)
    movie_pick = input(bcolors.generate_string("Please select a movie by number: ", bcolors.YELLOW))

    if not movie_pick.isnumeric():
      bcolors.print_color("MUST be a number", bcolors.RED)
      continue

    movie_pick_index = int(movie_pick) - 1

    if (movie_pick_index == -1):
      return

    if movie_pick_index < 0 or movie_pick_index >= len(results):
      bcolors.print_color("index out of range", bcolors.RED)
      continue
    
    choice = results[movie_pick_index]
    bcolors.print_color(choice[1] + " picked", bcolors.GREEN)

    while get_input(["rate", "watch", "add_collection", "remove_collection"], 
                    [rate_movie, watch_movie, add_movie_to_collection, remove_movie_from_collection], 
                    (curs, choice, user_id), (curs, choice, user_id), (curs, choice, user_id), (curs, choice, user_id)): continue

    break

  return

def movie_search(curs: cursor, user_id: int) -> None:
  """
  Allows the user to search for a particular movie, select it, and perform an action for it
  such as rate it. 

  Args:
      curs (cursor): the cursor connected to the database
      user_id (int): the id of the user
  """
  print("Searching: ")
  while True:
    search = input(bcolors.generate_string("Search Template\n(type: Name | Date | Cast_Member | Studio | Genre) (sort: y | n) [query]:\n", bcolors.YELLOW))

    search_results = search.split(" ")
    
    # test if the search result was proper

    # for now assume this is all true and sort is no
    attribute = search_results[0]
    sort_type = search_results[1]
    parameter = " ".join(search_results[2:]).lower()

    # default name
    where_query = generate_search_where(attribute, parameter)

    # assume sort query is default for now
    sort_query = "ORDER BY M.title ASC, release_date ASC"
    if sort_type.lower() == 'y':
      sort_query = generate_search_sort()

    attribute_query = "SELECT M.movie_id, title, length, mpaa_rating, first_name, last_name, R.rating, \
    G.genre_category, S.name, RD.release_date \
    FROM movie AS M JOIN person AS P \
    ON M.person_id = P.person_id \
    left JOIN rated AS R \
    ON R.user_id = '%s' AND M.movie_id = R.movie_id \
    \
    JOIN (SELECT DISTINCT movie_id, genre_category FROM genre_movie \
    JOIN genre ON genre_movie.genre_id = genre.genre_id \
    ORDER BY genre_category) AS G ON G.movie_id = M.movie_id \
    \
    LEFT JOIN (SELECT movie_id, name FROM studio_movie \
    JOIN studio on studio_movie.studio_id = studio.studio_id) AS S\
    ON S.movie_id = M.movie_id\
    \
    LEFT JOIN (SELECT DISTINCT movie_id, release_date FROM release_platform\
    JOIN release_platform_movie ON release_platform.platform_id = release_platform_movie.platform_id\
    ORDER BY release_date) AS RD ON RD.movie_id = M.movie_id" % user_id

    attribute_query += " " + where_query + " " + sort_query + ";"

    results = DataStream(curs, attribute_query)

    if results.get_size() == 0:
      bcolors.print_color("No movies found", bcolors.RED)
      continue

    all_results = get_unqiue_movies(results.get_all())
    index = 1
    for index, movie in enumerate(all_results):
      display_movie(curs, movie, index + 1)
    
    pick_movie(curs, all_results, user_id)

    break
  return

def get_top_movies(curs: cursor, user_id: int) -> None:
  def generate_query(curs: cursor, user_id: int) -> str:
    while True:
      query_type = input(bcolors.generate_string("Selected based on: (watches | ratings | combo)\n", bcolors.YELLOW))

      if query_type == "watches":
        return """SELECT count(user_id), M.movie_id, title, mpaa_rating FROM watched AS W
                  LEFT JOIN movie AS M ON M.movie_id = W.movie_id
                  WHERE user_id = '%s'
                  GROUP BY M.movie_id
                  order by count(user_id) DESC LIMIT 10;""" % user_id
      
      if query_type == "ratings":
        return """SELECT rating, M.movie_id, title, mpaa_rating FROM rated AS R
                  LEFT JOIN movie AS M ON M.movie_id =  R.movie_id
                  where user_id = '%s'
                  GROUP BY M.movie_id, R.rating
                  order by rating DESC LIMIT 10;""" % user_id
      
      if query_type == "combo":
        return """select R.rating, M.movie_id, M.title, M.mpaa_rating, count(R.movie_id) as times from rated as R
                  left join watched as W on W.movie_id = R.movie_id
                  left join movie as M on M.movie_id = R.movie_id
                  where R.user_id = '%s' and W.user_id = '%s'
                  group by M.movie_id, M.title, M.mpaa_rating, R.rating
                  order by R.rating desc, times DESC LIMIT 10;""" % (user_id, user_id)
        return
      
      bcolors.print_color("Invalid input", bcolors.RED)

    return

  # gets the top 10 based on user rating and watches

  print("Your top 10 movies are")
  query = generate_query(curs, user_id)
  
  movies = DataStream(curs, query)

  for index, movie in enumerate(movies.get_all()):
    index += 1
    color = bcolors.CYAN if index % 2 == 0 else bcolors.PINK
    bcolors.print_color(str(index) + ".\nName: " + movie[2] + "\nRating: " + movie[3], color)

  return

def get_top_general_movies(curs: cursor, user_id: int) -> None:
  # get the top 20 movies based on watches from the general public
  results = queries.get_recent_popular(curs)

  print("Top 20 most recent popular")
  
  for index, movie in enumerate(results):
    index += 1
    color = bcolors.CYAN if index % 2 == 0 else bcolors.PINK
    bcolors.print_color(str(index) + ".\nName: " + get_movie_name(curs, int(movie[0])) + "\nCount: " + str(movie[1]), color)

  return

def get_follower_top(curs: cursor, user_id: int) -> None:
  # get the top 20 movies based on watches from your followers

  results = queries.get_recent_popular_among_followers(curs, user_id)

  print("Top 20 most recent popular amount followers")
  
  for index, movie in enumerate(results):
    index += 1
    color = bcolors.CYAN if index % 2 == 0 else bcolors.PINK
    bcolors.print_color(str(index) + ".\nName: " + get_movie_name(curs, int(movie[0])) + "\nCount: " + str(movie[1]), color)

  return

def get_for_me(curs: cursor, user_id: int) -> None:
  # get the movies that are recommended to the user indiviually
  results = queries.get_recommended_movies(curs, user_id)

  print("Your recommended movies")

  for index, movie in enumerate(results):
    index += 1
    color = bcolors.CYAN if index % 2 == 0 else bcolors.PINK
    bcolors.print_color(str(index) + ".\nName: " + get_movie_name(curs, int(movie[0])), color)

  return

def get_top_5(curs: cursor, user_id: int):
  results = queries.get_top_this_month(curs)

  print("Top 5 this month")

  for index, movie in enumerate(results):
    index += 1
    color = bcolors.CYAN if index % 2 == 0 else bcolors.PINK
    bcolors.print_color(str(index) + ".\nName: " + get_movie_name(curs, int(movie[0])), color)

  return

def recommend_movies(curs: cursor, user_id: int) -> None:
  while get_input(["mytop", "generaltop", "followertop", "forme", "top5"],
    [get_top_movies, get_top_general_movies, get_follower_top, get_for_me, get_top_5],
    (curs, user_id), (curs, user_id), (curs, user_id), (curs, user_id), (curs, user_id)): continue

  return

def movies_start(curs: object, user_id: int) -> None:
  """
  the start page for the movies page

  Args:
      curs (object): cursor connected to the database
      user_id (int): the id of the user
  """
  bcolors.print_color("\nWelcome to movies", bcolors.GREEN)

  while get_input(["search", "recommend"], [movie_search, recommend_movies], (curs, user_id), (curs, user_id)): continue

  return