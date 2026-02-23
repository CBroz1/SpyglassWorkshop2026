"""Workshop utilities."""

import os

# Each attendee gets their own schema namespace in the shared MySQL instance.
# Tables declared with this prefix will live in e.g. "alice_workshop".
SCHEMA_PREFIX = os.getenv("USER", "workshop")
