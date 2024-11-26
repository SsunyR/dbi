package Grad_Project.Discord_Bot_Initializer.service;

import Grad_Project.Discord_Bot_Initializer.dto.CogsSelectionRequest;
import Grad_Project.Discord_Bot_Initializer.dto.CogsSelectionResponse;
import Grad_Project.Discord_Bot_Initializer.exception.FileProcessingException;
import lombok.extern.slf4j.Slf4j;
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
@Slf4j
public class CogsProcessorService {
    private static final int BUFFER_SIZE = 4096;
    private final ResourceLoader resourceLoader;
    private final String cogsPath;
    private final String botLauncherPath;

    public CogsProcessorService(
            ResourceLoader resourceLoader,
            @Value("${cogs.files.path:/bot/cogs/}") String cogsPath,
            @Value("${botlauncher.files.path:/BotLauncher/}") String botLauncherPath) {
        this.resourceLoader = resourceLoader;
        this.cogsPath = cogsPath;
        this.botLauncherPath = botLauncherPath;
    }

    public List<String> getAvailableCogsFiles() {
        try {
            Resource cogsResource = resourceLoader.getResource("classpath:static/" + cogsPath);
            File cogsDir = cogsResource.getFile();

            return Files.list(cogsDir.toPath())
                    .filter(path -> path.toString().endsWith(".py"))
                    .map(path -> path.getFileName().toString())
                    .collect(Collectors.toList());
        } catch (IOException e) {
            log.error("Failed to read cogs directory", e);
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
            log.error("Failed to process selected files", e);
            throw new FileProcessingException("Error creating zip file", e);
        }
    }

    private byte[] createBotLauncherZip(List<String> selectedFiles) throws IOException {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        Resource botLauncherResource = resourceLoader.getResource("classpath:" + botLauncherPath);
        Resource cogsResource = resourceLoader.getResource("classpath:" + cogsPath);

        try (ZipOutputStream zos = new ZipOutputStream(baos)) {
            // Add BotLauncher files
            addDirectoryToZip(botLauncherResource.getFile(), "BotLauncher", zos);

            // Add selected cogs files
            for (String fileName : selectedFiles) {
                addCogFileToZip(cogsResource.getFile().toPath(), fileName, zos);
            }
        }

        return baos.toByteArray();
    }

    private void addDirectoryToZip(File sourceDir, String zipPath, ZipOutputStream zos) throws IOException {
        Path sourcePath = sourceDir.toPath();
        Files.walk(sourcePath)
                .filter(path -> !Files.isDirectory(path))
                .forEach(path -> {
                    try {
                        String relativePath = zipPath + "/" + sourcePath.relativize(path);
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
            log.warn("Cog file not found: {}", fileName);
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