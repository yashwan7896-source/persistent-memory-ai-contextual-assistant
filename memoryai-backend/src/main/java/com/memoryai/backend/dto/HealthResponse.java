package com.memoryai.backend.dto;

public class HealthResponse {
    private String status;
    private String appName;
    private String env;

    public HealthResponse() {}

    public HealthResponse(String status, String appName, String env) {
        this.status = status;
        this.appName = appName;
        this.env = env;
    }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getAppName() { return appName; }
    public void setAppName(String appName) { this.appName = appName; }

    public String getEnv() { return env; }
    public void setEnv(String env) { this.env = env; }
}
