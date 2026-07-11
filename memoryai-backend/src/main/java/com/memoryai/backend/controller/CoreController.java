package com.memoryai.backend.controller;

import com.memoryai.backend.config.AppProperties;
import com.memoryai.backend.dto.ChatRequest;
import com.memoryai.backend.dto.ChatResponse;
import com.memoryai.backend.dto.HealthResponse;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1")
public class CoreController {

    private final AppProperties appProperties;

    public CoreController(AppProperties appProperties) {
        this.appProperties = appProperties;
    }

    @GetMapping("/health")
    public HealthResponse health() {
        return new HealthResponse("ok", appProperties.getName(), appProperties.getEnv());
    }

    @PostMapping("/chat")
    public ChatResponse chat(@Valid @RequestBody ChatRequest request) {
        // --- STUB ---
        // Real logic (LLM + memory) arrives in Part 6, once Part 3/4/5
        // (Python memory microservice + Java<->Python bridge) exist.
        String reply = String.format(
                "(stub) You said: '%s'. Memory + LLM wiring comes in Part 6.",
                request.getMessage()
        );
        return new ChatResponse(reply, request.getUserId(), List.of());
    }
}
