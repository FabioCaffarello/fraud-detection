from io import BytesIO

from logger.log import get_logger_from_env
from minio import Minio
from minio.error import S3Error

logger = get_logger_from_env(__name__)


class MinioClient:
    """
    A client class for interacting with a Minio server.

    This class provides methods for creating buckets, uploading and downloading objects,
    listing buckets and objects, and generating URIs for accessing objects on a Minio
    server.

    Initialization:
        endpoint (str): The URL of the Minio server.
        access_key (str): Access key for authentication.
        secret_key (str): Secret key for authentication.
        secure (bool, optional): If True, use a secure (HTTPS) connection. Defaults to False.

    Example Usage:
    ```
    minio = MinioClient(
        endpoint="http://minio.example.com",
        access_key="your_access_key",
        secret_key="your_secret_key"
    )
    minio.create_bucket("my_bucket")
    minio.upload_file("my_bucket", "example.txt", "path/to/local/file.txt")
    objects = minio.list_objects("my_bucket")
    print(objects)
    ```
    """

    def __init__(self, endpoint: str, access_key: str, secret_key: str, secure: bool = False):
        self._endpoint = endpoint
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )

    def create_bucket(self, bucket_name: str) -> None:
        """
        Create a new bucket on the Minio server.

        Args:
            bucket_name (str): The name of the bucket to be created.

        Raises:
            S3Error: If an error occurs while creating the bucket.
        """
        try:
            self.client.make_bucket(bucket_name)
            logger.info(f"Bucket {bucket_name} created successfully")
        except S3Error as err:
            logger.error(f"Error creating bucket: {err}")
            raise

    def list_buckets(self) -> list[str]:
        """
        List all buckets available on the Minio server.

        Returns:
            List[str]: A list of bucket names.

        Raises:
            S3Error: If an error occurs while listing buckets.
        """
        try:
            buckets = self.client.list_buckets()
            return [bucket.name for bucket in buckets]
        except S3Error as err:
            logger.error(f"Error listing buckets: {err}")
            raise

    def upload_file(self, bucket_name: str, object_name: str, file_path: str) -> str:
        """
        Upload a file to a specified bucket on the Minio server.

        Args:
            bucket_name (str): The name of the target bucket.
            object_name (str): The name of the object in the bucket.
            file_path (str): The local path to the file to be uploaded.

        Returns:
            str: The URI of the uploaded file.

        Raises:
            S3Error: If an error occurs while uploading the file.
        """
        try:
            self.client.fput_object(bucket_name, object_name, file_path)
            uri = self._get_uri(bucket_name, object_name)
            logger.info(f"File {file_path} uploaded to {uri}")
            return uri
        except S3Error as err:
            logger.error(f"Error uploading file: {err}")
            raise

    def upload_bytes(self, bucket_name: str, object_name: str, bytes_data: bytes) -> str:
        """
        Upload bytes data to a specified bucket on the Minio server.

        Args:
            bucket_name (str): The name of the target bucket.
            object_name (str): The name of the object in the bucket.
            bytes_data (bytes): The bytes data to be uploaded.

        Returns:
            str: The URI of the uploaded data.

        Raises:
            S3Error: If an error occurs while uploading the bytes data.
        """
        try:
            data_stream = BytesIO(bytes_data) if not isinstance(bytes_data, BytesIO) else bytes_data
            data_size = data_stream.getbuffer().nbytes
            self.client.put_object(bucket_name, object_name, data_stream, data_size)
            uri = self._get_uri(bucket_name, object_name)
            logger.info(f"Bytes data uploaded to {uri}")
            return uri
        except S3Error as err:
            logger.error(f"Error uploading bytes: {err}")
            raise

    def download_file(self, bucket_name: str, object_name: str, file_path: str) -> None:
        """
        Download a file from a specified bucket on the Minio server and save it locally.

        Args:
            bucket_name (str): The name of the source bucket.
            object_name (str): The name of the object to be downloaded.
            file_path (str): The local path where the downloaded file will be saved.

        Raises:
            S3Error: If an error occurs while downloading the file.
        """
        try:
            self.client.fget_object(bucket_name, object_name, file_path)
            logger.info(f"File {object_name} downloaded to {file_path}")
        except S3Error as err:
            logger.error(f"Error downloading file: {err}")
            raise

    def download_file_as_bytes(self, bucket_name: str, object_name: str) -> bytes:
        """
        Download a file from a specified bucket on the Minio server and return it as bytes.

        Args:
            bucket_name (str): The name of the source bucket.
            object_name (str): The name of the object to be downloaded.

        Returns:
            bytes: The content of the downloaded file as bytes.

        Raises:
            S3Error: If an error occurs while downloading the file.
        """
        try:
            response = self.client.get_object(bucket_name, object_name)
            data = response.read()
            logger.info(f"File {object_name} downloaded as bytes")
            return data
        except S3Error as err:
            logger.error(f"Error downloading file as bytes: {err}")
            raise

    def list_objects(self, bucket_name: str) -> list[str]:
        """
        List objects in a specified bucket on the Minio server.

        Args:
            bucket_name (str): The name of the bucket.

        Returns:
            List[str]: A list of object names in the bucket.

        Raises:
            S3Error: If an error occurs while listing objects.
        """
        try:
            objects = self.client.list_objects(bucket_name)
            return [obj.object_name for obj in objects]
        except S3Error as err:
            logger.error(f"Error listing objects: {err}")
            raise

    def _get_uri(self, bucket_name: str, object_name: str) -> str:
        """
        Generate a URI for accessing an object in the Minio server.

        Args:
            bucket_name (str): The name of the bucket containing the object.
            object_name (str): The name of the object for which the URI is generated.

        Returns:
            str: A URI string for accessing the specified object.
        """
        return f"http://{self._endpoint}/{bucket_name}/{object_name}"  # noqa
