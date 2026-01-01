package agent

import (
	"bytes"
	"encoding/base64"
	"fmt"
	"image/jpeg"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"image/png"
)

func (a *Agent) ExtractImage(pdfPath string) (string, error) {
	log.Printf("Extracting first page from PDF: %s", pdfPath)

	tempDir, err := os.MkdirTemp("", "montscan-")
	if err != nil {
		return "", fmt.Errorf("failed to create temp dir: %w", err)
	}

	defer func(path string) {
		err := os.RemoveAll(path)
		if err != nil {
			log.Printf("Warning: failed to remove temp dir %s: %v", path, err)
		}
	}(tempDir)

	outputPrefix := filepath.Join(tempDir, "page")

	cmd := exec.Command("pdftoppm", "-f", "1", "-l", "1", "-r", "300", "-png", pdfPath, outputPrefix)
	if output, err := cmd.CombinedOutput(); err != nil {
		return "", fmt.Errorf("pdftoppm failed: %w, output: %s", err, string(output))
	}

	files, err := filepath.Glob(outputPrefix + "*.png")
	if err != nil || len(files) == 0 {
		return "", fmt.Errorf("no output image found")
	}

	pngData, err := os.ReadFile(files[0])
	if err != nil {
		return "", fmt.Errorf("failed to read image: %w", err)
	}

	img, err := png.Decode(bytes.NewReader(pngData))
	if err != nil {
		return "", fmt.Errorf("failed to decode PNG: %w", err)
	}

	var jpegBuf bytes.Buffer
	if err := jpeg.Encode(&jpegBuf, img, &jpeg.Options{Quality: 85}); err != nil {
		return "", fmt.Errorf("failed to encode JPEG: %w", err)
	}

	encoded := base64.StdEncoding.EncodeToString(jpegBuf.Bytes())
	log.Printf("Extracted image: %d bytes", len(jpegBuf.Bytes()))
	return encoded, nil
}

func (a *Agent) ExtractImageWithMagick(pdfPath string) (string, error) {
	log.Printf("Extracting first page from PDF using ImageMagick: %s", pdfPath)

	tempFile, err := os.CreateTemp("", "montscan-*.jpg")
	if err != nil {
		return "", fmt.Errorf("failed to create temp file: %w", err)
	}
	tempPath := tempFile.Name()

	if err := tempFile.Close(); err != nil {
		return "", fmt.Errorf("failed to close temp file: %w", err)
	}

	defer func(name string) {
		err := os.Remove(name)
		if err != nil {
			log.Printf("Warning: failed to remove temp file %s: %v", name, err)
		}
	}(tempPath)

	cmd := exec.Command("magick", "convert", "-density", "300", pdfPath+"[0]", "-quality", "85", tempPath)
	if output, err := cmd.CombinedOutput(); err != nil {
		// Try without "magick" prefix for older ImageMagick versions
		cmd = exec.Command("convert", "-density", "300", pdfPath+"[0]", "-quality", "85", tempPath)
		if output, err = cmd.CombinedOutput(); err != nil {
			return "", fmt.Errorf("ImageMagick failed: %w, output: %s", err, string(output))
		}
	}

	data, err := os.ReadFile(tempPath)
	if err != nil {
		return "", fmt.Errorf("failed to read image: %w", err)
	}

	encoded := base64.StdEncoding.EncodeToString(data)
	log.Printf("Extracted image: %d bytes", len(data))
	return encoded, nil
}

func CheckPDFTools() string {
	if _, err := exec.LookPath("pdftoppm"); err == nil {
		return "pdftoppm"
	}

	// Check ImageMagick
	if _, err := exec.LookPath("magick"); err == nil {
		return "imagemagick"
	}
	if _, err := exec.LookPath("convert"); err == nil {
		return "imagemagick"
	}

	return ""
}

func GetPDFToolInstallInstructions() string {
	var sb strings.Builder
	sb.WriteString("PDF processing tools not found. Please install one of:\n")
	sb.WriteString("  - Poppler (pdftoppm):\n")
	sb.WriteString("    Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases\n")
	sb.WriteString("    Linux:   sudo apt-get install poppler-utils\n")
	sb.WriteString("    macOS:   brew install poppler\n")
	sb.WriteString("  - ImageMagick:\n")
	sb.WriteString("    Windows: Download from https://imagemagick.org/script/download.php\n")
	sb.WriteString("    Linux:   sudo apt-get install imagemagick\n")
	sb.WriteString("    macOS:   brew install imagemagick\n")
	return sb.String()
}
