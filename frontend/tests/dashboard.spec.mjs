import { test, expect } from '@playwright/test';

const BASE_URL = 'http://127.0.0.1:5173';
const API_URL = 'http://127.0.0.1:8000';

test.describe('Login y Dashboard', () => {
  test('debe cargar la pagina de login', async ({ page }) => {
    await page.goto(BASE_URL);
    await expect(page).toHaveTitle(/SST|ERP/i);
  });

  test('debe mostrar formulario de login', async ({ page }) => {
    await page.goto(BASE_URL);
    await expect(page.locator('#correo')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
  });

  test('debe login exitoso y redirigir al dashboard', async ({ page }) => {
    await page.goto(BASE_URL);
    
    // Llenar formulario
    await page.fill('#correo', 'test@admin.com');
    await page.fill('#password', 'Admin123!');
    
    // Click en submit
    await page.click('button[type="submit"]');
    
    // Esperar redireccion al dashboard
    await page.waitForURL('**/admin/dashboard', { timeout: 10000 });
    
    // Verificar que estamos en el dashboard
    expect(page.url()).toContain('/admin/dashboard');
  });
});

test.describe('API Backend', () => {
  test('backend esta corriendo', async ({ request }) => {
    const response = await request.get(`${API_URL}/health`);
    expect(response.ok()).toBeTruthy();
  });

  test('login API funciona', async ({ request }) => {
    const response = await request.post(`${API_URL}/auth/login-json`, {
      data: {
        correo: 'test@admin.com',
        password: 'Admin123!'
      }
    });
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.access_token).toBeTruthy();
  });
});
