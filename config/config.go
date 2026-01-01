package config

import (
	"os"
	"strconv"
)

type Config struct {
	// FTP Server settings
	FTPHost      string
	FTPPort      int
	FTPUsername  string
	FTPPassword  string
	FTPUploadDir string

	// NEXTCLOUD Settings
	NextcloudURL      string
	NextcloudUsername string
	NextcloudPassword string
	NextcloudPath     string

	// OLLAMA Settings
	OllamaHost  string
	OllamaModel string
}

func Load() *Config {
	port, err := strconv.Atoi(getEnv("FTP_PORT", "21"))
	if err != nil {
		port = 21
	}

	return &Config{
		FTPHost:           getEnv("FTP_HOST", "0.0.0.0"),
		FTPPort:           port,
		FTPUsername:       getEnv("FTP_USERNAME", "scanner"),
		FTPPassword:       getEnv("FTP_PASSWORD", "scanner123"),
		FTPUploadDir:      getEnv("FTP_UPLOAD_DIR", "./scans"),
		NextcloudURL:      os.Getenv("NEXTCLOUD_URL"),
		NextcloudUsername: os.Getenv("NEXTCLOUD_USERNAME"),
		NextcloudPassword: os.Getenv("NEXTCLOUD_PASSWORD"),
		NextcloudPath:     getEnv("NEXTCLOUD_UPLOAD_PATH", "/Documents/Scanned"),
		OllamaHost:        getEnv("OLLAMA_HOST", "http://localhost:11434"),
		OllamaModel:       getEnv("OLLAMA_MODEL", "llava"),
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
