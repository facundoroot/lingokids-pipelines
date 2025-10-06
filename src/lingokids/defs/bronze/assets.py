"""
Bronze layer assets that merge small files from MinIO into consolidated datasets.
This demonstrates handling the 'small file problem' common in data lakes.
"""
import json
import os
from pathlib import Path
from io import BytesIO

import dagster as dg
from minio import Minio


# MinIO configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "lingokidsadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "lingokidsadmin")


def get_minio_client() -> Minio:
    """Create MinIO client."""
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )


def merge_files_from_bucket(
    bucket_name: str,
    output_bucket: str,
    output_key: str,
    local_output_path: Path,
    context: dg.AssetExecutionContext
) -> dict:
    """
    Merge all JSON files from a MinIO bucket into a single file.

    Args:
        bucket_name: Source bucket name (e.g., 'raw-events')
        output_bucket: Destination bucket name (e.g., 'bronze')
        output_key: Output file key in bucket (e.g., 'events.json')
        local_output_path: Local path to write merged file
        context: Dagster execution context

    Returns:
        Metadata dict with merge stats
    """
    client = get_minio_client()

    # List all objects in the bucket
    objects = list(client.list_objects(bucket_name, recursive=True))
    context.log.info(f"Found {len(objects)} files in bucket '{bucket_name}'")

    # Collect all JSON lines
    all_lines = []
    total_bytes = 0

    for obj in objects:
        # Skip non-JSON files
        if not obj.object_name.endswith('.json'):
            continue

        context.log.debug(f"Reading {obj.object_name} ({obj.size} bytes)")

        # Get object from MinIO
        response = client.get_object(bucket_name, obj.object_name)
        content = response.read().decode('utf-8')
        response.close()

        # Each line is a JSON object (JSONL format)
        for line in content.strip().split('\n'):
            if line.strip():
                all_lines.append(line)

        total_bytes += obj.size

    context.log.info(f"Merged {len(all_lines)} records from {len(objects)} files ({total_bytes:,} bytes)")

    # Create merged content
    merged_content = '\n'.join(all_lines)
    merged_bytes = merged_content.encode('utf-8')

    # Write to MinIO bronze bucket
    client.put_object(
        output_bucket,
        output_key,
        BytesIO(merged_bytes),
        length=len(merged_bytes),
        content_type='application/json'
    )
    context.log.info(f"✓ Uploaded to MinIO: s3://{output_bucket}/{output_key}")

    # Write to local file for dbt
    local_output_path.parent.mkdir(parents=True, exist_ok=True)
    local_output_path.write_text(merged_content)
    context.log.info(f"✓ Wrote to local: {local_output_path}")

    return {
        "source_files": len(objects),
        "records": len(all_lines),
        "source_bytes": total_bytes,
        "output_bytes": len(merged_bytes),
        "compression_ratio": f"{(1 - len(merged_bytes)/total_bytes)*100:.1f}%"
    }


@dg.asset(
    key=["bronze", "bronze_events"],
    group_name="user_activity_pipeline",
    kinds={"s3", "python"}
)
def bronze_events(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """
    Merge all event files from MinIO raw-events bucket into a single bronze file.
    Demonstrates handling the 'small file problem' by consolidating many small
    files into fewer, larger files optimized for analytical queries.
    """
    project_root = Path(__file__).parent.parent.parent.parent.parent
    local_path = project_root / "dbt" / "data" / "bronze" / "bronze_events.json"

    metadata = merge_files_from_bucket(
        bucket_name="raw-events",
        output_bucket="bronze",
        output_key="events.json",
        local_output_path=local_path,
        context=context
    )

    return dg.MaterializeResult(
        metadata={
            "source_files": dg.MetadataValue.int(metadata["source_files"]),
            "records": dg.MetadataValue.int(metadata["records"]),
            "source_size_bytes": dg.MetadataValue.int(metadata["source_bytes"]),
            "output_size_bytes": dg.MetadataValue.int(metadata["output_bytes"]),
            "preview": dg.MetadataValue.md(
                f"Merged **{metadata['records']}** records from **{metadata['source_files']}** files"
            )
        }
    )


@dg.asset(
    key=["bronze", "bronze_users"],
    group_name="user_activity_pipeline",
    kinds={"s3", "python"}
)
def bronze_users(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """
    Merge all user files from MinIO raw-users bucket into a single bronze file.
    """
    project_root = Path(__file__).parent.parent.parent.parent.parent
    local_path = project_root / "dbt" / "data" / "bronze" / "bronze_users.json"

    metadata = merge_files_from_bucket(
        bucket_name="raw-users",
        output_bucket="bronze",
        output_key="users.json",
        local_output_path=local_path,
        context=context
    )

    return dg.MaterializeResult(
        metadata={
            "source_files": dg.MetadataValue.int(metadata["source_files"]),
            "records": dg.MetadataValue.int(metadata["records"]),
            "source_size_bytes": dg.MetadataValue.int(metadata["source_bytes"]),
            "output_size_bytes": dg.MetadataValue.int(metadata["output_bytes"]),
            "preview": dg.MetadataValue.md(
                f"Merged **{metadata['records']}** records from **{metadata['source_files']}** files"
            )
        }
    )


@dg.asset(
    key=["bronze", "bronze_activities"],
    group_name="user_activity_pipeline",
    kinds={"s3", "python"}
)
def bronze_activities(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """
    Merge all activity files from MinIO raw-activities bucket into a single bronze file.
    """
    project_root = Path(__file__).parent.parent.parent.parent.parent
    local_path = project_root / "dbt" / "data" / "bronze" / "bronze_activities.json"

    metadata = merge_files_from_bucket(
        bucket_name="raw-activities",
        output_bucket="bronze",
        output_key="activities.json",
        local_output_path=local_path,
        context=context
    )

    return dg.MaterializeResult(
        metadata={
            "source_files": dg.MetadataValue.int(metadata["source_files"]),
            "records": dg.MetadataValue.int(metadata["records"]),
            "source_size_bytes": dg.MetadataValue.int(metadata["source_bytes"]),
            "output_size_bytes": dg.MetadataValue.int(metadata["output_bytes"]),
            "preview": dg.MetadataValue.md(
                f"Merged **{metadata['records']}** records from **{metadata['source_files']}** files"
            )
        }
    )
