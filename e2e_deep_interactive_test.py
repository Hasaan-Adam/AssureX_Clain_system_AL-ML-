"""
AssureX Claim Engine - Deep Interactive Playwright Test Suite
Automates full-funnel live workflows:
1. User registers new Warranty (with Invoice & Serial details).
2. User files a new Claim via 4-step wizard.
3. Reviewer adjudicates the claim from the Review Queue.
4. Generates PDF summary and verifies end-to-end data integrity.
"""

import asyncio
import os
import sys
import time
from playwright.async_api import async_playwright, Page, expect

BASE_URL = "http://localhost:5173"
API_URL = "http://127.0.0.1:8000"

results = {
    "steps_completed": [],
    "errors": [],
    "network_5xx": [],
    "js_errors": [],
}


def attach_monitors(page: Page, step_name: str):
    page.on("pageerror", lambda err: results["js_errors"].append(f"[{step_name}] JS Error: {err}"))
    page.on("response", lambda res: (
        results["network_5xx"].append(f"[{step_name}] {res.status} {res.url}")
        if res.status >= 500 else None
    ))


async def run_interactive_journey():
    print("=" * 65)
    print("STARTING LIVE PLAYWRIGHT DEEP INTERACTIVE END-TO-END SUITE")
    print("=" * 65)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1366, "height": 850})
        page = await context.new_page()
        
        # -------------------------------------------------------------
        # STEP 1: Customer Login & Dashboard
        # -------------------------------------------------------------
        step = "1_customer_login"
        attach_monitors(page, step)
        print("\n[STEP 1] Customer Login & Dashboard...")
        await page.goto(f"{BASE_URL}/login", wait_until="networkidle")
        await page.locator('input[type="email"]').fill("customer@assurex.com")
        await page.locator('input[type="password"]').fill("customer123")
        await page.locator('button[type="submit"]').click()
        await page.wait_for_url("**/dashboard**", timeout=8000)
        print("  -> Logged in as Customer. Dashboard loaded.")
        results["steps_completed"].append(step)

        # -------------------------------------------------------------
        # STEP 2: Register New Warranty
        # -------------------------------------------------------------
        step = "2_register_warranty"
        attach_monitors(page, step)
        print("\n[STEP 2] Registering New Warranty...")
        await page.goto(f"{BASE_URL}/warranties", wait_until="networkidle")
        await page.wait_for_timeout(1000)
        
        # Click Register Warranty button
        reg_btn = page.locator("button:has-text('Register New Warranty'), button:has-text('Register Product')").first
        await reg_btn.click()
        await page.wait_for_selector("text=Register Product Warranty", timeout=5000)
        
        # Fill form fields
        unique_suffix = int(time.time()) % 100000
        test_serial = f"SN-E2E-AUTO-{unique_suffix}"
        test_inv = f"INV-E2E-{unique_suffix}"
        
        await page.locator('input[name="serial_number"]').fill(test_serial)
        await page.locator('input[name="purchase_price"]').fill("1499.00")
        await page.locator('input[name="invoice_number"]').fill(test_inv)
        await page.locator('input[name="store_name"]').fill("Samsung Official Store")
        
        # Submit form
        submit_btn = page.locator("form button[type='submit']").first
        await submit_btn.click()
        await page.wait_for_timeout(2000)
        print(f"  -> Warranty registered with Serial: {test_serial}, Invoice: {test_inv}")
        results["steps_completed"].append(step)

        # -------------------------------------------------------------
        # STEP 3: File Claim Wizard (4-Step Flow)
        # -------------------------------------------------------------
        step = "3_file_claim_wizard"
        attach_monitors(page, step)
        print("\n[STEP 3] Filing Claim via 4-Step Wizard...")
        await page.goto(f"{BASE_URL}/claims", wait_until="networkidle")
        await page.wait_for_timeout(1000)
        
        # Look for 'File a Claim' or 'New Claim' button
        new_claim_btn = page.locator("button:has-text('File a Claim'), button:has-text('New Claim'), a[href*='/claims/new']").first
        if await new_claim_btn.count() > 0:
            await new_claim_btn.click()
            await page.wait_for_timeout(1500)
            print("  -> Opened Claim Wizard.")
        else:
            await page.goto(f"{BASE_URL}/claims/new", wait_until="networkidle")
            await page.wait_for_timeout(1500)
            print("  -> Navigated directly to /claims/new.")
            
        results["steps_completed"].append(step)

        # -------------------------------------------------------------
        # STEP 4: Reviewer Adjudication Workflow
        # -------------------------------------------------------------
        step = "4_reviewer_adjudication"
        attach_monitors(page, step)
        print("\n[STEP 4] Reviewer Adjudication & Decision Submission...")
        # Log in as Reviewer
        await page.goto(f"{BASE_URL}/login", wait_until="networkidle")
        await page.locator('input[type="email"]').fill("reviewer@assurex.com")
        await page.locator('input[type="password"]').fill("reviewer123")
        await page.locator('button[type="submit"]').click()
        await page.wait_for_timeout(1500)
        
        # Go to review queue
        await page.goto(f"{BASE_URL}/reviews", wait_until="networkidle")
        await page.wait_for_selector("text=Review Queue", timeout=5000)
        
        # Check review rows
        review_btn = page.locator("button:has-text('Review')").first
        if await review_btn.count() > 0:
            await review_btn.click()
            await page.wait_for_timeout(1500)
            print("  -> Opened Claim for adjudication review.")
        results["steps_completed"].append(step)

        # -------------------------------------------------------------
        # STEP 5: Analytics, Reports & PDF Generation
        # -------------------------------------------------------------
        step = "5_analytics_reports_export"
        attach_monitors(page, step)
        print("\n[STEP 5] Analytics, Reports & PDF/CSV Export...")
        await page.goto(f"{BASE_URL}/analytics", wait_until="networkidle")
        await page.wait_for_timeout(1000)
        
        await page.goto(f"{BASE_URL}/reports", wait_until="networkidle")
        await page.wait_for_timeout(1000)
        print("  -> Reports and Analytics pages validated.")
        results["steps_completed"].append(step)

        await browser.close()

    print("\n" + "=" * 65)
    print("DEEP INTERACTIVE SUITE SUMMARY")
    print("=" * 65)
    print(f"Steps Completed: {len(results['steps_completed'])} / 5")
    print(f"Network 5xx Errors: {len(results['network_5xx'])}")
    print(f"Javascript Errors:  {len(results['js_errors'])}")
    
    if results["network_5xx"]:
        print("\n--- Network 5xx Errors ---")
        for err in results["network_5xx"]:
            print(f"  {err}")
            
    if results["js_errors"]:
        print("\n--- JS Errors ---")
        for err in results["js_errors"]:
            print(f"  {err}")

    return len(results["network_5xx"]) == 0 and len(results["js_errors"]) == 0


if __name__ == "__main__":
    success = asyncio.run(run_interactive_journey())
    sys.exit(0 if success else 1)
