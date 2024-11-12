package Grad_Project.Discord_Bot_Initializer.model;

import lombok.Data;

@Data
public class CogsFile {
    private String fileName;
    private boolean selected;
    private String description;

    public CogsFile(String fileName) {
        this.fileName = fileName;
        this.selected = false;
        this.description = generateDescription(fileName);
    }

    private String generateDescription(String fileName) {
        return "Python module for " + fileName + " functionality";
    }
}