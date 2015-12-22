--
-- File generated with SQLiteStudio v3.0.6 on 周二 十二月 22 13:20:46 2015
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: task_cost
CREATE TABLE task_cost (
    id           INTEGER     PRIMARY KEY AUTOINCREMENT,
    task_id      INT,
    task_effort  INT,
    task_surplus INT,
    is_current   INT,
    sprint_id    INT,
    team_id      INTEGER,
    reserved     TEXT (1024) 
);


-- Table: daily_cost
CREATE TABLE daily_cost (
    id         INTEGER     PRIMARY KEY AUTOINCREMENT,
    task_id    INT,
    cost_day   DATE,
    task_cost  INT,
    is_current INT,
    sprint_id  INT,
    team_id    INTEGER,
    reserved   TEXT (1024) 
);


-- Table: team_manhours
CREATE TABLE team_manhours (
    id             INTEGER    PRIMARY KEY AUTOINCREMENT,
    team_id        INTEGER,
    is_current     INTEGER,
    sprint_id      INTEGER,
    member_id      INTEGER,
    manhours       INTEGER,
    sprint_workday INTEGER,
    reserved       TEXT (128) 
);


-- Table: team_members_info
CREATE TABLE team_members_info (
    id        INTEGER     PRIMARY KEY AUTOINCREMENT,
    card_id   TEXT (128),
    passwd    TEXT (128),
    name      TEXT (16),
    role      INT,
    team_id   INT         CONSTRAINT team_id_default DEFAULT (1),
    is_on_job INT         CONSTRAINT is_on_job_default DEFAULT (1),
    reserved  TEXT (1024) 
);


-- Table: team_info
CREATE TABLE team_info (
    team_id              INTEGER    PRIMARY KEY,
    team_name            TEXT (32),
    name2                TEXT (32),
    [desc]               TEXT (128),
    [current_sprint_id]  INTEGER
);


-- Table: task_info
CREATE TABLE task_info (
    id            INTEGER    PRIMARY KEY AUTOINCREMENT,
    task_id       INT,
    task_name     TEXT (128),
    task_remarks  TEXT (64),
    task_owner    TEXT (128),
    task_priority INT        CONSTRAINT task_priority_default DEFAULT (2),
    task_status   INT        CONSTRAINT task_status_default DEFAULT (0),
    is_current    INT        CONSTRAINT is_current_default DEFAULT (1),
    sprint_id     INT,
    team_id       INT,
    task_color    INT (0)    CONSTRAINT task_color_default DEFAULT (1) 
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
