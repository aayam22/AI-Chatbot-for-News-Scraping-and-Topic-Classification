import { test, expect } from "@playwright/test";

test("chat history persists across archive, refresh, and logout/login", async ({ page }) => {
  const uniqueId = Date.now();
  const username = `e2e_user_${uniqueId}`;
  const email = `e2e_${uniqueId}@example.com`;
  const password = "Strong!Pass123";
  const question = `History flow question ${uniqueId}`;
  const answer = `E2E answer (0 prior turns): ${question}`;

  await test.step("register a fresh account with debug OTP", async () => {
    await page.goto("/register");
    await page.getByPlaceholder("USERNAME").fill(username);
    await page.getByPlaceholder("EMAIL ADDRESS").fill(email);
    await page.getByPlaceholder("PASSWORD").fill(password);
    await page.getByRole("button", { name: "SEND OTP" }).click();

    const debugOtpBox = page.getByText(/Debug OTP:/);
    await expect(debugOtpBox).toBeVisible();

    const otpText = await debugOtpBox.textContent();
    const otp = otpText?.match(/\d{6}/)?.[0];

    expect(otp).toBeTruthy();

    await page.getByPlaceholder("ENTER OTP").fill(otp);
    await page.getByRole("button", { name: "VERIFY & CREATE ACCOUNT" }).click();
    await page.waitForURL("**/login");
  });

  await test.step("log in and send a chat message", async () => {
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

  await test.step("open archive and delete the assistant reply", async () => {
    await page.getByRole("link", { name: /archive/i }).click();
    await page.waitForURL("**/archive");

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
