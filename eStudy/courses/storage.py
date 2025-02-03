from storages.backends.s3boto3 import S3Boto3Storage

class S3VideoStorage(S3Boto3Storage):
    """Custom S3 storage backend for video uploads, disabling checksum validation."""
    
    location = ""  # Keep files at the root (or modify as needed)
    default_acl = "private"

    def get_default_settings(self):
        """Override default settings to disable checksum algorithm."""
        settings = super().get_default_settings()
        settings["use_accelerate_endpoint"] = False  # Disable accelerate endpoint
        settings["use_ssl"] = True  # Ensure SSL is used
        settings["s3_use_sigv4"] = True  # Ensure SigV4 authentication
        settings["checksum_algorithm"] = None  # Disable checksum
        return settings
