// CogsProcessorService.java
package Grad_Project.Discord_Bot_Initializer.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.util.FileSystemUtils;

import java.io.IOException;
import java.nio.file.*;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

@Service
public class CogsProcessorService {

    @Value("${app.cogs.source-path}")
    private String sourcePathStr;

    @Value("${app.cogs.dest-path}")
    private String destPathStr;

    public void copySelectedFiles(List<String> selectedFiles) throws IOException {
        Path sourceDir = Paths.get(System.getProperty("user.dir"), "src", "main", "resources", sourcePathStr);
        Path destDir = Paths.get(System.getProperty("user.dir"), "src", "main", "resources", destPathStr);

        // Create destination directory if it doesn't exist
        Files.createDirectories(destDir);

        // Clean destination directory before copying new files
        FileSystemUtils.deleteRecursively(destDir.toFile());
        Files.createDirectories(destDir);

        for (String fileName : selectedFiles) {
            Path sourcePath = sourceDir.resolve(fileName);
            Path destPath = destDir.resolve(fileName);

            if (Files.exists(sourcePath)) {
                Files.copy(sourcePath, destPath, StandardCopyOption.REPLACE_EXISTING);
            } else {
                throw new IOException("Source file not found: " + fileName);
            }
        }
    }

    public Path createBotLauncherZip() throws IOException {
        Path botLauncherDir = Paths.get(System.getProperty("user.dir"), "src", "main", "resources", "static", "BotLauncher");
        Path zipFile = Paths.get(System.getProperty("user.dir"), "src", "main", "resources", "static", "BotLauncher.zip");

        try (ZipOutputStream zos = new ZipOutputStream(Files.newOutputStream(zipFile))) {
            Files.walk(botLauncherDir)
                    .filter(path -> !Files.isDirectory(path))
                    .forEach(path -> {
                        ZipEntry zipEntry = new ZipEntry(botLauncherDir.relativize(path).toString());
                        try {
                            zos.putNextEntry(zipEntry);
                            Files.copy(path, zos);
                            zos.closeEntry();
                        } catch (IOException e) {
                            throw new RuntimeException("Failed to create zip file", e);
                        }
                    });
        }

        return zipFile;
    }

    public void cleanupFiles() throws IOException {

        // Delete the cogs folder in BotLauncher/_internal
        Path cogsDir = Paths.get(System.getProperty("user.dir"), "src", "main", "resources", "static", "BotLauncher", "_internal", "cogs");
        if (Files.exists(cogsDir)) {
            FileSystemUtils.deleteRecursively(cogsDir);
            Files.createDirectories(cogsDir); // Recreate empty cogs directory
        }
    }
}