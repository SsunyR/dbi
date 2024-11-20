package Grad_Project.Discord_Bot_Initializer.model;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class CogsFile {
    private String fileName;   // Cogs 파일 이름
    private boolean selected;  // 선택 여부
    private String description; // 파일 설명

    // 생성자: 파일 이름으로 객체 초기화
    public CogsFile(String fileName) {
        this.fileName = fileName;
        this.selected = true; // 생성 시 선택 상태로 설정
        this.description = generateDescription(fileName); // 설명 생성
    }

    /**
     * 파일 설명을 생성하는 메서드
     * @param fileName 파일 이름
     * @return 생성된 설명 문자열
     */
    private String generateDescription(String fileName) {
        if (fileName == null || fileName.isEmpty()) {
            return "No description available.";
        }
        String baseName = fileName.contains(".")
                ? fileName.substring(0, fileName.lastIndexOf('.'))
                : fileName;
        return "Python module for " + baseName;
    }

    /**
     * 디버깅 및 로깅을 위한 객체 표현
     */
    @Override
    public String toString() {
        return "CogsFile{" +
                "fileName='" + fileName + '\'' +
                ", selected=" + selected +
                ", description='" + description + '\'' +
                '}';
    }
}
