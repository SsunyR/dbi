// CogsController.java
package Grad_Project.Discord_Bot_Initializer.controller;

import Grad_Project.Discord_Bot_Initializer.model.CogsFile;
import Grad_Project.Discord_Bot_Initializer.service.CogsProcessorService;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

@Controller
@RequiredArgsConstructor
public class CogsController {

    @Value("classpath:static/bot/cogs/*.py")
    private Resource[] cogsResources;

    private final CogsProcessorService cogsProcessorService;

    @GetMapping("/")
    public String showCogsSelector(Model model) {
        List<CogsFile> cogsFiles = Arrays.stream(cogsResources)
                .map(resource -> {
                    try {
                        String fileName = resource.getFilename();
                        if (fileName != null) {
                            return new CogsFile(fileName.substring(0, fileName.lastIndexOf('.')));
                        }
                        return null;
                    } catch (Exception e) {
                        throw new RuntimeException("Error reading cogs files", e);
                    }
                })
                .filter(file -> file != null)
                .collect(Collectors.toList());

        model.addAttribute("cogsFiles", cogsFiles);
        return "selector";
    }

    @PostMapping("/process")
    public ResponseEntity<Resource> processAndDownload(@RequestBody List<String> selectedFiles) {
        try {
            cogsProcessorService.cleanupFiles();

            List<String> filesWithExtension = selectedFiles.stream()
                    .map(file -> file + ".py")
                    .collect(Collectors.toList());

            // Process files and create zip
            cogsProcessorService.copySelectedFiles(filesWithExtension);
            Path zipFile = cogsProcessorService.createBotLauncherZip();

            // Prepare download
            Resource resource = new UrlResource(zipFile.toUri());

            return ResponseEntity.ok()
                    .contentType(MediaType.APPLICATION_OCTET_STREAM)
                    .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"BotLauncher.zip\"")
                    .body(resource);
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }
}