package com.memoryai.backend.dto;

import jakarta.validation.constraints.NotBlank;

public class ChatRequest {

    @NotBlank(message = "user_id is required")
    private String userId;

    @NotBlank(message = "message is required")
    private String message;

    public ChatRequest() {}

    public ChatRequest(String userId, String message) {
        this.userId = userId;
        this.message = message;
    }

    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }

    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
}
