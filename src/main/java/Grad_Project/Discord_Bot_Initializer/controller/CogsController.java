package Grad_Project.Discord_Bot_Initializer.controller;

import Grad_Project.Discord_Bot_Initializer.dto.CogsSelectionRequest;
import Grad_Project.Discord_Bot_Initializer.dto.CogsSelectionResponse;
import Grad_Project.Discord_Bot_Initializer.exception.FileProcessingException;
import Grad_Project.Discord_Bot_Initializer.service.CogsProcessorService;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Controller
@RequiredArgsConstructor
public class CogsController {
    private static final Logger logger = LoggerFactory.getLogger(CogsController.class);
    private final CogsProcessorService cogsProcessorService;

    @GetMapping("/")
    public String showCogsSelector(Model model) {
        try {
            List<String> cogsFileNames = cogsProcessorService.getAvailableCogsFiles();
            model.addAttribute("cogsFileNames", cogsFileNames);
            return "selector";
        } catch (Exception e) {
            logger.error("Failed to load Cogs selector", e);
            throw new FileProcessingException("Failed to load Cogs files", e);
        }
    }

    @PostMapping("/download")
    public ResponseEntity<Resource> processAndDownload(
            @Validated @RequestBody CogsSelectionRequest request) {
        try {
            CogsSelectionResponse response = cogsProcessorService.processSelectedFiles(request);

            return ResponseEntity.ok()
                    .contentType(MediaType.APPLICATION_OCTET_STREAM)
                    .header(HttpHeaders.CONTENT_DISPOSITION,
                            "attachment; filename=\"" + response.getFileName() + "\"")
                    .header(HttpHeaders.CONTENT_LENGTH,
                            String.valueOf(response.getContent().length))
                    .header(HttpHeaders.ACCEPT_RANGES, "bytes")
                    .body(response.getResource());
        } catch (Exception e) {
            logger.error("Error processing files for download", e);
            throw new FileProcessingException("Failed to process selected files", e);
        }
    }
}