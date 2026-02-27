"""Workshop utilities."""

import os

# Each attendee gets their own schema namespace in the shared MySQL instance.
# The instructor grants ALL PRIVILEGES on `workshop_%.*`, so every schema
# named "workshop_<username>" is writable by the attendee account.
# Tables declared here will live in e.g. "workshop_alice".
SCHEMA_PREFIX = os.getenv("USER", "workshop")
