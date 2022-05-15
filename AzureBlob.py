import os
import yaml
from os.path import exists
from azure.storage.blob import ContainerClient


def load_config():
    dir_root = os.path.dirname(os.path.abspath(__file__))
    with open(dir_root + "/config.yaml", "r") as ymlfile:
        return yaml.load(ymlfile, Loader=yaml.FullLoader)


def get_file(filename):
    file_exists = exists(filename)
    return file_exists


def upload_file(filename, connection_string, container_name):
    container_client = ContainerClient.from_connection_string(connection_string, container_name)
    blob_client = container_client.get_blob_client(filename)
    with open(filename, "rb") as data:
        print("Uploading file to blob storage...")
        blob_client.upload_blob(data, overwrite=True)
        print(f'{filename} uploaded to blob storage')
    # os.remove(filename)


def get_blob_audio(filename, connection_string, container_name):
    fps = 44100
    container_client = ContainerClient.from_connection_string(connection_string, container_name)
    blob_client = container_client.get_blob_client(blob=filename)
    print(blob_client.url)
    blob_data = blob_client.download_blob()
    data = blob_data.readall()
    # playsound(blob_client.url)
    print(type(data))
    dir_root = os.path.dirname(os.path.abspath(__file__))
    download_path = os.path.join(dir_root, filename)
    print(download_path)

    with open(download_path, mode='bx') as f:
        f.write(data)
    return True
