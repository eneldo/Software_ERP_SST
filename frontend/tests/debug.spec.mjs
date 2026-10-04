import { test, expect } from '@playwright/test';

const BASE_URL = 'http://127.0.0.1:5173';

test('debug - capturar todo', async ({ page }) => {
  const logs = [];
  const errors = [];
  
  page.on('console', msg => {
    logs.push(`[${msg.type()}] ${msg.text()}`);
  });
  
  page.on('pageerror', err => {
    errors.push(err.message);
  });

  await page.goto(BASE_URL, { waitUntil: 'networkidle' });
  await page.waitForTimeout(5000);
  
  console.log('=== TODOS LOS LOGS ===');
  logs.forEach(l => console.log(l));
  console.log('=== ERRORES DE PAGINA ===');
  errors.forEach(e => console.log(e));
  console.log('=== HTML CARGADO ===');
  const html = await page.content();
  console.log(html.substring(0, 2000));
  
  await page.screenshot({ path: 'test-results/debug-blank.png', fullPage: true });
});
