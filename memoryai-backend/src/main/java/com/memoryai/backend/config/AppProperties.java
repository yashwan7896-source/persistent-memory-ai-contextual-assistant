package com.memoryai.backend.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/**
 * Java equivalent of Part 1's src/config/settings.py.
 * Values come from application.properties (or env vars, Spring maps them automatically).
 */
@Component
@ConfigurationProperties(prefix = "app")
public class AppProperties {

    private String name = "MemoryAI";
    private String env = "development";

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getEnv() { return env; }
    public void setEnv(String env) { this.env = env; }
}
