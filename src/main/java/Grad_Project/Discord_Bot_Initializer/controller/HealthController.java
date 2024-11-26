package Grad_Project.Discord_Bot_Initializer.controller;

import Grad_Project.Discord_Bot_Initializer.service.CogsProcessorService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
@RequiredArgsConstructor
public class HealthController {

    private final CogsProcessorService cogsProcessorService;

    @GetMapping("/health")
    public ResponseEntity<String> healthCheck() {
        try {
            cogsProcessorService.getAvailableCogsFiles();
            return ResponseEntity.ok("Service is healthy");
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Service is unhealthy");
        }
    }
}
