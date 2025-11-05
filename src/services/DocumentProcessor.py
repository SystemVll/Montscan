import logging
import pytesseract
import ollama
import requests
import os

from requests.auth import HTTPBasicAuth
from datetime import datetime
from pdf2image import convert_from_path

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Handles OCR, AI naming, and Nextcloud upload of scanned documents.

    This class provides methods to:
    - Extract text from PDF files using OCR.
    - Generate descriptive filenames using AI.
    - Upload processed files to Nextcloud via WebDAV.
    """

    def __init__(self):
        """
        Initialize the DocumentProcessor with environment variables.

        Environment variables:
        - OLLAMA_HOST: Host URL for the Ollama AI service.
        - OLLAMA_MODEL: Model name for Ollama AI.
        - NEXTCLOUD_URL: Base URL for Nextcloud.
        - NEXTCLOUD_USERNAME: Username for Nextcloud authentication.
        - NEXTCLOUD_PASSWORD: Password for Nextcloud authentication.
        - NEXTCLOUD_UPLOAD_PATH: Path in Nextcloud to upload files.
        - TESSERACT_PATH: Path to the Tesseract OCR executable.
        """
        self.ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.2')
        self.nextcloud_url = os.getenv('NEXTCLOUD_URL')
        self.nextcloud_username = os.getenv('NEXTCLOUD_USERNAME')
        self.nextcloud_password = os.getenv('NEXTCLOUD_PASSWORD')
        self.nextcloud_path = os.getenv('NEXTCLOUD_UPLOAD_PATH', '/Documents/Scanned')

        tesseract_path = os.getenv('TESSERACT_PATH')
        if tesseract_path and os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file using OCR.

        Args:
            pdf_path (str): Path to the PDF file.

        Returns:
            str: Extracted text from the PDF.
        """
        logger.info(f"Extracting text from PDF: {pdf_path}")

        try:
            images = convert_from_path(pdf_path, dpi=300)

            full_text = []
            for i, image in enumerate(images):
                logger.info(f"Processing page {i + 1}/{len(images)}")
                text = pytesseract.image_to_string(image, lang='eng')
                full_text.append(text)

            combined_text = '\n\n'.join(full_text)
            logger.info(f"Extracted {len(combined_text)} characters from {len(images)} pages")
            return combined_text

        except Exception as e:
            logger.error(f"Error during OCR: {e}")
            return ""

    def generate_filename_with_ai(self, ocr_text: str, original_filename: str) -> str:
        """
        Generate a descriptive filename using AI based on OCR text.

        Args:
            ocr_text (str): Text extracted from the document.
            original_filename (str): Original filename of the document.

        Returns:
            str: AI-generated filename with a .pdf extension.
        """
        logger.info("Generating filename with AI...")

        if not ocr_text.strip():
            logger.warning("No OCR text available, using timestamp")
            return f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        try:
            text_preview = ocr_text[:2000] if len(ocr_text) > 2000 else ocr_text

            prompt = f"""Based on the following scanned document text, generate a concise, descriptive filename (without extension).
The filename should:
- Be 3-6 words maximum
- In french
- Use underscores instead of spaces
- Be descriptive of the document's content
- Use uppercase letters
- Not include special characters except underscores and hyphens
- Include relevant date if mentioned in the document at the end (format: DD-MM-YYYY)

Document text:
{text_preview}

Respond with ONLY the filename, nothing else."""

            response = ollama.chat(
                model=self.ollama_model,
                messages=[{'role': 'user', 'content': prompt}]
            )

            suggested_name = response['message']['content'].strip()

            suggested_name = suggested_name.replace(' ', '_')
            suggested_name = ''.join(c for c in suggested_name if c.isalnum() or c in '_-')
            suggested_name = suggested_name.lower()

            if len(suggested_name) < 5:
                suggested_name = f"{suggested_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            filename = f"{suggested_name}.pdf"
            logger.info(f"AI suggested filename: {filename}")
            return filename

        except Exception as e:
            logger.error(f"Error generating filename with AI: {e}")
            return f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    def upload_to_nextcloud(self, local_path: str, remote_filename: str) -> bool:
        """
        Upload a file to Nextcloud via WebDAV.

        Args:
            local_path (str): Path to the local file.
            remote_filename (str): Filename to use in Nextcloud.

        Returns:
            bool: True if the upload was successful, False otherwise.
        """
        if not self.nextcloud_url or not self.nextcloud_username or not self.nextcloud_password:
            logger.error("Nextcloud credentials not configured")
            return False

        try:
            webdav_base = f"{self.nextcloud_url.rstrip('/')}/remote.php/dav/files/{self.nextcloud_username}"
            remote_path = f"{self.nextcloud_path}/{remote_filename}".replace('//', '/')
            upload_url = f"{webdav_base}{remote_path}"

            logger.info(f"Uploading to Nextcloud: {remote_path}")

            with open(local_path, 'rb') as f:
                file_data = f.read()

            response = requests.put(
                upload_url,
                data=file_data,
                auth=HTTPBasicAuth(self.nextcloud_username, self.nextcloud_password),
                headers={'Content-Type': 'application/pdf'},
                timeout=300,
                verify=False
            )

            if response.status_code in [201, 204]:
                logger.info(f"Successfully uploaded to Nextcloud: {remote_path}")
                return True
            else:
                logger.error(f"Failed to upload to Nextcloud. Status: {response.status_code}, Response: {response.text}")
                return False

        except FileNotFoundError:
            logger.error(f"Local file not found: {local_path}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error uploading to Nextcloud: {e}")
            return False
        except Exception as e:
            logger.error(f"Error uploading to Nextcloud: {e}")
            return False

    def process_document(self, pdf_path: str) -> bool:
        """
        Process a document through the complete pipeline.

        Steps:
        1. Extract text from the PDF using OCR.
        2. Generate a descriptive filename using AI.
        3. Upload the file to Nextcloud.

        Args:
            pdf_path (str): Path to the PDF file.

        Returns:
            bool: True if the document was processed successfully, False otherwise.
        """
        logger.info(f"Processing document: {pdf_path}")

        try:
            ocr_text = self.extract_text_from_pdf(pdf_path)

            new_filename = self.generate_filename_with_ai(ocr_text, os.path.basename(pdf_path))

            if self.upload_to_nextcloud(pdf_path, new_filename):
                logger.info(f"Document processing completed successfully: {new_filename}")
                return True
            else:
                logger.error("Failed to upload to Nextcloud")
                return False

        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return False