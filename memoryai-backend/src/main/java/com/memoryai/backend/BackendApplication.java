package com.memoryai.backend;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * MemoryAI backend entrypoint.
 * Run with: mvn spring-boot:run
 * Then visit http://localhost:8080/api/v1/health
 *
 * This is the Java equivalent of Part 2's original FastAPI version.
 * Chat endpoint is still a stub here too - Part 6 (conversation manager)
 * wires in the real LLM + memory logic.
 */
@SpringBootApplication
public class BackendApplication {
    public static void main(String[] args) {
        SpringApplication.run(BackendApplication.class, args);
    }
}
