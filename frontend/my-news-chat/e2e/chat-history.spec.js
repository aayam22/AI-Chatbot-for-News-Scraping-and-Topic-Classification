import { test, expect } from "@playwright/test";

const BACKEND_URL = "http://127.0.0.1:8000";

test("chat history persists across archive, refresh, clear, and logout/login", async ({ page, request }) => {
  const uniqueId = Date.now();
  const username = `e2e_user_${uniqueId}`;
  const email = `e2e_${uniqueId}@example.com`;
  const password = "Strong!Pass123";
  const question = `History flow question ${uniqueId}`;
  const answer = `E2E answer (0 prior turns): ${question}`;

  await test.step("register a fresh account through the API", async () => {
    const otpResponse = await request.post(`${BACKEND_URL}/register/request-otp`, {
      data: { username, email, password },
    });

    expect(otpResponse.ok()).toBeTruthy();

    const otpPayload = await otpResponse.json();
    const otp = otpPayload.debug_otp;

    expect(otp).toBeTruthy();

    const registerResponse = await request.post(`${BACKEND_URL}/register`, {
      data: { username, email, otp },
    });

    expect(registerResponse.ok()).toBeTruthy();
  });

  await test.step("log in and send a chat message", async () => {
    await page.goto("/login");
    await page.getByPlaceholder("USERNAME").fill(username);
    await page.getByPlaceholder("PASSWORD").fill(password);
    await page.getByRole("button", { name: "SIGN IN" }).click();
    await page.waitForURL("**/");

    await page.locator("#chat-input").fill(question);
    await page.getByRole("button", { name: "Send" }).click();

    await expect(page.getByText(question, { exact: true })).toBeVisible();
    await expect(page.getByText(answer, { exact: true })).toBeVisible();
  });

  await test.step("refresh the feed and confirm server-backed rehydration", async () => {
    await page.reload();
    await expect(page.getByText(question, { exact: true })).toBeVisible();
    await expect(page.getByText(answer, { exact: true })).toBeVisible();
  });

  await test.step("clear the feed without clearing server memory", async () => {
    const clearMemoryRequest = page
      .waitForRequest((req) => req.url().includes("/clear-memory"), { timeout: 1000 })
      .catch(() => null);

    await page.getByRole("button", { name: "Clear" }).click();

    expect(await clearMemoryRequest).toBeNull();
    await expect(page.getByText(question, { exact: true })).toHaveCount(0);
    await expect(page.getByText(answer, { exact: true })).toHaveCount(0);

    await page.getByRole("link", { name: /archive/i }).click();
    await page.waitForURL("**/archive");

    await expect(page.getByText(question, { exact: true })).toBeVisible();
    await expect(page.getByText(answer, { exact: true })).toBeVisible();
  });

  await test.step("open archive and delete the assistant reply", async () => {
    await expect(page.getByText(question, { exact: true })).toBeVisible();
    await expect(page.getByText(answer, { exact: true })).toBeVisible();

    await page.getByText(answer, { exact: true }).click();
    await page.getByRole("button", { name: "DELETE MESSAGE" }).click();

    await expect(page.getByText(answer, { exact: true })).toHaveCount(0);
  });

  await test.step("return to feed and confirm archive deletion synced", async () => {
    await page.getByRole("link", { name: /feed/i }).click();
    await page.waitForURL("**/");

    await expect(page.getByText(question, { exact: true })).toBeVisible();
    await expect(page.getByText(answer, { exact: true })).toHaveCount(0);
  });

  await test.step("log out and back in, then confirm history still comes from the server", async () => {
    await page.getByRole("button", { name: /logout/i }).click();
    await page.waitForURL("**/login");

    await page.getByPlaceholder("USERNAME").fill(username);
    await page.getByPlaceholder("PASSWORD").fill(password);
    await page.getByRole("button", { name: "SIGN IN" }).click();
    await page.waitForURL("**/");

    await expect(page.getByText(question, { exact: true })).toBeVisible();
    await expect(page.getByText(answer, { exact: true })).toHaveCount(0);
  });
});
