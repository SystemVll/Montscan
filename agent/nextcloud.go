package agent

import (
	"fmt"
	"log"
	"os"
	"path"
	"strings"

	"github.com/studio-b12/gowebdav"
)

func (a *Agent) UploadToNextcloud(localPath, remoteFilename string) error {
	if a.config.NextcloudURL == "" || a.config.NextcloudUsername == "" || a.config.NextcloudPassword == "" {
		return fmt.Errorf("Nextcloud credentials not configured")
	}

	webdavURL := fmt.Sprintf("%s/remote.php/dav/files/%s",
		strings.TrimSuffix(a.config.NextcloudURL, "/"),
		a.config.NextcloudUsername,
	)

	client := gowebdav.NewClient(webdavURL, a.config.NextcloudUsername, a.config.NextcloudPassword)

	remotePath := a.config.NextcloudPath
	if err := client.MkdirAll(remotePath, 0755); err != nil {
		log.Printf("Warning: could not create remote directory (may already exist): %v", err)
	}

	data, err := os.ReadFile(localPath)
	if err != nil {
		return fmt.Errorf("failed to read local file: %w", err)
	}

	fullRemotePath := path.Join(remotePath, remoteFilename)
	log.Printf("Uploading to Nextcloud: %s", fullRemotePath)

	if err := client.Write(fullRemotePath, data, 0644); err != nil {
		return fmt.Errorf("failed to upload to Nextcloud: %w", err)
	}

	log.Printf("Successfully uploaded to Nextcloud: %s", fullRemotePath)
	return nil
}
