<div align="center">
  <img width="256" height="256" alt="image" src="https://github.com/user-attachments/assets/ced68675-3338-4e7e-b9a0-5a9fc887aeac" />
</div>

<div align="center">
  <p><b>Montscan</b>: Automated scanner document processor with Vision AI, AI naming, and Nextcloud upload! ✨</p>
</div>

---

## ✨ Features

- 📡 **FTP Server** - Receives documents from network scanners
- 👁️ **Vision AI Processing** - Analyzes scanned documents using Ollama vision models
- 🤖 **AI-Powered Naming** - Generates descriptive filenames in French using Ollama
- ☁️ **Nextcloud Integration** - Automatically uploads processed documents via WebDAV
- 🎨 **Colorful CLI** - Beautiful startup banner with configuration overview
- 🐳 **Docker Support** - Easy deployment with Docker Compose

---

## 📋 Table of Contents

- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#️-configuration-options)
- [Usage](#-usage)
- [Docker Deployment](#-docker-deployment)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

---

## 🔧 Prerequisites

- **Go 1.24+**
- **Poppler** (pdftoppm) or **ImageMagick** - For PDF to image conversion
- **Ollama** - [Installation guide](https://ollama.ai/) with a vision model (e.g., `llava`, `llama3.2-vision`)
- **Nextcloud instance** (optional) - For cloud storage integration

---

## 📦 Installation

### Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/SystemVll/Montscan.git
   cd Montscan
   ```

2. **Build the application**
   ```bash
   go build -o montscan .
   ```

3. **Install Poppler or ImageMagick**
    - **Windows**: Download from [GitHub Releases](https://github.com/oschwartz10612/poppler-windows/releases)
    - **Linux**: `sudo apt-get install poppler-utils`
    - **macOS**: `brew install poppler`

4. **Set up Ollama with a vision model**
   ```bash
   # Install Ollama from https://ollama.ai/
   ollama pull llava
   # or any other vision-capable model
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
| `OLLAMA_MODEL` | Ollama vision model to use | `llava` |

---

## 🚀 Usage

### Running Locally

```bash
# Set environment variables (optional, defaults are provided)
export FTP_USERNAME=your-username
export FTP_PASSWORD=your-password
export NEXTCLOUD_URL=https://your-nextcloud.com
export NEXTCLOUD_USERNAME=your-nc-user
export NEXTCLOUD_PASSWORD=your-nc-password

# Run the application
./montscan
```

You should see a colorful startup banner:

```
══════════════════════════════════════════════════════════════════════
║  🖨️  MONTSCAN - Scanner Document Processing System  📄  ║
══════════════════════════════════════════════════════════════════════

📡 FTP Server Configuration:
   ├─ Host: 0.0.0.0
   ├─ Port: 21
   ├─ Username: your-username
   └─ Upload Directory: /path/to/scans

☁️  Nextcloud Integration:
   └─ URL: https://your-nextcloud.com

🤖 AI Processing (Ollama):
   ├─ Host: http://localhost:11434
   └─ Model: llava

📄 PDF Processing:
   └─ Tool: pdftoppm

──────────────────────────────────────────────────────────────────────
✅ All systems initialized - Ready to process documents!
──────────────────────────────────────────────────────────────────────

🚀 Server is now running! Press Ctrl+C to stop.
```

### Using with a Network Scanner

1. Configure your network scanner to send scans via FTP
2. Set the FTP server address to your Montscan instance
3. Use the credentials from your environment variables
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
  -p 21000-21010:21000-21010 \
  -v ./scans:/app/scans \
  -e FTP_USERNAME=scanner \
  -e FTP_PASSWORD=scanner123 \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  --name montscan \
  montscan
```

---

## 🔍 Troubleshooting

### Common Issues

#### FTP Connection Refused
- **Solution**: Check that the FTP port (default 21) is not blocked by firewall
- On Windows, you may need to allow the application through the firewall

#### AI Naming Fails
- **Solution**: Verify Ollama is running and a vision model is downloaded
- Test with: `ollama list` and ensure you have a vision-capable model (e.g., `llava`, `llama3.2-vision`)

#### Nextcloud Upload Fails
- **Solution**: Check Nextcloud credentials and URL
- Ensure the upload path exists in Nextcloud
- Verify WebDAV is enabled on your Nextcloud instance

#### Poppler/ImageMagick Not Found
- **Solution**: Install Poppler or ImageMagick and ensure it's in your system PATH
- Windows: Add Poppler's `bin` folder to PATH environment variable

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- [goftp/server](https://github.com/goftp/server) - Go FTP server library
- [Ollama](https://ollama.ai/) - Local AI vision model runner
- [Nextcloud](https://nextcloud.com/) - Self-hosted cloud storage
- [gowebdav](https://github.com/studio-b12/gowebdav) - WebDAV client for Go
- [fatih/color](https://github.com/fatih/color) - Colorful terminal output

---

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

<div align="center">
  <strong>Made with ❤️ for automated document management</strong>
</div>