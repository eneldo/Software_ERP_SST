import { expect, test } from '@playwright/test';

test('frontend health y login público', async ({ page, request }) => {
  const health = await request.get('/health');
  expect(health.status()).toBe(200);
  expect((await health.text()).trim()).toMatch(/^ok$/i);

  const response = await page.goto('/');
  expect(response?.status()).toBe(200);
  await expect(page).toHaveTitle(/SST|ERP/i);
  await expect(page.locator('#correo')).toBeVisible();
  await expect(page.locator('#password')).toBeVisible();
  await expect(page.locator('button[type="submit"]')).toBeEnabled();
});
