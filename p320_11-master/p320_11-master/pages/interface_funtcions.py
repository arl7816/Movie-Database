"""
holds some core commands shared between the the user pages
@author Alex Lee
"""

from psycopg2._psycopg import cursor

class DataStream:
  """
  Holds the contents of a SQL command into a stream data structure
  (MUST be a SELECT statement)
  """
  def __init__(self, curs: cursor, command: str, args = None) -> None:
    """
    Holds the contents of a SQL command into a stream data structure 
    (MUST be a SELECT statement)

    Args:
        curs (object): the cursor object for SQL injection
        command (str): the SQL command your trying to use
        args (tuple[object], optional): The arguments provided to your SQL command. Defaults to None.
          to use arguments (such as WHERE USERNAME = "Emily") the following formate must be used for 
          the above command parameter {WHERE USERNAME = '%s'} or {WHERE USERNAME = "%s"}. 
          Where 's' is your argument being passed in by args and quotes are used by SQL to know its a 
          argument and not a variable.
    """
    self.arr = []
    if args == None:
      curs.execute(command)
    else:
      curs.execute(command % args)
    
    self.arr = curs.fetchall()

    self.size = len(self.arr)
    self.index = 0
  
  def get_size(self) -> int:
    """
    Gets the total number of rows in the table

    Returns:
      int: the number of rows in the table
    """
    return self.size

  def get_all(self) -> list[tuple[object]]:
    """
    Returns an array with all the data streams contents

    Returns:
        list[tuple[object]]: all of the contents of a command
    """
    return self.arr

  def peek(self) -> object:
    """
    Returns the next element in the data set, without moving onto the next one

    Post-req:
      the data stream points to the SAME row of the SQL command 

    Returns:
      object: the content of the command (None, if end of stream reached)
    """
    if (self.size) <= self.index:
      return None
    
    return self.arr[self.index]
  
  def next(self) -> object:
    """
    Returns the next element in the data set, with moving onto the next one

    Post-req:
      the data stream points to the NEXT row of the SQL command
    
    Returns:
      object: the content of the command (None if end of stream reached)
    """
    if (self.size) <= self.index:
      return None

    self.index += 1

    return self.arr[self.index - 1]


class bcolors:
  """
  Changes the color of the terminal text.
  \n
  !!!WARNING will set all of terminal below to the color, make sure to reset color
  if desired at the end of the print statement and or string!!!
  """

  PINK = '\033[95m'
  BLUE = '\033[94m'
  CYAN = '\033[96m'
  GREEN = '\033[92m'
  YELLOW = '\033[93m'
  RED = '\033[91m'
  DEFAULT = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'

  def generate_string(string: str, color: str, underline = False, bold = False, end_color = DEFAULT) -> str:
    return (bcolors.UNDERLINE if underline else "") + (bcolors.BOLD if bold else "") + color + string + end_color

  def print_color(string: str, color: str, underline = False, bold = False, end_color = DEFAULT) -> None:
    """
    Prints out a colored string in the command Line

    Args:
        string (str): The string to be printed
        color (str): The color of the string (recommend using the bcolors class)
        underline (bool, optional): Whether or not the text is underlined. Defaults to False.
        bold (bool, optional): whether or not the text is bold. Defaults to False.
        end_color (str, optional): The terminal color after the print statement. 
        Defaults to bcolors.DEFAULT.
    """
    print((bcolors.UNDERLINE if underline else "") + 
          (bcolors.BOLD if bold else "") + 
          color + string + end_color)

def get_str_list(strings: list[str]) -> str:
  """
  Converts an array of strings into a singular one 
  that displays each string in a list such that
  [x1, x2, ..., xn] --> 
  1: x1
  2: x2\n
  ...
  n: xn

  Args:
    strings (list[str]): An array of strings

  Returns:
      str: the list of strings
  """
  return_str = ""
  for index, string in enumerate(strings):
    return_str += str(index + 1) + ": " + string

    if index != len(strings) - 1:
      return_str += "\n" 
  return return_str

def call_function(funct: object, aug: tuple[object]) -> object:
  """
  calls a function using provided arguments if any are provided

  Args:
      funct (object): the function being called
      aug (tuple[object]): the arguments being called as a tuple

  Returns:
      object: the return value of the function call
  """

  if aug == None or type(aug) == tuple and len(aug) == 0:
    return funct()

  if type(aug) != tuple: 
    return funct(aug)

  a = aug
  return funct(*aug)

def get_input(options: list[str], outputs: list[object], *arguments: tuple[object]) -> bool:
  def print_options():
    print("0: back")
    for index, option in enumerate(options):
      print(str(index + 1) + ":", option)

  """
  Prints out the options available to the user and allows the user to select an option which brings them to the next page
  Args:
    options (list[str]): the names of the pages the user can go to
    outputs (list[object]): the functions to be called to start up the page
    *arguments: a arbitrary amount of arguments for each output function where each argument is contained in a tuple. 
      If there are no arguments, provide nothing.
      if at least one function requires a argument, provide all arguments for each corresponding function, for functions with no
      parameters, simply provide an empty tuple '()'

  Raises:
    IndexError: If the number of options does not equal outputs, an error is thrown

  Pre-req: 
    the input names for all options must be a string with at least one non-number character

  Returns true if user wants to move to a new page, false if the user wants to go back in the pages
  """
  if len(options) != len(outputs): 
    raise IndexError("The options must match the number of outputs")
  
  if len(arguments) != 0 and len(arguments) != len(outputs):
    raise IndexError("You have provided arguments that dont account for all functions")
  
  standard_input = len(arguments) == 0
  user_input = ""
  while (True):

    print_options()

    user_input = input("Input: ")

    if user_input.isnumeric():
      user_input = int(user_input) - 1
      if user_input < -1 or user_input > (len(options) - 1):
        print("Invalid range")
        continue

      elif user_input == -1:
        return False
      
      outputs[user_input]() if standard_input else call_function(outputs[user_input], arguments[user_input])
      break

    if not user_input.isnumeric():
      if user_input not in options:
        print("Not a proper option")
        continue

      for i in range(len(options)):
        if options[i] == user_input:
          outputs[i]() if standard_input else call_function(outputs[i], arguments[i])
          return True
        
  return True

def get_unqiue_movies(movies: list[tuple[object]]) -> list[tuple[object]]:
  seen_movies = set()
  new_movies = []
  for movie in movies:
    if movie[0] in seen_movies:
      continue
    new_movies.append(movie)
    seen_movies.add(movie[0])
  return new_movies

def get_user_id(curs: cursor, username: str) -> int:
  """
  Gets the user_id from a given username

  Pre-req: 
    username must be unique to a user_id  

  Args:
    curs (cursor): the cursor object used for SQL injection
    username (str): the given username

  Returns:
    int: the id of the user
  """
  query = "SELECT user_id FROM users WHERE username = '%s'" % username
  #print(DataStream(curs, query).get_all())
  return int(DataStream(curs, query).peek()[0])

def get_movie_name(curs: cursor, movie_id: int):
  return DataStream(curs, "SELECT title FROM movie WHERE movie_id = '%s';" % movie_id).next()[0]