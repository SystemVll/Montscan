import logging
import os
import magic
from pyftpdlib.handlers import FTPHandler

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("/srv/ftp/uploads").resolve()
MAX_FILE_SIZE = 30 * 1024 * 1024 # 30mo

class ScannerHandler(FTPHandler):
    """
    Custom FTP handler for processing uploaded PDF files.

    This class extends the `pyftpdlib.handlers.FTPHandler` to add functionality
    for handling uploaded files. Specifically, it enqueues PDF files to a
    ProcessingManager for asynchronous processing with retries and idempotency.
    """

    processor = None
    manager = None

    def is_real_pdf(file_path):
        """Check if PDF file is valid, prevent from nullbytes, etc..."""
        try:
            mime = magic.from_file(file_path, mime=True)
            return mime == 'application/pdf'
        except Exception as e:
            logger.error(f"Error checking file type: {e}")
            return False

    def is_safe_path(path: str) -> bool:
        """
        Check if path is safe into UPLOAD_DIR.
        """
        try:
            real = Path(path).resolve()
            return UPLOAD_DIR == real.parent or UPLOAD_DIR in real.parents
        except Exception:
            return False

    def on_file_received(self, file_path):
        """
        Called when a file upload is completed.

        This method is triggered after a file is successfully uploaded to the FTP server.
        It checks if the file is a PDF and enqueues it to the ProcessingManager for
        asynchronous processing. Falls back to synchronous processing if manager is not set.

        Args:
            file_path (str): The path to the uploaded file.
        """
        logger.info(f"File received: {file_path}")

        if not file_path.lower().endswith('.pdf') or not is_real_pdf(file_path):
            logger.warning("Skipping non-PDF file: %s", os.path.basename(file_path))
            return

        if not is_safe_path(file_path):
            logger.error("Rejected unsafe path: %s", file_path)
            return

        try:
            file_size = os.path.getsize(file_path)
        except Exception as e:
            logger.error("Cannot determine file size: %s", e)
            return

        if file_size > MAX_FILE_SIZE:
            logger.warning(
                "File too large (%d bytes). Max allowed is %d. File: %s",
                file_size, MAX_FILE_SIZE, os.path.basename(file_path)
            )
            return

        if self.manager:
            try:
                self.manager.submit_file(file_path)
                logger.info("File enqueued for asynchronous processing: %s", file_path)
            except Exception as e:
                logger.error("Error enqueuing file for processing: %s", e)
        else:
            # Fallback to old behavior if manager not present
            logger.warning("Processing manager not configured, attempting synchronous processing")
            try:
                if self.processor:
                    success = self.processor.process_document(file_path)

                    if success:
                        try:
                            os.remove(file_path)
                            logger.info(f"Deleted processed file: {file_path}")
                        except Exception as e:
                            logger.error(f"Error deleting file: {e}")
                    else:
                        logger.error(f"Failed to process document: {file_path}")
                else:
                    logger.error("Document processor not initialized")

            except Exception as e:
                logger.error(f"Error in file received handler: {e}")
