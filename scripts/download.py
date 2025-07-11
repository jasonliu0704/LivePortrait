from azure.storage.blob import BlobServiceClient
import os
import argparse
import sys

def download_from_blob_storage(
    connection_string: str,
    container_name: str,
    blob_name: str,
    local_file_path: str = None
) -> str:
    """
    Download a file from Azure Blob Storage.

    Args:
        connection_string: Azure Storage account connection string
        container_name: Name of the container to download from
        blob_name: Name of the blob to download
        local_file_path: Optional local path to save the file (if None, uses blob_name)

    Returns:
        str: Path to the downloaded file
    """
    try:
        # Create the BlobServiceClient using the connection string
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # Get a reference to the container
        container_client = blob_service_client.get_container_client(container_name)

        # Get a blob client for the file
        blob_client = container_client.get_blob_client(blob_name)

        # If local_file_path is not provided, use the blob name
        if local_file_path is None:
            local_file_path = os.path.basename(blob_name)

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

        # Download the file
        with open(local_file_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

        return local_file_path

    except Exception as e:
        raise Exception(f"Failed to download file from Azure Blob Storage: {str(e)}")

def download_directory_from_blob_storage(
    connection_string: str,
    container_name: str,
    blob_prefix: str,
    local_dir_path: str = None
) -> list:
    """
    Download all blobs with a given prefix (directory) from Azure Blob Storage.

    Args:
        connection_string: Azure Storage account connection string
        container_name: Name of the container to download from
        blob_prefix: Prefix of the blobs to download (directory in blob storage)
        local_dir_path: Local directory to save files (if None, uses current directory)

    Returns:
        list: List of local file paths downloaded
    """
    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        if local_dir_path is None:
            local_dir_path = os.getcwd()

        # Ensure prefix does not start with a slash
        blob_prefix_clean = blob_prefix.lstrip("/")

        print(f"Searching for blobs with prefix: {blob_prefix_clean}")

        downloaded_files = []
        blobs = container_client.list_blobs(name_starts_with=blob_prefix_clean)

        # Convert to list to get count
        blob_list = list(blobs)
        total_blobs = len(blob_list)

        if total_blobs == 0:
            print(f"No blobs found with prefix: {blob_prefix_clean}")
            return []

        print(f"Found {total_blobs} files to download")

        for i, blob in enumerate(blob_list, 1):
            try:
                # Calculate relative path from the prefix
                if blob_prefix_clean:
                    rel_path = blob.name[len(blob_prefix_clean):].lstrip("/")
                else:
                    rel_path = blob.name

                local_file_path = os.path.join(local_dir_path, rel_path)

                # Create directory structure if it doesn't exist
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

                print(f"Downloading [{i}/{total_blobs}]: {blob.name} -> {local_file_path}")

                # Download the blob
                with open(local_file_path, "wb") as download_file:
                    download_file.write(container_client.get_blob_client(blob.name).download_blob().readall())

                downloaded_files.append(local_file_path)

            except Exception as e:
                print(f"Error downloading {blob.name}: {str(e)}")
                continue

        print(f"Successfully downloaded {len(downloaded_files)} out of {total_blobs} files")
        return downloaded_files

    except Exception as e:
        raise Exception(f"Failed to download directory from Azure Blob Storage: {str(e)}")

def list_blobs_in_directory(
    connection_string: str,
    container_name: str,
    blob_prefix: str
) -> list:
    """
    List all blobs in a directory (with given prefix).

    Args:
        connection_string: Azure Storage account connection string
        container_name: Name of the container
        blob_prefix: Prefix to search for

    Returns:
        list: List of blob names
    """
    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        blob_prefix_clean = blob_prefix.lstrip("/")
        blobs = container_client.list_blobs(name_starts_with=blob_prefix_clean)

        return [blob.name for blob in blobs]

    except Exception as e:
        raise Exception(f"Failed to list blobs: {str(e)}")

# Example usage:
if __name__ == "__main__":
    # Set up command line argument parser
    parser = argparse.ArgumentParser(description='Download a file or directory from Azure Blob Storage')
    parser.add_argument('blob_name', type=str, help='Name of the blob or prefix (directory) to download')
    parser.add_argument('--output', '-o', type=str, help='Local path to save the file or directory', default=None)
    parser.add_argument('--list', '-l', action='store_true', help='List files in directory instead of downloading')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be downloaded without actually downloading')

    # Parse arguments
    args = parser.parse_args()

    # Azure storage settings
    CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=stjasonliu07032540789180;AccountKey=/iPu+qMSWor+9SVqsdiaItknXki6giBvXVKH6YE0TMKIq3pT+gB3Jh/qaJ+xr4BE6NM2Eyup/v//+AStnUjxJg==;EndpointSuffix=core.windows.net"
    CONTAINER_NAME = "liveportrait"

    try:
        # Check if it's a directory (ends with slash) or if --list flag is used
        is_directory = args.blob_name.endswith("/") or args.list

        if args.list:
            # List files in directory
            files = list_blobs_in_directory(
                connection_string=CONNECTION_STRING,
                container_name=CONTAINER_NAME,
                blob_prefix=args.blob_name
            )
            print(f"Files in directory '{args.blob_name}':")
            for f in files:
                print(f"  {f}")
            print(f"Total: {len(files)} files")

        elif args.dry_run:
            # Show what would be downloaded
            files = list_blobs_in_directory(
                connection_string=CONNECTION_STRING,
                container_name=CONTAINER_NAME,
                blob_prefix=args.blob_name
            )
            print(f"Would download {len(files)} files:")
            for f in files:
                print(f"  {f}")

        elif is_directory:
            # Download directory
            files = download_directory_from_blob_storage(
                connection_string=CONNECTION_STRING,
                container_name=CONTAINER_NAME,
                blob_prefix=args.blob_name,
                local_dir_path=args.output
            )
            print(f"Directory downloaded successfully. {len(files)} files downloaded.")
            for f in files:
                print(f"  {f}")
        else:
            # Download single file
            output_path = args.output
            # If output is a directory, save the file inside that directory
            if output_path and os.path.isdir(output_path):
                output_path = os.path.join(output_path, os.path.basename(args.blob_name))
            file_path = download_from_blob_storage(
                connection_string=CONNECTION_STRING,
                container_name=CONTAINER_NAME,
                blob_name=args.blob_name,
                local_file_path=output_path
            )
            print(f"File downloaded successfully to: {file_path}")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

# Example usage:
# python download.py assets/0.png -o ~/Downloads/0.png
# python download.py assets/ -o ~/Downloads/assets/
# python download.py assets/ --list
# python download.py assets/ --dry-run
