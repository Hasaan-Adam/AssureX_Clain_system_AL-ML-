import { test, expect } from '@playwright/test';

test.describe('AssureX Full End-to-End Test Suite', () => {
  const baseURL = 'http://localhost:5173';

  test.beforeEach(async ({ page }) => {
    // Monitor console errors
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log(`[Browser Console Error]: ${msg.text()}`);
      }
    });
    await page.goto(`${baseURL}/login`);
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await page.reload();
  });


  test('1. Landing Page Loads & Displays Logo and Features', async ({ page }) => {
    await page.goto(baseURL);
    await expect(page).toHaveTitle(/AssureX Claim Engine/);
    
    // Check Logo
    const logo = page.locator('img[alt="AssureX Logo"]').first();
    await expect(logo).toBeVisible();

    // Check Hero text
    await expect(page.locator('text=Warranty Claims').first()).toBeVisible();
    await expect(page.locator('text=Sign In').first()).toBeVisible();
  });

  test('2. User Registration & Auto-Login Flow', async ({ page }) => {
    const timestamp = Date.now();
    const testEmail = `playwright_${timestamp}@test.com`;

    await page.goto(`${baseURL}/register`);
    
    // Fill Registration Form
    await page.fill('input[name="full_name"]', 'Playwright Automated Tester');
    await page.fill('input[name="email"]', testEmail);
    await page.fill('input[name="password"]', 'Password123!');
    await page.fill('input[name="confirmPassword"]', 'Password123!');
    
    // Check terms
    await page.check('input[type="checkbox"]');
    
    // Submit
    await page.click('button[type="submit"]');

    // Should redirect to dashboard and show welcome toast or dashboard content
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    await expect(page).toHaveURL(`${baseURL}/dashboard`);
    console.log('Registration & Auto-login passed successfully!');
  });

  test('3. Admin Login & Console Dashboard Access', async ({ page }) => {
    await page.goto(`${baseURL}/login`);
    
    await page.fill('input[type="email"]', 'admin@assurex.com');
    await page.fill('input[type="password"]', 'admin123');
    
    await page.click('button[type="submit"]');

    // Should redirect to /admin
    await page.waitForURL('**/admin', { timeout: 10000 });
    await expect(page).toHaveURL(`${baseURL}/admin`);
    
    // Check admin console elements
    await expect(page.getByRole('link', { name: 'Admin Console' }).or(page.getByRole('link', { name: 'Dashboard' })).first()).toBeVisible();
    console.log('Admin Login passed successfully!');
  });

  test('4. Reviewer Login & Manual Review Queue', async ({ page }) => {
    await page.goto(`${baseURL}/login`);
    
    await page.fill('input[type="email"]', 'reviewer@assurex.com');
    await page.fill('input[type="password"]', 'reviewer123');
    
    await page.click('button[type="submit"]');

    // Should redirect to /reviews
    await page.waitForURL('**/reviews', { timeout: 10000 });
    await expect(page).toHaveURL(`${baseURL}/reviews`);
    console.log('Reviewer Login & Review Queue passed successfully!');
  });

  test('5. Customer Login, Warranties & Claims Pages', async ({ page }) => {
    await page.goto(`${baseURL}/login`);
    
    await page.fill('input[type="email"]', 'customer@assurex.com');
    await page.fill('input[type="password"]', 'customer123');
    
    await page.click('button[type="submit"]');

    // Should redirect to /dashboard
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    await expect(page).toHaveURL(`${baseURL}/dashboard`);

    // Navigate to Warranties
    await page.goto(`${baseURL}/warranties`);
    await expect(page).toHaveURL(`${baseURL}/warranties`);

    // Navigate to Claims
    await page.goto(`${baseURL}/claims`);
    await expect(page).toHaveURL(`${baseURL}/claims`);

    // Navigate to New Claim form
    await page.goto(`${baseURL}/claims/new`);
    await expect(page).toHaveURL(`${baseURL}/claims/new`);
    console.log('Customer navigation passed successfully!');
  });
});
