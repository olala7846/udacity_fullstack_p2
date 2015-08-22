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
        SELECT * FROM match
        WHERE (winner = {0} AND loser = {1})
        OR (winner = {1} AND loser = {0})
        """.format(pid1, pid2))
    results = cur.fetchall()
    conn.close()
    return len(results) > 0


def namedPlayerStandings():
    """ like playerStandings() but with named tuples

    This method should return a list of named touple ordered by # of wins

    Returns;
        A list of namedtouples player with ['id', 'name', 'wins', 'matches']
    """
    Player = namedtuple('Player', ['id', 'name', 'wins', 'matches'])
    return [Player(*p) for p in playerStandings()]


def recursivePairingWithNamedData(currentPlayerStandings):
    """Pair players by currentPlayerStandings without rematch

    Recursively try to pair players by current ranking and check
    if matched before, recursively try every combinations until
    any available pairing found.

    Returns:
        A list of pairing in touple
        (player1_id, player1_name, player2_id, player2_name)
        and return None if no possible pairings
    """
    # 2 players left, return if not previously matched
    if len(currentPlayerStandings) == 2:
        p1 = currentPlayerStandings[0]
        p2 = currentPlayerStandings[1]
        if not hasPreviouslyMatchd(p1.id, p2.id):
            return [(p1.id, p1.name, p2.id, p2.name)]
        else:
            return None
    # more than 2 players, always select first player
    # and pair with the rest players according to ranking
    # till found a available pairing
    else:
        p1 = currentPlayerStandings[0]
        for p2 in currentPlayerStandings[1:]:
            # Recursively pair with a copy of the rest players
            playerStandingsCopy = list(currentPlayerStandings)
            playerStandingsCopy.remove(p1)
            playerStandingsCopy.remove(p2)
            subPairing = recursivePairingWithNamedData(playerStandingsCopy)
            if subPairing is not None:
                # found available paring! concact and return
                return [(p1.id, p1.name, p2.id, p2.name)] + subPairing
            else:
                # (p1, p2) is not a possible pairing, try next
                continue
        return None


def pairingsWithoutRematch():
    """Returns pairing without player rematch, return Node if impossible"""
    namedCurrentStanding = namedPlayerStandings()
    return recursivePairingWithNamedData(namedCurrentStanding)


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
    if countPlayers() % 2 != 0:
        print "# of player should be even"
        return None
    pairings = pairingsWithoutRematch()
    if not pairings:
        print "Impossible to pair without rematch"
    else:
        return pairingsWithoutRematch()
