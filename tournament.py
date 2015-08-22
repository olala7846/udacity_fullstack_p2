#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
from collections import namedtuple


def connect(database_name="tournament"):
    """Connect to the PostgreSQL database.  Returns a database connection. and a cursor"""
    try:
        conn = psycopg2.connect("dbname={}".format(database_name))
        cursor = conn.cursor()
        return conn, cursor
    except:
        print "Error trying connect to DB {}".format(database_name)


def deleteMatches():
    """Remove all the match records from the database."""
    conn, cur = connect()
    cur.execute("""DELETE FROM match;""")
    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    conn, cur = connect()
    cur.execute("""DELETE FROM player;""")
    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn, cur = connect()
    cur.execute("""SELECT count(*) from player;""")
    result = cur.fetchone()
    conn.close()
    return result[0]


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    conn, cur = connect()
    cur.execute("INSERT INTO player (name) VALUES (%s);", (name, ))
    conn.commit()
    conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn, cur = connect()
    cur.execute("""SELECT * FROM player_standings""")
    results = cur.fetchall()
    conn.close()
    return results


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    # should raise exception on input error? maybe winner == loser
    conn, cur = connect()
    cur.execute(
        "INSERT INTO MATCH (winner, loser) VALUES (%s, %s);", (winner, loser))
    conn.commit()
    conn.close()


def hasPreviouslyMatchd(pid1, pid2):
    conn, cur = connect()
    cur.execute("""
        SELECT * FROM matches
        WHERE (winner = {0} AND loser = {1})
        OR (winner = {1} AND loser = {0})
        """)
    results = conn.fetchall()
    conn.close()
    return len(results) > 0


def namedPlayerStandings():
    Player = namedtuple('Player', ['id', 'name', 'wins', 'matches'])
    return [Player(*p) for p in playerStandings()]


def recursivePairingWithNamedData(namedCurrentStandings):
    # 2 players left, if previously matched return None
    if len(namedCurrentStandings) == 2:
        p1 = currentStandings[0]
        p2 = currentStandings[1]
        if not hasPreviouslyMatchd(p1.id, p2.id):
            return [(p1.id, p1.name), (p2.id, p2.name)]
        else:
            return None
    else:
        p1 = currentStandings[0]
        for p2 in currentStandings[1:]:
            leftInStandings = list(currentStandings)
            leftInStandings.remove(p1)
            leftInStandings.remove(p2)
            subPairing = recursivePairingWithNamedData(leftInStandings)
            if subPairing is None:
                continue
            else:
                return [(p1.id, p1.name, p2.id, p2.name)] + subPairing
        return None


def pairingsWithoutRematch():
    """Returns pairing without player rematch, return Node if impossible"""
    namedCurrentStandings = namedPlayerStandings()
    return recursivePairingWithNamedData(namedCurrentStandings)


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings = playerStandings()
    if countPlayers() % 2 != 0
        print "# of player should be even"
        return None

    return pairingsWithoutRematch()

