"""
Initialize MinIO with sample data.
Uploads the raw JSON files to their respective buckets.
"""
import os
from pathlib import Path
from minio import Minio
from minio.error import S3Error

# MinIO configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"

def upload_file_to_minio(client: Minio, bucket_name: str, file_path: Path, object_name: str):
    """
    Upload a single file to MinIO bucket.

    Args:
        client: MinIO client
        bucket_name: Target bucket name
        file_path: Path to local file
        object_name: Name of the object in the bucket
    """
    print(f"  Uploading {file_path.name} to {bucket_name}/{object_name}...")

    client.fput_object(
        bucket_name,
        object_name,
        str(file_path),
        content_type='application/json'
    )

    print(f"  ✓ Uploaded successfully")

def main():
    """Main initialization function."""
    print("=" * 60)
    print("MinIO Data Initialization Script")
    print("=" * 60)
    print()

    # Initialize MinIO client
    try:
        client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False
        )
        print("✓ Connected to MinIO")
    except Exception as e:
        print(f"✗ Failed to connect to MinIO: {e}")
        return

    # Source data files (in dbt/data directory or /app/data in Docker)
    if Path("/app/data").exists():
        data_dir = Path("/app/data")
    else:
        data_dir = Path(__file__).parent.parent / "dbt" / "data"

    datasets = [
        ("raw_events.json", "raw-events", "raw_events.json"),
        ("raw_users.json", "raw-users", "raw_users.json"),
        ("raw_activities.json", "raw-activities", "raw_activities.json"),
    ]

    for filename, bucket, object_name in datasets:
        print()
        print(f"Processing {filename}...")
        print("-" * 60)

        file_path = data_dir / filename

        if not file_path.exists():
            print(f"  ✗ File not found: {file_path}")
            continue

        # Upload to MinIO
        try:
            upload_file_to_minio(client, bucket, file_path, object_name)
        except S3Error as e:
            print(f"  ✗ Upload failed: {e}")
            continue

    print()
    print("=" * 60)
    print("✓ Initialization complete!")
    print("=" * 60)
    print()
    print("You can view the buckets at: http://localhost:9001")
    print("Login: minioadmin / minioadmin")
    print()

if __name__ == "__main__":
    main()
