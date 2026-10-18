import logging
from pathlib import Path

from backend.app.core.config import settings

logger = logging.getLogger("astromind.reports.storage")


class ReportStorageService:
    """
    Unified report storage service supporting both AWS S3 object storage
    and local filesystem storage with transparent fallback.
    """

    def __init__(self) -> None:
        self.provider = settings.REPORT_STORAGE_PROVIDER.lower()
        self.bucket_name = settings.S3_BUCKET_NAME or settings.REPORT_BUCKET
        self.region = settings.AWS_REGION
        self.local_dir = Path("backend/storage/reports")
        self.local_dir.mkdir(parents=True, exist_ok=True)
        self._s3_client = None

    def _get_s3_client(self):
        if self._s3_client is None:
            import boto3

            kwargs = {"region_name": self.region}
            if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
                kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
                kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY

            self._s3_client = boto3.client("s3", **kwargs)
        return self._s3_client

    def save_report(self, report_id: str, pdf_bytes: bytes, chart_id: str = "general") -> str:
        """
        Persists report PDF bytes to storage.
        Returns the storage key identifier.
        """
        s3_key = f"reports/{chart_id}/{report_id}.pdf"

        # 1. Always save a local copy as cache/backup
        local_path = self.local_dir / f"{report_id}.pdf"
        local_path.write_bytes(pdf_bytes)

        # 2. Upload to S3 if configured or if AWS credentials are provided
        if self.provider == "s3" or (settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY):
            try:
                s3 = self._get_s3_client()
                s3.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=pdf_bytes,
                    ContentType="application/pdf",
                    ServerSideEncryption="AES256",
                    Metadata={
                        "report_id": report_id,
                        "chart_id": chart_id,
                    },
                )
                logger.info(f"Report {report_id} successfully stored in S3 bucket: s3://{self.bucket_name}/{s3_key}")
                return s3_key
            except Exception as exc:  # noqa: BLE001
                logger.warning(f"Failed to upload report to S3, falling back to local storage: {exc}")
                return str(local_path)

        return str(local_path)

    def get_report_bytes(self, storage_key: str, report_id: str) -> bytes:
        """Retrieves raw PDF bytes from S3 or local disk."""
        # Check local file first
        local_path = self.local_dir / f"{report_id}.pdf"
        if local_path.exists():
            return local_path.read_bytes()

        # If stored in S3, download from bucket
        if storage_key.startswith("reports/") and (settings.AWS_ACCESS_KEY_ID or self.provider == "s3"):
            try:
                s3 = self._get_s3_client()
                response = s3.get_object(Bucket=self.bucket_name, Key=storage_key)
                return response["Body"].read()
            except Exception as exc:  # noqa: BLE001
                logger.error(f"Failed to fetch report from S3: {exc}")

        # Fallback path check
        path = Path(storage_key)
        if path.exists():
            return path.read_bytes()

        raise FileNotFoundError(f"Report file not found for key: {storage_key}")

    def generate_presigned_download_url(self, s3_key: str, filename: str = "kundli_report.pdf") -> str | None:
        """Generates a secure presigned S3 download URL valid for SIGNED_URL_TTL_SECONDS."""
        if not s3_key.startswith("reports/") or not (settings.AWS_ACCESS_KEY_ID or self.provider == "s3"):
            return None

        try:
            s3 = self._get_s3_client()
            url = s3.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": s3_key,
                    "ResponseContentDisposition": f'attachment; filename="{filename}"',
                },
                ExpiresIn=settings.SIGNED_URL_TTL_SECONDS,
            )
            return url
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"Could not generate presigned URL: {exc}")
            return None


report_storage = ReportStorageService()
