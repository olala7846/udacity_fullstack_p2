-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- close db connections except self
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'TARGET_DB'
AND pid <> pg_backend_pid();

-- drop the tournament database to avoid duplicate
DROP DATABASE IF EXISTS tournament;
-- create a database name tournament
CREATE DATABASE tournament;
-- connect to tournament
\c tournament

-- create tables
CREATE TABLE player (
    player_id SERIAL PRIMARY KEY,
    name text
);

CREATE TABLE match (
    match_id SERIAL PRIMARY KEY,
    winner integer REFERENCES player
    ON DELETE CASCADE,
    loser integer REFERENCES player
    ON DELETE CASCADE,
    CHECK (winner <> loser)
);

-- create view
CREATE VIEW match_record AS
SELECT player.player_id, player.name, COUNT(match.match_id) AS matched 
FROM player
LEFT JOIN match
ON player.player_id = match.winner
OR player.player_id = match.loser
GROUP BY player.player_id;

CREATE VIEW won_record AS
SELECT player.player_id, count(match.winner) AS won
FROM player
LEFT JOIN match
ON player.player_id = match.winner
GROUP BY player.player_id;

CREATE VIEW player_standings AS
SELECT won_record.player_id, name, won, matched
FROM won_record
JOIN match_record
ON won_record.player_id = match_record.player_id
ORDER BY won DESC;
