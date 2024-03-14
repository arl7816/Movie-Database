import datetime
import uuid
from psycopg2._psycopg import cursor
from datetime import date


def create_user(curs: cursor, username: str, password: str, first_name: str, last_name: str) -> int:
    sql = """select count(*) from users where username = %s"""
    data = (username, )
    curs.execute(sql, data)
    if curs.fetchone()[0] != 0:
        return -1

    num = str(int(uuid.uuid4()))
    num = int(num[:9])
    daytime = datetime.datetime.now()
    sql = """insert into users (user_id, password, username, first_name, last_name, creation_date)
        values (%s, %s, %s, %s, %s, %s)"""
    data = (num, password, username, first_name, last_name, daytime)
    curs.execute(sql, data)
    return num


def update_user_login(curs: cursor, user_id: int) -> None:
    daytime = datetime.datetime.now()
    sql = """insert into user_login_time (user_id, time) values (%s, %s)"""
    data = (user_id, daytime)
    curs.execute(sql, data)


def follow_user(curs: cursor, follower_id: int, followed_id: int) -> None:
    sql = """insert into followers (follower_id, followed_id) values (%s, %s)"""
    data = (follower_id, followed_id)
    curs.execute(sql, data)


def get_follower_count(curs: cursor, user_id: int) -> int:
    sql = """select count(*) from followers where followed_id = %s"""
    data = (user_id, )
    curs.execute(sql, data)
    return curs.fetchone()[0]


def get_following_count(curs: cursor, user_id: int) -> int:
    sql = """select count(*) from followers where follower_id = %s"""
    data = (user_id,)
    curs.execute(sql, data)
    return curs.fetchone()[0]


def unfollow_user(curs: cursor, follower_id: int, followed_id: int) -> None:
    sql = """delete from followers where follower_id = %s and followed_id = %s"""
    data = (follower_id, followed_id)
    curs.execute(sql, data)


def create_email(curs: cursor, user_id: int, email: str) -> None:
    sql = """insert into emails (user_id, email_address) values (%s, %s)"""
    data = (user_id, email)
    curs.execute(sql, data)


def remove_email(curs: cursor, user_id: int, email: str) -> None:
    sql = """delete from emails where user_id = %s and email_address = %s"""
    data = (user_id, email)
    curs.execute(sql, data)


def create_collection(curs: cursor, user_id: int, collection_name: str) -> int:
    num = str(int(uuid.uuid4()))
    num = int(num[:9])
    sql = """insert into collection (name, collection_id, user_id) values (%s, %s, %s)"""
    data = (collection_name, num, user_id)
    curs.execute(sql, data)
    return num


def change_collection_name(curs: cursor, collection_id: int, collection_name: str) -> None:
    sql = """update collection set name = %s where collection_id = %s"""
    data = (collection_name, collection_id)
    curs.execute(sql, data)


def delete_collection(curs: cursor, collection_id: int) -> None:
    sql = """delete from collection_movie where collection_id = %s"""
    data = (collection_id, )
    curs.execute(sql, data)

    sql = """delete from collection where collection_id = %s"""
    data = (collection_id, )
    curs.execute(sql, data)


def add_movie_to_collection(curs: cursor, movie_id: int, collection_id: int) -> None:
    sql = """insert into collection_movie (movie_id, collection_id) values (%s, %s)"""
    data = (movie_id, collection_id)
    curs.execute(sql, data)


def remove_movie_from_collection(curs: cursor, movie_id: int, collection_id: int) -> None:
    sql = """delete from collection_movie where movie_id = %s and collection_id = %s"""
    data = (movie_id, collection_id)
    curs.execute(sql, data)


def view_collection(curs: cursor, collection_id: int) -> tuple[str, int, int, int]:
    sql = """select count(*), sum(movie.length) from movie
            inner join collection_movie on collection_movie.collection_id = %s and movie.movie_id = collection_movie.movie_id"""
    data = (collection_id, )
    curs.execute(sql, data)
    fetched = curs.fetchone()

    sql = """select name from collection where collection_id = %s"""
    curs.execute(sql, data)
    collection_name = curs.fetchone()[0]

    if fetched[0] == 0:
        return collection_name, 0, 0, 0

    num_movies = fetched[0]
    duration = fetched[1]
    hours = duration // 60
    minutes = duration % 60
    return collection_name, num_movies, hours, minutes


