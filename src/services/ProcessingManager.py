import logging
import hashlib
import sqlite3
import time
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class ProcessingManager:
    """
    Asynchronous processing manager:
    - Submits PDF processing tasks to a ThreadPoolExecutor
    - Tracks processed files by SHA256 checksum in a small SQLite DB
    - Retries processing with exponential backoff on failure
    - Removes files on success
    """

    def __init__(self, processor, db_path: str = "./processed.db", max_workers: int = 4, max_retries: int = 3):
        self.processor = processor
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.max_retries = max_retries
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS processed (file_hash TEXT PRIMARY KEY, filename TEXT, processed_at TEXT)"
            )
            conn.commit()
        finally:
            conn.close()

    def _sha256(self, file_path: str) -> str:
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    def _is_already_processed(self, file_hash: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute("SELECT 1 FROM processed WHERE file_hash = ?", (file_hash,))
            return cur.fetchone() is not None
        finally:
            conn.close()

    def _mark_processed(self, file_hash: str, filename: str):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                "INSERT OR REPLACE INTO processed (file_hash, filename, processed_at) VALUES (?, ?, ?)",
                (file_hash, filename, datetime.now(timezone.utc).isoformat())
            )
            conn.commit()
        finally:
            conn.close()

    def submit_file(self, file_path: str):
        if not file_path.lower().endswith(".pdf"):
            logger.debug("submit_file: not a PDF, ignoring: %s", file_path)
            return
        if not os.path.exists(file_path):
            logger.warning("submit_file: file does not exist: %s", file_path)
            return

        file_hash = self._sha256(file_path)
        if self._is_already_processed(file_hash):
            logger.info("File already processed (checksum match), deleting local copy: %s", file_path)
            try:
                os.remove(file_path)
            except Exception as e:
                logger.error("Error deleting duplicate local file: %s", e)
            return

        logger.info("Enqueuing file for processing: %s", file_path)
        self.executor.submit(self._process_with_retries, file_path, file_hash)

    def _process_with_retries(self, file_path: str, file_hash: str):
        backoff = 1
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info("Processing attempt %d for %s", attempt, file_path)
                success = self.processor.process_document(file_path)
                if success:
                    self._mark_processed(file_hash, os.path.basename(file_path))
                    try:
                        os.remove(file_path)
                        logger.info("Deleted processed file: %s", file_path)
                    except Exception as e:
                        logger.error("Error deleting file after processing: %s", e)
                    return
                else:
                    logger.warning("Processor returned False for %s (attempt %d)", file_path, attempt)
            except Exception as e:
                logger.error("Unexpected error processing %s: %s", file_path, e)

            if attempt < self.max_retries:
                logger.info("Retrying in %ds...", backoff)
                time.sleep(backoff)
                backoff *= 2

        logger.error("Failed to process file after %d attempts: %s", self.max_retries, file_path)

