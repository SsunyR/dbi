package Grad_Project.Discord_Bot_Initializer.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
@RequiredArgsConstructor
public class TokenGuideController {

    @GetMapping("/guide")
    public String tokenGuide(){
        return "token-guide";
    }
}
