package Grad_Project.Discord_Bot_Initializer.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        registry.addResourceHandler("/css/**")
                .addResourceLocations("classpath:/static/css/");
        registry.addResourceHandler("/js/**")
                .addResourceLocations("classpath:/static/js/");
        registry.addResourceHandler("/bot/cogs/**")
                .addResourceLocations("classpath:/static/bot/cogs/");
        registry.addResourceHandler("/BotLauncher.zip")
                .addResourceLocations("classpath:/static/BotLauncher.zip");
    }
}
