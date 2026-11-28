ALTER TABLE rush_runs ADD COLUMN rush_eligible INTEGER CHECK(rush_eligible IN (0,1));
