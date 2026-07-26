CREATE TABLE IF NOT EXISTS respondents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS responses (
    respondent_id INTEGER NOT NULL REFERENCES respondents(id),
    tetrad_index INTEGER NOT NULL,
    most_style TEXT NOT NULL,
    least_style TEXT NOT NULL,
    UNIQUE (respondent_id, tetrad_index),
    CHECK (tetrad_index BETWEEN 0 AND 23),
    CHECK (most_style IN ('D', 'I', 'S', 'C')),
    CHECK (least_style IN ('D', 'I', 'S', 'C')),
    CHECK (most_style <> least_style)
);

CREATE TABLE IF NOT EXISTS results (
    respondent_id INTEGER NOT NULL UNIQUE REFERENCES respondents(id),
    most_d INTEGER NOT NULL,
    most_i INTEGER NOT NULL,
    most_s INTEGER NOT NULL,
    most_c INTEGER NOT NULL,
    least_d INTEGER NOT NULL,
    least_i INTEGER NOT NULL,
    least_s INTEGER NOT NULL,
    least_c INTEGER NOT NULL,
    diff_d INTEGER NOT NULL,
    diff_i INTEGER NOT NULL,
    diff_s INTEGER NOT NULL,
    diff_c INTEGER NOT NULL,
    top_styles TEXT NOT NULL,
    bottom_styles TEXT NOT NULL,
    completed_at TEXT NOT NULL DEFAULT (datetime('now'))
);
