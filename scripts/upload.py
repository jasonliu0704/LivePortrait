from azure.storage.blob import BlobServiceClient
import os
import argparse

def upload_to_blob_storage(
    connection_string: str,
    container_name: str,
    local_file_path: str,
    directory: str = None,
    blob_name: str = None
) -> str:
    """
    Upload a file to Azure Blob Storage.

    Args:
        connection_string: Azure Storage account connection string
        container_name: Name of the container to upload to
        local_file_path: Path to the local file to upload
        directory: Optional directory path within the container
        blob_name: Optional name for the blob (if None, uses filename from local_file_path)

    Returns:
        str: URL of the uploaded blob
    """
    try:
        # Create the BlobServiceClient using the connection string
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # Get a reference to the container
        container_client = blob_service_client.get_container_client(container_name)

        # If blob_name is not provided, use the original filename
        if blob_name is None:
            blob_name = os.path.basename(local_file_path)

        # If directory is provided, prepend it to the blob name
        if directory:
            # Remove leading/trailing slashes and normalize path
            directory = directory.strip('/')
            blob_name = f"{directory}/{blob_name}"

        # Get a blob client for the file
        blob_client = container_client.get_blob_client(blob_name)

        # Upload the file
        with open(local_file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        # Return the blob URL
        return blob_client.url

    except Exception as e:
        raise Exception(f"Failed to upload file to Azure Blob Storage: {str(e)}")

# Example usage:
if __name__ == "__main__":
    # Set up command line argument parser
    parser = argparse.ArgumentParser(description='Upload a file to Azure Blob Storage')
    parser.add_argument('file_path', type=str, help='Path to the file you want to upload')
    parser.add_argument('--directory', '-d', type=str, help='Directory path within the container (e.g., "images/profile")', default=None)

    # Parse arguments
    args = parser.parse_args()

    # Verify if file exists
    if not os.path.exists(args.file_path):
        print(f"Error: File '{args.file_path}' does not exist")
        exit(1)

    # Azure storage settings
    CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=stjasonliu07032540789180;AccountKey=/iPu+qMSWor+9SVqsdiaItknXki6giBvXVKH6YE0TMKIq3pT+gB3Jh/qaJ+xr4BE6NM2Eyup/v//+AStnUjxJg==;EndpointSuffix=core.windows.net"
    CONTAINER_NAME = "liveportrait"

    try:
        blob_url = upload_to_blob_storage(
            connection_string=CONNECTION_STRING,
            container_name=CONTAINER_NAME,
            local_file_path=args.file_path,
            directory=args.directory
        )
        print(f"File uploaded successfully. Blob URL: {blob_url}")
    except Exception as e:
        print(f"Error: {str(e)}")

# python store.py ~/Downloads/0.png -d assets
# azcopy login --account-name stazureaitre643816552456 --account-key DefaultEndpointsProtocol=https;AccountName=stjasonliu07032540789180;AccountKey=/iPu+qMSWor+9SVqsdiaItknXki6giBvXVKH6YE0TMKIq3pT+gB3Jh/qaJ+xr4BE6NM2Eyup/v//+AStnUjxJg==;EndpointSuffix=core.windows.net
