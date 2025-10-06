"""Bronze layer component - merges small files from MinIO."""
from dagster import Definitions

from .assets import bronze_activities, bronze_events, bronze_users

defs = Definitions(
    assets=[
        bronze_events,
        bronze_users,
        bronze_activities,
    ]
)
