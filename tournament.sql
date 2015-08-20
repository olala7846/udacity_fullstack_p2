-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

CREATE TABLE player (
    id serial primary key,
    name text
);

CREATE TABLE match (
    id serial primary key,
    winner integer references player (id),
    loser integer references player (id)
    ON DELETE CASCADE
);

CREATE VIEW match_record AS
SELECT player.id, player.name, count(match.id) AS matched 
FROM player
LEFT JOIN match
ON player.id = match.winner
OR player.id = match.loser
GROUP BY player.id;

CREATE VIEW won_record AS
SELECT player.id, count(match.winner) AS won
FROM player
LEFT JOIN match
ON player.id = match.winner
GROUP BY player.id;

