-- Workshop database roles and users.
-- Adapted from the original make_users.sql with the following corrections:
--   • Fixed typo: NORMAL_USER → sailor in the GRANT statement.
--   • Added CREATE privilege to dj_user so attendees can declare their own
--     schemas via dj.schema().
--   • Added ALL PRIVILEGES on %_workshop schemas so each attendee's personal
--     namespace (<username>_workshop) is writable.
--   • Added SET DEFAULT ROLE ALL for MySQL 8 role activation.

-- ---------------------------------------------------------------------------
-- Roles
-- ---------------------------------------------------------------------------

CREATE ROLE IF NOT EXISTS 'dj_admin';
GRANT ALL PRIVILEGES ON `%`.* TO 'dj_admin';

CREATE ROLE IF NOT EXISTS 'dj_user';
-- Allow attendees to create new schemas (needed by dj.schema()).
GRANT CREATE ON *.* TO 'dj_user';
-- Read access to everything.
GRANT SELECT ON `%`.* TO 'dj_user';
-- Full access to each attendee's personal workshop schema (<username>_workshop).
GRANT ALL PRIVILEGES ON `%\_workshop`.* TO 'dj_user';
-- Full access to Spyglass pipeline schemas.
GRANT ALL PRIVILEGES ON `common\_%`.* TO 'dj_user';
GRANT ALL PRIVILEGES ON `spikesorting\_%`.* TO 'dj_user';
GRANT ALL PRIVILEGES ON `decoding\_%`.* TO 'dj_user';
GRANT ALL PRIVILEGES ON `position\_%`.* TO 'dj_user';
GRANT ALL PRIVILEGES ON `linearization\_%`.* TO 'dj_user';
GRANT ALL PRIVILEGES ON `ripple\_%`.* TO 'dj_user';
GRANT ALL PRIVILEGES ON `lfp\_%`.* TO 'dj_user';
GRANT ALL PRIVILEGES ON `waveform\_%`.* TO 'dj_user';
GRANT ALL PRIVILEGES ON `mua\_%`.* TO 'dj_user';
GRANT ALL PRIVILEGES ON `workshop\_%`.* TO 'dj_user';

CREATE ROLE IF NOT EXISTS 'dj_guest';
GRANT SELECT ON `%`.* TO 'dj_guest';

-- ---------------------------------------------------------------------------
-- Users
-- ---------------------------------------------------------------------------

-- Admin — instructor use only.
CREATE USER IF NOT EXISTS 'captain'@'%' IDENTIFIED BY 'brigde';
GRANT 'dj_admin' TO 'captain'@'%';
SET DEFAULT ROLE ALL TO 'captain'@'%';

-- Standard attendee account.
CREATE USER IF NOT EXISTS 'sailor'@'%' IDENTIFIED BY 'galley';
GRANT 'dj_user' TO 'sailor'@'%';
SET DEFAULT ROLE ALL TO 'sailor'@'%';

-- Read-only observer account.
CREATE USER IF NOT EXISTS 'swab'@'%' IDENTIFIED BY 'bilge';
GRANT 'dj_guest' TO 'swab'@'%';
SET DEFAULT ROLE ALL TO 'swab'@'%';

FLUSH PRIVILEGES;