def view_collections_ordered(curs: cursor, user_id: int) -> None:
    sql = """select collection_id from collection where user_id = %s
            order by name asc"""
    data = (user_id, )
    curs.execute(sql, data)
    i = 1
    for d in curs.fetchall():
        info = view_collection(curs, d[0])
        print(i, ": Collection name:", info[0])
        print("Movies in collection:", info[1])
        print("Total movie duration:", info[2], "h", info[3], "m")
        i += 1


def watch_movie(curs: cursor, user_id: int, movie_id: int) -> None:
    daytime = datetime.datetime.now()
    sql = """insert into watched (user_id, movie_id, time_watched) values (%s, %s, %s)"""
    data = (user_id, movie_id, daytime)
    curs.execute(sql, data)


def watch_collection(curs: cursor, user_id: int, collection_id: int) -> None:
    sql = """select movie_id from collection_movie where collection_id = %s"""
    data = (collection_id, )
    curs.execute(sql, data)
    movies = curs.fetchall()
    for movie_id in movies:
        watch_movie(curs, user_id, movie_id)


def get_collection_count(curs: cursor, user_id: int) -> int:
    sql = """select count(*) from collection where user_id = %s"""
    data = (user_id, )
    curs.execute(sql, data)
    return curs.fetchone()[0]


def rate_movie(curs: cursor, user_id: int, movie_id: int, rating: int) -> None:
    sql = """insert into rated (user_id, movie_id, rating) values (%s, %s, %s)"""
    data = (user_id, movie_id, rating)
    curs.execute(sql, data)


def update_movie_rating(curs: cursor, user_id: int, movie_id: int, rating: int) -> None:
    sql = """update rated set rating = %s where user_id = %s and movie_id = %s"""
    data = (rating, user_id, movie_id)
    curs.execute(sql, data)


def get_recent_popular(curs: cursor) -> tuple[tuple[int, int]]:
    today = datetime.datetime.now().date()
    previous = datetime.timedelta(days=90)
    past = today - previous

    sql = """   select movie_id, count(movie_id) as freq
                from watched
                where time_watched between %s and %s
                group by movie_id
                order by freq desc
                limit 20"""
    data = (past, today)
    curs.execute(sql, data)
    return curs.fetchall()


def get_recent_popular_among_followers(curs: cursor, user_id: int) -> tuple[tuple[int, int]]:
    today = datetime.datetime.now().date()
    previous = datetime.timedelta(days=90)
    past = today - previous

    sql = """   select movie_id, count(movie_id) as freq
                from watched
                where time_watched between %s and %s and user_id in
                (select follower_id from followers where followed_id = %s)
                group by movie_id
                order by freq desc
                limit 20"""

    data = (past, today, user_id)
    curs.execute(sql, data)
    return curs.fetchall()


def get_top_this_month(curs: cursor) -> tuple[tuple[int, int]]:
    today = datetime.datetime.now().date()
    past = today.replace(day=1)

    sql = """   select movie_id, count(movie_id) as freq
                from watched
                where movie_id in 
                    (select movie_id from release_platform_movie where release_date between %s and %s)
                and time_watched between %s and %s
                group by movie_id
                order by freq desc
                limit 5;"""
    data = (past, today, past, today)
    curs.execute(sql, data)
    return curs.fetchall()


def get_recommended_movies(curs: cursor, user_id: int) -> tuple[tuple[int, int]]:
    sql = """   (select movie_id from rated where movie_id in (
                    select distinct movie_id from genre_movie where genre_id in (
                        select distinct genre_id from genre_movie where movie_id in (
                            select movie_id from watched where user_id in (
                                select distinct user_id
                                from watched
                                where movie_id in (
                                    select movie_id
                                    from watched
                                    where user_id = %s
                                )
                            )
                            group by movie_id
                            order by count(movie_id) DESC
                            limit 5
                        )
                    ) limit 100
                )
                group by movie_id
                order by avg(rating) DESC
                limit 10)
                except
                (select movie_id
                from watched
                where user_id = %s);"""
    data = (user_id, user_id)
    curs.execute(sql, data)
    return curs.fetchall()
