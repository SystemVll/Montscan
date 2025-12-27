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

    agent = None

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
            if self.agent:
                success = self.agent.process_document(file_path)

                if success:
                    try:
                        os.remove(file_path)
                        logger.info(f"Deleted processed file: {file_path}")
                    except Exception as e:
                        logger.error(f"Error deleting file: {e}")
                else:
                    logger.error("Document processor not initialized")

            except Exception as e:
                logger.error(f"Error in file received handler: {e}")
