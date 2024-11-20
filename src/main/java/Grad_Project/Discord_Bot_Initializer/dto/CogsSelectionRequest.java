package Grad_Project.Discord_Bot_Initializer.dto;

import jakarta.validation.constraints.NotEmpty;
import lombok.Data;
import java.util.List;

@Data
public class CogsSelectionRequest {
    @NotEmpty(message = "At least one file must be selected")
    private List<String> selectedFiles;
}