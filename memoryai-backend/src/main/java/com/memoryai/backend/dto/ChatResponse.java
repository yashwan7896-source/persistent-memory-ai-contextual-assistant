package com.memoryai.backend.dto;

import java.time.Instant;
import java.util.List;

public class ChatResponse {

    private String reply;
    private String userId;
    private Instant timestamp = Instant.now();
    // Placeholder - Part 3+ populates this with real retrieved memories
    private List<Object> memoriesUsed;

    public ChatResponse() {}

    public ChatResponse(String reply, String userId, List<Object> memoriesUsed) {
        this.reply = reply;
        this.userId = userId;
        this.memoriesUsed = memoriesUsed;
    }

    public String getReply() { return reply; }
    public void setReply(String reply) { this.reply = reply; }

    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }

    public Instant getTimestamp() { return timestamp; }
    public void setTimestamp(Instant timestamp) { this.timestamp = timestamp; }

    public List<Object> getMemoriesUsed() { return memoriesUsed; }
    public void setMemoriesUsed(List<Object> memoriesUsed) { this.memoriesUsed = memoriesUsed; }
}
