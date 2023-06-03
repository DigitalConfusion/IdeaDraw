DROP TABLE IF EXISTS drawings;
DROP TABLE IF EXISTS lobbies;
DROP TABLE IF EXISTS players;

CREATE TABLE drawings (
  drawing_id INTEGER PRIMARY KEY AUTOINCREMENT,
  drawing_stage INTEGER NOT NULL,
  lobby_code TEXT NOT NULL,
  player_id INTEGER NOT NULL,
  vote_total INTEGER DEFAULT 0,
  voters INTEGER DEFAULT 0,
  average_vote FLOAT DEFAULT 0.0,
  drawing_base64 TEXT NOT NULL
);

CREATE TABLE lobbies (
  lobby_id INTEGER PRIMARY KEY AUTOINCREMENT,
  lobby_code TEXT UNIQUE NOT NUll,
  round_length_seconds INTEGER NOT NULL,
  prompt TEXT NOT NULL,
  players TEXT NOT NULL,
  player_count INTEGER DEFAULT 1,
  drawing_stage INTEGER DEFAULT 1,
  first_drawing_start_time INTEGER,
  second_drawing_start_time INTEGER,
  third_drawing_start_time INTEGER,
  first_drawing_win_id INTEGER,
  second_drawing_win_id INTEGER,
  third_drawing_win_id INTEGER
);

CREATE TABLE players (
  player_id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL
);