''' 
    File that writes to and reads models from the Oracle Cloud Storage Bucket.
'''

import oci
import io
import os
from dotenv import load_dotenv

load_dotenv()

config = {
    "user": os.environ["OCI_USER"],
    "key_content": os.environ["OCI_KEY_CONTENT"],
    "fingerprint": os.environ["OCI_FINGERPRINT"],
    "tenancy": os.environ["OCI_TENANCY"],
    "region": os.environ["OCI_REGION"],
}

oci.config.validate_config(config)
object_storage_client = oci.object_storage.ObjectStorageClient(config)
namespace = object_storage_client.get_namespace().data
bucket_name = os.environ["OCI_BUCKET_NAME"]


def write_to_object_storage(bucket_name, object_name, content):
    # Create a byte stream from the content (accepts str or bytes)
    if isinstance(content, bytes):
        byte_stream = io.BytesIO(content)
    else:
        byte_stream = io.BytesIO(content.encode('utf-8'))

    # Upload the byte stream to Object Storage
    response = object_storage_client.put_object(
        namespace_name=namespace,
        bucket_name=bucket_name,
        object_name=object_name,
        put_object_body=byte_stream
    )
    print(f"Object '{object_name}' uploaded to bucket '{bucket_name}' with status: {response.status}")


def read_from_object_storage(bucket_name, object_name):
    # Get the object from Object Storage
    response = object_storage_client.get_object(
        namespace_name=namespace,
        bucket_name=bucket_name,
        object_name=object_name
    )

    # Read the content of the object as raw bytes
    content = response.data.content
    print(f"Object '{object_name}' read from bucket '{bucket_name}' ({len(content)} bytes)")
    return content




if __name__ == "__main__":
    test_file = "oracle_test.txt"
    test_content = "This is a test file for Oracle Cloud Storage. Testing read and write operations."
    write_to_object_storage(bucket_name, test_file, test_content)
    read_from_object_storage(bucket_name, test_file)