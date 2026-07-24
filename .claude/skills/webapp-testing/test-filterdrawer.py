#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
import sys

def test_filter_drawer():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Navigate to the roles page
            page.goto('http://localhost:3000/roles-permissions')
            page.wait_for_load_state('networkidle')

            # Take initial screenshot
            page.screenshot(path='/tmp/1-initial.png', full_page=True)
            print("✓ Screenshot 1: Initial page")

            # Check if "Filtri" button exists
            filtri_button = page.locator('button:has-text("Filtri")')
            if filtri_button.count() == 0:
                print("✗ 'Filtri' button not found")
                return False

            # Click the Filtri button to open the drawer
            filtri_button.first.click()
            page.wait_for_load_state('networkidle')

            # Take screenshot of open drawer
            page.screenshot(path='/tmp/2-drawer-open.png', full_page=True)
            print("✓ Screenshot 2: Drawer open")

            # Check if the drawer header "Filtri" is visible
            header = page.locator('h2:has-text("Filtri")')
            if header.count() == 0:
                print("✗ Drawer header 'Filtri' not found")
                return False
            print("✓ Drawer header visible")

            # Check if backdrop is visible
            backdrop = page.locator('div.fixed.inset-0.z-40')
            if backdrop.count() == 0:
                print("✗ Backdrop not found")
                return False
            print("✓ Backdrop visible")

            # Check if close button (X) exists
            close_btn = page.locator('button[aria-label="Chiudi filtri"]')
            if close_btn.count() == 0:
                print("✗ Close button (X) not found")
                return False
            print("✓ Close button (X) visible")

            # Check if Reset and Applica buttons exist
            reset_btn = page.locator('button:has-text("Reset")')
            apply_btn = page.locator('button:has-text("Applica")')
            if reset_btn.count() == 0:
                print("✗ Reset button not found")
                return False
            if apply_btn.count() == 0:
                print("✗ Applica button not found")
                return False
            print("✓ Reset and Applica buttons visible")

            # Test clicking Applica button to close the drawer
            apply_btn.first.click()
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(300)  # Wait for animation

            # Check if drawer is closed
            header_after = page.locator('h2:has-text("Filtri")')
            if header_after.count() != 0:
                print("✗ Drawer did not close after clicking Applica")
                return False
            print("✓ Drawer closes when Applica is clicked")

            # Take screenshot after closing
            page.screenshot(path='/tmp/3-drawer-closed.png', full_page=True)
            print("✓ Screenshot 3: Drawer closed")

            # Reopen the drawer for further tests
            filtri_button.first.click()
            page.wait_for_load_state('networkidle')

            # Test clicking the X button to close
            close_btn = page.locator('button[aria-label="Chiudi filtri"]')
            close_btn.first.click()
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(300)  # Wait for animation

            header_after_x = page.locator('h2:has-text("Filtri")')
            if header_after_x.count() != 0:
                print("✗ Drawer did not close after clicking X button")
                return False
            print("✓ Drawer closes when X button is clicked")

            # Reopen and test backdrop click
            filtri_button.first.click()
            page.wait_for_load_state('networkidle')

            # Click the backdrop to close
            backdrop = page.locator('div.fixed.inset-0.z-40').first
            backdrop.click(force=True)
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(300)  # Wait for animation

            header_after_backdrop = page.locator('h2:has-text("Filtri")')
            if header_after_backdrop.count() != 0:
                print("✗ Drawer did not close after clicking backdrop")
                return False
            print("✓ Drawer closes when backdrop is clicked")

            print("\n✓ All tests passed!")
            return True

        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            browser.close()

if __name__ == '__main__':
    success = test_filter_drawer()
    sys.exit(0 if success else 1)
