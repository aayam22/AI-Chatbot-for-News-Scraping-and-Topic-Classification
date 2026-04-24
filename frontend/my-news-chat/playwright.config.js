import { defineConfig } from "@playwright/test";
import process from "node:process";

const isCI = Boolean(process.env.CI);

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  forbidOnly: isCI,
  retries: isCI ? 1 : 0,
  reporter: "list",
  timeout: 90_000,
  expect: {
    timeout: 15_000,
  },
  use: {
    baseURL: "http://127.0.0.1:4173",
    browserName: "chromium",
    channel: "msedge",
    headless: true,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "off",
  },
  webServer: [
    {
      command: "powershell -ExecutionPolicy Bypass -File .\\scripts\\run-e2e-backend.ps1",
      url: "http://127.0.0.1:8000/docs",
      reuseExistingServer: !isCI,
      timeout: 120_000,
    },
    {
      command: "powershell -ExecutionPolicy Bypass -File .\\scripts\\run-e2e-frontend.ps1",
      url: "http://127.0.0.1:4173/login",
      reuseExistingServer: !isCI,
      timeout: 120_000,
    },
  ],
});
