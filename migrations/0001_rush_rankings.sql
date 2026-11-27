CREATE TABLE IF NOT EXISTS rush_rooms (id TEXT PRIMARY KEY, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS rush_players (id TEXT PRIMARY KEY, room_id TEXT NOT NULL REFERENCES rush_rooms(id), name TEXT NOT NULL, token_hash TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL, UNIQUE(room_id,name));
CREATE TABLE IF NOT EXISTS rush_runs (player_id TEXT NOT NULL REFERENCES rush_players(id), run_id TEXT NOT NULL, played_at TEXT NOT NULL, points INTEGER NOT NULL, max_combo INTEGER NOT NULL, answered INTEGER NOT NULL, PRIMARY KEY(player_id,run_id));
CREATE INDEX IF NOT EXISTS rush_runs_period ON rush_runs(player_id,played_at);
