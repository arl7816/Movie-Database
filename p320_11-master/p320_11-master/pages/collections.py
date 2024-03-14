from pages.interface_funtcions import *
from psycopg2._psycopg import cursor
import queries

def remove_collection(curs: cursor, user_id: int) -> None:
  name = input("Collection name: ")

  sql = "select collection_id from collection where name = %s and user_id = %s"
  data = (name, user_id)
  curs.execute(sql, data)
  info = curs.fetchone()

  if info is None:
    print("Collection does not exist!")
    return

  id = info[0]
  queries.delete_collection(curs, id)

  return


def rename_collection(curs: cursor, user_id: int) -> None:
  name = input("Current collection name: ")

  sql = "select collection_id from collection where name = %s and user_id = %s"
  data = (name, user_id)
  curs.execute(sql, data)
  info = curs.fetchone()

  if info is None:
    print("Collection does not exist!")
    return

  id = info[0]
  newname = input("New collection name: ")

  sql = "select count(*) from collection where name = %s and user_id = %s"
  data = (newname, user_id)
  curs.execute(sql, data)
  info = curs.fetchone()

  if info[0] != 0:
    print("Collection name already exists!")
    return

  queries.change_collection_name(curs, id, newname)

  return


def view_collections(curs: cursor, user_id: int) -> None:
  """
  [NOT FINISHED]
  allows the user to see the all of their collections
  """

  queries.view_collections_ordered(curs, user_id)

  return


def create_collection(curs: cursor, user_id: int) -> None:
  name = input("Collection name:")

  sql = """select count(*) from collection where user_id = %s and name = %s"""
  data = (user_id, name)
  curs.execute(sql, data)

  if curs.fetchone()[0] != 0:
    print("Collection with name", name, "already exists!")
    return

  queries.create_collection(curs, user_id, name)

  return


def play_collection(curs: cursor, user_id: int) -> None:
  name = input("Collection name:")

  sql = "select collection_id from collection where name = %s and user_id = %s"
  data = (name, user_id)
  curs.execute(sql, data)
  info = curs.fetchone()

  if info is None:
    print("Collection does not exist!")
    return

  id = info[0]

  queries.watch_collection(curs, user_id, id)


def collection_count(curs: cursor, user_id: int) -> None:
  count = queries.get_collection_count(curs, user_id)
  print("Total collections in account:", count)


def collection_start(curs: cursor, user_id: int) -> None:
  """
  Starts up the collection page
  """
  print("\nWelcome to your collections")
  while get_input(["view", "play", "create", "count", "rename", "remove"],
                  [view_collections, play_collection, create_collection, collection_count, rename_collection, remove_collection],
                  (curs, user_id), (curs, user_id), (curs, user_id), (curs, user_id), (curs, user_id), (curs, user_id)): continue
  return