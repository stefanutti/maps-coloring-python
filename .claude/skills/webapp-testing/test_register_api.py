from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Capture network requests and responses
    captured_requests = []

    def handle_route(route):
        request = route.request
        if '/api/auth/register' in request.url:
            captured_requests.append({
                'url': request.url,
                'method': request.method,
                'post_data': request.post_data,
                'headers': dict(request.headers)
            })
        route.continue_()

    page.route('**/*', handle_route)

    # Navigate to login
    page.goto('http://localhost:3000/login')
    page.wait_for_load_state('networkidle')
    print("✓ Navigated to login page")

    # Click Registrati
    page.click('text=Registrati')
    print("✓ Clicked Registrati")

    # Wait for form
    page.wait_for_selector('text=Inserisci la tua email per ricevere un link di registrazione.')
    print("✓ Registration form appeared")

    # Get all email inputs and find the one in the registration section
    # The registration form is in the footer section with the text "Inserisci la tua email per ricevere un link di registrazione."
    register_section = page.locator('text=Inserisci la tua email per ricevere un link di registrazione.').locator('..')
    email_input = register_section.locator('input[type="email"]')

    email_input.fill('test@frontiere.io')
    print("✓ Filled email")

    # Wait a moment for form to update
    page.wait_for_timeout(500)

    # Take screenshot before submit
    page.screenshot(path='/tmp/before_submit.png', full_page=True)
    print("✓ Screenshot taken before submit: /tmp/before_submit.png")

    # Find the submit button within the registration section
    submit_button = page.locator('button[type="submit"]:has-text("Registrati")').last
    print(f"Submit button visible: {submit_button.is_visible()}")
    print(f"Submit button disabled: {submit_button.is_disabled()}")

    # Click submit button
    submit_button.click()
    print("✓ Clicked submit button")

    # Wait for response
    page.wait_for_timeout(3000)

    # Take screenshot after submit
    page.screenshot(path='/tmp/after_submit.png', full_page=True)
    print("✓ Screenshot taken after submit: /tmp/after_submit.png")

    # Check for confirmation message
    page.wait_for_timeout(500)
    confirmation_locator = page.locator('text=Se l\'email è autorizzata riceverai un link per completare la registrazione.')
    print(f"Confirmation message visible: {confirmation_locator.is_visible()}")

    # Print page content
    content = page.content()
    if 'Se l\'email è autorizzata' in content:
        print("✓ Confirmation message text found in HTML")
    else:
        print("✗ Confirmation message text NOT in HTML")

    # Print captured requests
    print("\n=== Captured API Requests ===")
    if captured_requests:
        for req in captured_requests:
            print(f"\nURL: {req['url']}")
            print(f"Method: {req['method']}")
            print(f"Post Data: {req['post_data']}")
    else:
        print("No /api/auth/register requests captured")

    # Check browser console logs
    print("\n=== Page State ===")
    print(f"Current URL: {page.url}")

    browser.close()
