package Grad_Project.Discord_Bot_Initializer.dto;

import lombok.Builder;
import lombok.Data;
import org.springframework.core.io.Resource;

@Data
@Builder
public class CogsSelectionResponse {
    private String fileName;
    private byte[] content;
    private Resource resource;
}