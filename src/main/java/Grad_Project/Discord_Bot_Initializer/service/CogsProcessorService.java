package Grad_Project.Discord_Bot_Initializer.service;

import Grad_Project.Discord_Bot_Initializer.dto.CogsSelectionRequest;
import Grad_Project.Discord_Bot_Initializer.dto.CogsSelectionResponse;
import Grad_Project.Discord_Bot_Initializer.exception.FileProcessingException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.core.io.Resource;
import org.springframework.core.io.ResourceLoader;
import org.springframework.stereotype.Service;

import java.io.*;
import java.nio.file.*;
import java.util.List;
import java.util.stream.Collectors;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

@Service
public class CogsProcessorService {
    private static final Logger logger = LoggerFactory.getLogger(CogsProcessorService.class);
    private static final int BUFFER_SIZE = 4096;

    @Value("${cogs.files.directory:src/main/resources/static/bot/cogs}")
    private String cogPathStr;

    private final ResourceLoader resourceLoader;

    public CogsProcessorService(ResourceLoader resourceLoader) {
        this.resourceLoader = resourceLoader;
    }

    public List<String> getAvailableCogsFiles() {
        try {
            Path cogsDir = Paths.get(cogPathStr);
            return Files.list(cogsDir)
                    .filter(path -> path.toString().endsWith(".py"))
                    .map(path -> path.getFileName().toString())
                    .collect(Collectors.toList());
        } catch (IOException e) {
            logger.error("Failed to read cogs directory", e);
            throw new FileProcessingException("Unable to read available cogs files", e);
        }
    }

    public CogsSelectionResponse processSelectedFiles(CogsSelectionRequest request) {
        try {
            byte[] zipContent = createBotLauncherZip(request.getSelectedFiles());
            Resource resource = new ByteArrayResource(zipContent);

            return CogsSelectionResponse.builder()
                    .fileName("BotLauncher.zip")
                    .content(zipContent)
                    .resource(resource)
                    .build();
        } catch (IOException e) {
            logger.error("Failed to process selected files", e);
            throw new FileProcessingException("Error creating zip file", e);
        }
    }

    private byte[] createBotLauncherZip(List<String> selectedFiles) throws IOException {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        Path botLauncherDir = Paths.get(System.getProperty("user.dir"), "src", "main", "resources", "static", "BotLauncher");
        Path cogsDir = Paths.get(cogPathStr);

        try (ZipOutputStream zos = new ZipOutputStream(baos)) {
            // Add BotLauncher files
            addDirectoryToZip(botLauncherDir, "BotLauncher", zos);

            // Add selected cogs files
            for (String fileName : selectedFiles) {
                addCogFileToZip(cogsDir, fileName, zos);
            }
        }

        return baos.toByteArray();
    }

    private void addDirectoryToZip(Path sourceDir, String zipPath, ZipOutputStream zos) throws IOException {
        Files.walk(sourceDir)
                .filter(path -> !Files.isDirectory(path))
                .forEach(path -> {
                    try {
                        String relativePath = zipPath + "/" + sourceDir.relativize(path).toString();
                        addFileToZip(path, relativePath, zos);
                    } catch (IOException e) {
                        throw new FileProcessingException("Failed to add file to zip: " + path, e);
                    }
                });
    }

    private void addCogFileToZip(Path cogsDir, String fileName, ZipOutputStream zos) throws IOException {
        Path cogFile = cogsDir.resolve(fileName);
        if (Files.exists(cogFile)) {
            addFileToZip(cogFile, "BotLauncher/_internal/cogs/" + fileName, zos);
        } else {
            logger.warn("Cog file not found: {}", fileName);
        }
    }

    private void addFileToZip(Path file, String zipPath, ZipOutputStream zos) throws IOException {
        ZipEntry zipEntry = new ZipEntry(zipPath);
        zos.putNextEntry(zipEntry);

        byte[] buffer = new byte[BUFFER_SIZE];
        try (InputStream in = Files.newInputStream(file)) {
            int len;
            while ((len = in.read(buffer)) > 0) {
                zos.write(buffer, 0, len);
            }
        }

        zos.closeEntry();
    }
}