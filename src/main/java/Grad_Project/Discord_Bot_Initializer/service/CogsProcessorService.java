package Grad_Project.Discord_Bot_Initializer.service;

import Grad_Project.Discord_Bot_Initializer.dto.CogsSelectionRequest;
import Grad_Project.Discord_Bot_Initializer.dto.CogsSelectionResponse;
import Grad_Project.Discord_Bot_Initializer.exception.FileProcessingException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.core.io.ResourceLoader;
import org.springframework.core.io.support.ResourcePatternResolver;
import org.springframework.stereotype.Service;

import java.io.*;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.locks.ReentrantLock;
import java.util.stream.Collectors;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
import java.util.zip.ZipOutputStream;

@Service
@Slf4j
public class CogsProcessorService {

    private static final int BUFFER_SIZE = 4096;
    private static final int MAX_ZIP_SIZE = 100 * 1024 * 1024; // 100MB

    private final ResourceLoader resourceLoader;
    private final ResourcePatternResolver resourcePatternResolver;
    private final String cogsPath;
    private final String botLauncherZipPath;

    private final ReentrantLock lock = new ReentrantLock();

    public CogsProcessorService(
            ResourceLoader resourceLoader,
            ResourcePatternResolver resourcePatternResolver,
            @Value("${cogs.files.path:classpath:/static/bot/cogs/}") String cogsPath,
            @Value("${botlauncher.zip.path:classpath:/static/BotLauncher.zip}") String botLauncherZipPath) {
        this.resourceLoader = resourceLoader;
        this.resourcePatternResolver = resourcePatternResolver;
        this.cogsPath = cogsPath;
        this.botLauncherZipPath = botLauncherZipPath;
    }

    public List<String> getAvailableCogsFiles() {
        try {
            Resource[] resources = resourcePatternResolver.getResources(cogsPath + "*.py");
            return Arrays.stream(resources)
                    .map(Resource::getFilename)
                    .collect(Collectors.toList());
        } catch (IOException e) {
            log.error("Failed to read cogs files", e);
            throw new FileProcessingException("Unable to read available cogs files", e);
        }
    }

    public CogsSelectionResponse processSelectedFiles(CogsSelectionRequest request) {
        lock.lock();
        try {
            validateRequest(request);
            long startTime = System.currentTimeMillis();

            byte[] zipContent = addCogsToExistingZip(request.getSelectedFiles());
            logPerformanceMetrics(startTime);

            return CogsSelectionResponse.builder()
                    .fileName("BotLauncher.zip")
                    .content(zipContent)
                    .build();
        } catch (IOException e) {
            log.error("Failed to process selected files", e);
            throw new FileProcessingException("Error updating zip file", e);
        } finally {
            lock.unlock();
        }
    }

    private void validateRequest(CogsSelectionRequest request) {
        if (request == null || request.getSelectedFiles() == null || request.getSelectedFiles().isEmpty()) {
            throw new FileProcessingException("Invalid request: selected files are missing");
        }
    }

    private byte[] addCogsToExistingZip(List<String> selectedFiles) throws IOException {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        Resource botLauncherZipResource = resourceLoader.getResource(botLauncherZipPath);

        try (
                ZipInputStream zis = new ZipInputStream(botLauncherZipResource.getInputStream());
                ZipOutputStream zos = new ZipOutputStream(baos)
        ) {
            ZipEntry entry;
            byte[] buffer = new byte[BUFFER_SIZE];

            while ((entry = zis.getNextEntry()) != null) {
                zos.putNextEntry(new ZipEntry(entry.getName()));
                int len;
                while ((len = zis.read(buffer)) > 0) {
                    zos.write(buffer, 0, len);
                }
                zos.closeEntry();
            }

            int totalSize = 0;

            for (String fileName : selectedFiles) {
                Resource cogResource = resourceLoader.getResource(cogsPath + fileName);
                if (cogResource.exists() && cogResource.isReadable()) {
                    try (InputStream in = cogResource.getInputStream()) {
                        ZipEntry newEntry = new ZipEntry("_internal/cogs/" + fileName);
                        zos.putNextEntry(newEntry);

                        int len;
                        while ((len = in.read(buffer)) > 0) {
                            zos.write(buffer, 0, len);
                            totalSize += len;
                            if (totalSize > MAX_ZIP_SIZE) {
                                throw new FileProcessingException("File size exceeds maximum limit");
                            }
                        }
                        zos.closeEntry();
                    }
                } else {
                    log.warn("Cog file not found or unreadable: {}", fileName);
                }
            }
        }

        return baos.toByteArray();
    }

    private void logPerformanceMetrics(long startTime) {
        long endTime = System.currentTimeMillis();
        log.info("{} completed in {} ms", "processSelectedFiles", (endTime - startTime));
    }
}
