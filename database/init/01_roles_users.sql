-- Workshop database roles and users.
-- Adapted from the original make_users.sql with the following corrections:
--   • Fixed typo: NORMAL_USER → sailor in the GRANT statement.
--   • Added CREATE privilege to dj_user so attendees can declare their own
--     schemas via dj.schema().
--   • Added ALL PRIVILEGES on workshop_% schemas so each attendee's personal
--     namespace (workshop_<username>) is writable.
--   • activate_all_roles_on_login=ON (set in docker-compose) handles role
--     activation; SET DEFAULT ROLE is not required.
--   • Stale mysql.db rows with Db='%' (from earlier buggy GRANT … ON `%`.*)
--     are deleted before FLUSH so they cannot shadow schema-level grants.

-- ---------------------------------------------------------------------------
-- Roles
-- ---------------------------------------------------------------------------

CREATE ROLE IF NOT EXISTS 'dj_admin';
GRANT ALL PRIVILEGES ON *.* TO 'dj_admin';

CREATE ROLE IF NOT EXISTS 'dj_user';
-- Allow attendees to create new schemas (needed by dj.schema()).
GRANT CREATE ON *.* TO 'dj_user';
-- Read access to everything.
GRANT SELECT ON *.* TO 'dj_user';
-- Full access to Spyglass pipeline schemas.
GRANT ALL PRIVILEGES ON `common_%`.* TO 'dj_user';
GRANT ALL PRIVILEGES ON `spikesorting_%`.* TO 'dj_user';
GRANT ALL PRIVILEGES ON `decoding_%`.* TO 'dj_user';
GRANT ALL PRIVILEGES ON `position_%`.* TO 'dj_user';
GRANT ALL PRIVILEGES ON `linearization_%`.* TO 'dj_user';
GRANT ALL PRIVILEGES ON `ripple_%`.* TO 'dj_user';
GRANT ALL PRIVILEGES ON `lfp_%`.* TO 'dj_user';
GRANT ALL PRIVILEGES ON `waveform_%`.* TO 'dj_user';
GRANT ALL PRIVILEGES ON `mua_%`.* TO 'dj_user';
GRANT ALL PRIVILEGES ON `workshop_%`.* TO 'dj_user';

CREATE ROLE IF NOT EXISTS 'dj_guest';
GRANT SELECT ON *.* TO 'dj_guest';

-- Remove stale database-level wildcard grants that a mysqldump restore may
-- leave in mysql.db.  These have Db='%' (literal %) and block schema-level
-- INSERT/UPDATE grants below because MySQL evaluates the broader % row first.
-- DELETE is idempotent — safe to run even when the rows do not exist.
DELETE FROM mysql.db WHERE Db = '%' AND User IN ('dj_admin', 'dj_user', 'dj_guest');

-- Flush so role grants above are visible to subsequent GRANT … TO user
-- statements (required when re-running after a mysqldump restore).
FLUSH PRIVILEGES;

-- ---------------------------------------------------------------------------
-- Users
-- ---------------------------------------------------------------------------

-- Admin — instructor use only.
CREATE USER IF NOT EXISTS 'captain' IDENTIFIED BY 'bridge';
GRANT 'dj_admin' TO 'captain';

-- Standard attendee account.
CREATE USER IF NOT EXISTS 'sailor' IDENTIFIED BY 'galley';
GRANT 'dj_user' TO 'sailor';

-- Read-only observer account.
CREATE USER IF NOT EXISTS 'swab' IDENTIFIED BY 'bilge';
GRANT 'dj_guest' TO 'swab';

FLUSH PRIVILEGES;
