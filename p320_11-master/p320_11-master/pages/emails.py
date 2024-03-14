from pages.interface_funtcions import *
from psycopg2._psycopg import cursor
import queries


def add_email(curs: cursor, user_id: int) -> None:
    email = input("Please provide an email to add to your account: ")

    sql = """select count(*) from emails where user_id = %s and email_address = %s"""
    data = (user_id, email)
    curs.execute(sql, data)
    info = curs.fetchone()

    if info[0] != 0:
        print("Email is already associated with your account!")
        return

    queries.create_email(curs, user_id, email)

    print("Email added successfully!")

    return


def remove_email(curs: cursor, user_id: int) -> None:
    email = input("Please provide an email to remove from your account: ")

    sql = """select count(*) from emails where user_id = %s and email_address = %s"""
    data = (user_id, email)
    curs.execute(sql, data)
    info = curs.fetchone()

    if info[0] != 1:
        print("This email is not associated with your account!")
        return

    queries.remove_email(curs, user_id, email)

    print("Email removed successfully!")

    return


def view_emails(curs: cursor, user_id: int) -> None:
    sql = """select email_address from emails where user_id = %s"""
    data = (user_id, )
    curs.execute(sql, data)
    info = curs.fetchall()

    if len(info) == 0:
        print("No emails associated with this account!")
        return

    print("Your emails: ")
    for email in info:
        print(email[0])

    return


def email_start(curs: cursor, user_id: int) -> None:
  """
  Starts up the email page
  """
  print("Welcome to your emails")
  while get_input(["add", "remove", "view"],
                  [add_email, remove_email, view_emails],
                  (curs, user_id), (curs, user_id), (curs, user_id)): continue
  return