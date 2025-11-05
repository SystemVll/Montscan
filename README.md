<div align="center">
  <img width="256" height="256" alt="image" src="https://github.com/user-attachments/assets/ced68675-3338-4e7e-b9a0-5a9fc887aeac" />
</div>

<div align="center">
  <p><b>Montscan</b>: Automated scanner document processor with OCR, AI naming, and Nextcloud upload! ✨</p>
</div>

---

## ✨ Features

- 📡 **FTP Server** - Receives documents from network scanners
- 🔍 **OCR Processing** - Extracts text from scanned PDFs using Tesseract
- 🤖 **AI-Powered Naming** - Generates descriptive filenames in French using Ollama
- ☁️ **Nextcloud Integration** - Automatically uploads processed documents via WebDAV
- 🎨 **Colorful CLI** - Beautiful startup banner with configuration overview
- 🐳 **Docker Support** - Easy deployment with Docker Compose

---

## 📋 Table of Contents

- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Docker Deployment](#-docker-deployment)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

---

## 🔧 Prerequisites

- **Python 3.14+**
- **Tesseract OCR** - [Installation guide](https://github.com/tesseract-ocr/tesseract)
- **Poppler** - For PDF to image conversion
- **Ollama** - [Installation guide](https://ollama.ai/) with a language model (e.g., `llama3.2`)
- **Nextcloud instance** (optional) - For cloud storage integration

---

## 📦 Installation

### Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/SystemVll/Montscan.git
   cd montscan
   ```

2. **Install dependencies using uv**
   ```bash
   pip install uv
   uv sync
   ```

3. **Install Tesseract OCR**
   - **Windows**: Download from [GitHub Releases](https://github.com/UB-Mannheim/tesseract/wiki)
   - **Linux**: `sudo apt-get install tesseract-ocr`
   - **macOS**: `brew install tesseract`

4. **Install Poppler**
   - **Windows**: Download from [GitHub Releases](https://github.com/oschwartz10612/poppler-windows/releases)
   - **Linux**: `sudo apt-get install poppler-utils`
   - **macOS**: `brew install poppler`

5. **Set up Ollama**
   ```bash
   # Install Ollama from https://ollama.ai/
   ollama pull llama3.2
   ```

---

### ⚙️ Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `FTP_HOST` | FTP server host address | `0.0.0.0` |
| `FTP_PORT` | FTP server port | `21` |
| `FTP_USERNAME` | FTP authentication username | `scanner` |
| `FTP_PASSWORD` | FTP authentication password | `scanner123` |
| `FTP_UPLOAD_DIR` | Local directory for uploaded files | `./scans` |
| `NEXTCLOUD_URL` | Nextcloud instance URL | - |
| `NEXTCLOUD_USERNAME` | Nextcloud username | - |
| `NEXTCLOUD_PASSWORD` | Nextcloud password | - |
| `NEXTCLOUD_UPLOAD_PATH` | Upload path in Nextcloud | `/Documents/Scanned` |
| `OLLAMA_HOST` | Ollama service URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Ollama model to use | `llama3.2` |
| `TESSERACT_PATH` | Path to Tesseract executable | System PATH |

---

## 🚀 Usage

### Running Locally

```bash
# Activate virtual environment (if using uv)
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Run the application
python src/main.py
```

You should see a colorful startup banner:

```
══════════════════════════════════════════════════════════════════════
║  🖨️  MONTSCAN - Scanner Document Processing System  📄  ║
══════════════════════════════════════════════════════════════════════

📡 FTP Server Configuration:
   ├─ Host: 0.0.0.0
   ├─ Port: 21
   ├─ Username: scanner
   └─ Upload Directory: /path/to/scans

☁️  Nextcloud Integration:
   └─ URL: https://your-nextcloud.com

🤖 AI Processing (Ollama):
   └─ Host: http://localhost:11434

──────────────────────────────────────────────────────────────────────
✅ All systems initialized - Ready to process documents!
──────────────────────────────────────────────────────────────────────

🚀 Server is now running! Press Ctrl+C to stop.
```

### Using with a Network Scanner

1. Configure your network scanner to send scans via FTP
2. Set the FTP server address to your Montscan instance
3. Use the credentials from your `.env` file
4. Scan a document - it will be automatically processed!

---

## 🐳 Docker Deployment

### Using Docker Compose

1. **Update environment variables in `docker-compose.yml`**

2. **Build and start the container**
   ```bash
   docker-compose up -d
   ```

3. **View logs**
   ```bash
   docker-compose logs -f
   ```

4. **Stop the container**
   ```bash
   docker-compose down
   ```

### Using Docker directly

```bash
# Build the image
docker build -t montscan .

# Run the container
docker run -d \
  -p 21:21 \
  -v ./scans:/app/scans \
  --env-file .env \
  --name montscan \
  montscan
```

---

## 🔍 Troubleshooting

### Common Issues

#### FTP Connection Refused
- **Solution**: Check that the FTP port (default 21) is not blocked by firewall
- On Windows, you may need to allow Python through the firewall

#### OCR Not Working
- **Solution**: Ensure Tesseract is installed and `TESSERACT_PATH` is set correctly
- Test with: `tesseract --version`

#### AI Naming Fails
- **Solution**: Verify Ollama is running and the model is downloaded
- Test with: `ollama list` and `ollama run llama3.2 "Hello"`

#### Nextcloud Upload Fails
- **Solution**: Check Nextcloud credentials and URL
- Ensure the upload path exists in Nextcloud
- Verify WebDAV is enabled on your Nextcloud instance

#### Poppler Not Found
- **Solution**: Install Poppler and ensure it's in your system PATH
- Windows: Add Poppler's `bin` folder to PATH environment variable

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- [pyftpdlib](https://github.com/giampaolo/pyftpdlib) - Python FTP server library
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - OCR engine
- [Ollama](https://ollama.ai/) - Local AI model runner
- [Nextcloud](https://nextcloud.com/) - Self-hosted cloud storage

---

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

<div align="center">
  <strong>Made with ❤️ for automated document management</strong>
</div>

