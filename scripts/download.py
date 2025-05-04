from azure.storage.blob import BlobServiceClient
import os
import argparse

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
        downloaded_files = []
        blobs = container_client.list_blobs(name_starts_with=blob_prefix_clean)
        for blob in blobs:
            rel_path = os.path.relpath(blob.name, blob_prefix_clean)
            local_file_path = os.path.join(local_dir_path, rel_path)
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
            with open(local_file_path, "wb") as download_file:
                download_file.write(container_client.get_blob_client(blob.name).download_blob().readall())
            downloaded_files.append(local_file_path)
        return downloaded_files
    except Exception as e:
        raise Exception(f"Failed to download directory from Azure Blob Storage: {str(e)}")

# Example usage:
if __name__ == "__main__":
    # Set up command line argument parser
    parser = argparse.ArgumentParser(description='Download a file or directory from Azure Blob Storage')
    parser.add_argument('blob_name', type=str, help='Name of the blob or prefix (directory) to download')
    parser.add_argument('--output', '-o', type=str, help='Local path to save the file or directory', default=None)

    # Parse arguments
    args = parser.parse_args()

    # Azure storage settings
    CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=stjasonliu07032540789180;AccountKey=/iPu+qMSWor+9SVqsdiaItknXki6giBvXVKH6YE0TMKIq3pT+gB3Jh/qaJ+xr4BE6NM2Eyup/v//+AStnUjxJg==;EndpointSuffix=core.windows.net"
    CONTAINER_NAME = "liveportrait"

    try:
        # If blob_name ends with a slash or is a directory, treat as directory download
        if args.blob_name.endswith("/") or (args.output and os.path.isdir(args.output)):
            files = download_directory_from_blob_storage(
                connection_string=CONNECTION_STRING,
                container_name=CONTAINER_NAME,
                blob_prefix=args.blob_name,
                local_dir_path=args.output
            )
            print(f"Directory downloaded successfully. {len(files)} files downloaded.")
            for f in files:
                print(f)
        else:
            file_path = download_from_blob_storage(
                connection_string=CONNECTION_STRING,
                container_name=CONTAINER_NAME,
                blob_name=args.blob_name,
                local_file_path=args.output
            )
            print(f"File downloaded successfully to: {file_path}")
    except Exception as e:
        print(f"Error: {str(e)}")

# Example usage:
# python download.py assets/0.png -o ~/Downloads/0.png
