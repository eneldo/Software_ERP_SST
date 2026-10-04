import { test, expect } from '@playwright/test';

const BASE_URL = 'http://127.0.0.1:5173';

test.describe('Dashboard y Modulos', () => {
  test('dashboard carga correctamente', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.fill('#correo', 'test@admin.com');
    await page.fill('#password', 'Admin123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/admin/dashboard', { timeout: 10000 });
    
    expect(page.url()).toContain('/admin/dashboard');
    await page.waitForTimeout(1000);
    const body = await page.locator('body').textContent();
    expect(body.length).toBeGreaterThan(0);
    console.log('Dashboard: OK');
  });

  test('organizacion/empresas carga', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.fill('#correo', 'test@admin.com');
    await page.fill('#password', 'Admin123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/admin/dashboard', { timeout: 10000 });
    
    await page.goto(`${BASE_URL}/organizacion/empresas`);
    await page.waitForTimeout(2000);
    expect(page.url()).toContain('/organizacion/empresas');
    console.log('Organizacion/Empresas: OK');
  });

  test('planear/politica-sst carga', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.fill('#correo', 'test@admin.com');
    await page.fill('#password', 'Admin123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/admin/dashboard', { timeout: 10000 });
    
    await page.goto(`${BASE_URL}/planear/politica-sst`);
    await page.waitForTimeout(2000);
    expect(page.url()).toContain('/planear/politica-sst');
    console.log('Planear/Politica: OK');
  });

  test('hacer/capacitaciones carga', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.fill('#correo', 'test@admin.com');
    await page.fill('#password', 'Admin123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/admin/dashboard', { timeout: 10000 });
    
    await page.goto(`${BASE_URL}/hacer/capacitaciones`);
    await page.waitForTimeout(2000);
    expect(page.url()).toContain('/hacer/capacitaciones');
    console.log('Hacer/Capacitaciones: OK');
  });

  test('verificar/auditorias carga', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.fill('#correo', 'test@admin.com');
    await page.fill('#password', 'Admin123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/admin/dashboard', { timeout: 10000 });
    
    await page.goto(`${BASE_URL}/verificar/auditorias`);
    await page.waitForTimeout(2000);
    expect(page.url()).toContain('/verificar/auditorias');
    console.log('Verificar/Auditorias: OK');
  });
});
