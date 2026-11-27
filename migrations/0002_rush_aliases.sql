CREATE TABLE IF NOT EXISTS rush_aliases (player_id TEXT PRIMARY KEY REFERENCES rush_players(id), display_name TEXT NOT NULL CHECK(length(display_name) BETWEEN 1 AND 4 AND display_name NOT GLOB '*[^A-Z0-9]*'));
CREATE INDEX IF NOT EXISTS rush_aliases_name ON rush_aliases(display_name);
