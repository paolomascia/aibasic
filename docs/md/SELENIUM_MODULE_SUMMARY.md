# Selenium Module - Complete Reference

## Overview

The **Selenium module** provides comprehensive web browser automation and testing capabilities with multi-browser support.

**Module Type**: `(selenium)` or `(browser)`
**Primary Use Cases**: Web scraping, automated testing, browser automation, form filling, E2E testing, UI testing

---

## Configuration

```ini
[selenium]
BROWSER = chrome
HEADLESS = false
WINDOW_SIZE = 1920x1080
IMPLICIT_WAIT = 10
PAGE_LOAD_TIMEOUT = 30
DOWNLOAD_DIR = ./downloads
CHROME_DRIVER_PATH =
FIREFOX_DRIVER_PATH =
EDGE_DRIVER_PATH =
```

---

## Basic Operations

```basic
REM Navigate and interact
10 (selenium) navigate to "https://example.com"
20 (selenium) click element "#login-button" by "css"
30 (selenium) type "user@example.com" into "#email" by "css"
40 (selenium) type "password123" into "#password" by "css"

REM Wait for elements
50 (selenium) wait for element ".dashboard" to be "visible" with timeout 10

REM Extract data
60 LET title = (selenium) get text from "h1" by "css"
70 LET href = (selenium) get attribute "href" from "a.link" by "css"

REM Screenshots
80 (selenium) screenshot "page.png"

REM Form handling
90 (selenium) select "USA" from "#country" by "css" using "text"
100 (selenium) upload file "document.pdf" to "#file-input" by "css"

REM Cleanup
110 (selenium) quit
```

---

## Advanced Features

### Element Location Strategies

```basic
REM CSS Selector (recommended)
10 (selenium) click element "#submit-button" by "css"

REM XPath
20 (selenium) click element "//button[@id='submit']" by "xpath"

REM ID
30 (selenium) click element "submit-button" by "id"

REM Class Name
40 (selenium) click element "btn-primary" by "class"

REM Link Text
50 (selenium) click element "Click here" by "link_text"

REM Partial Link Text
60 (selenium) click element "Click" by "partial_link_text"
```

### Wait Strategies

```basic
REM Wait for element to be visible
10 (selenium) wait for element "#result" to be "visible" with timeout 10

REM Wait for element to be clickable
20 (selenium) wait for element "#button" to be "clickable" with timeout 10

REM Wait for element to be present (in DOM)
30 (selenium) wait for element "#data" to be "present" with timeout 10

REM Click with explicit wait
40 (selenium) click element "#dynamic-button" by "css" with wait 5
```

### JavaScript Execution

```basic
REM Execute JavaScript
10 (selenium) execute script "alert('Hello!');"

REM Get return value
20 LET height = (selenium) execute script "return document.body.scrollHeight;"

REM Scroll to bottom
30 (selenium) execute script "window.scrollTo(0, document.body.scrollHeight);"

REM Change element style
40 (selenium) execute script "document.querySelector('#header').style.backgroundColor = 'red';"

REM Access localStorage
50 LET token = (selenium) execute script "return localStorage.getItem('token');"
```

### Window and Frame Management

```basic
REM Get all windows
10 LET windows = (selenium) get window handles

REM Switch to window by index
20 (selenium) switch to window 1

REM Close current window
30 (selenium) close window

REM Switch back to main window
40 (selenium) switch to window 0

REM Switch to iframe
50 (selenium) switch to frame 0

REM Switch back to main content
60 (selenium) switch to default content
```

### Cookie Management

```basic
REM Add cookie
10 (selenium) add cookie "user_id" with value "12345"

REM Add cookie with options
20 (selenium) add cookie "session" with value "abc123" and domain "example.com" and path "/"

REM Get specific cookie
30 LET user_cookie = (selenium) get cookie "user_id"

REM Get all cookies
40 LET all_cookies = (selenium) get all cookies

REM Delete cookie
50 (selenium) delete cookie "user_id"

REM Delete all cookies
60 (selenium) delete all cookies
```

### Alert Handling

```basic
REM Get alert text
10 LET alert_text = (selenium) get alert text

REM Accept alert
20 (selenium) accept alert

REM Dismiss alert
30 (selenium) dismiss alert

REM Send text to prompt
40 (selenium) send text "John Doe" to alert
50 (selenium) accept alert
```

### Mouse Actions

```basic
REM Hover over element
10 (selenium) hover over element "#menu-item" by "css"

REM Drag and drop
20 (selenium) drag element "#draggable" and drop to "#droppable" by "css"

REM Scroll to element
30 (selenium) scroll to element "#footer" by "css"
```

### Window Management

```basic
REM Set window size
10 (selenium) set window size 1920 1080

REM Maximize window
20 (selenium) maximize window

REM Minimize window
30 (selenium) minimize window
```

---

## Common Use Cases

### Login Automation

```basic
10 PRINT "=== Login Automation ==="
20 (selenium) navigate to "https://example.com/login"
30 (selenium) type "user@example.com" into "#username" by "css"
40 (selenium) type "password123" into "#password" by "css"
50 (selenium) click element "#login-button" by "css"
60 (selenium) wait for element ".dashboard" to be "visible" with timeout 10
70 PRINT "Login successful!"
```

### Form Filling

```basic
10 PRINT "=== Form Automation ==="
20 (selenium) navigate to "https://example.com/contact"
30 (selenium) type "John Doe" into "#name" by "css"
40 (selenium) type "john@example.com" into "#email" by "css"
50 (selenium) type "Hello, this is my message" into "#message" by "css"
60 (selenium) select "USA" from "#country" by "css" using "text"
70 (selenium) click element "#agree-terms" by "css"
80 (selenium) click element "#submit-button" by "css"
90 PRINT "Form submitted!"
```

### Web Scraping

```basic
10 PRINT "=== Web Scraping ==="
20 (selenium) navigate to "https://example.com/products"
30 (selenium) wait for element ".product" to be "visible" with timeout 10

40 REM Extract product data using JavaScript
50 LET products = (selenium) execute script "return Array.from(document.querySelectorAll('.product')).map(p => ({title: p.querySelector('.title').innerText, price: p.querySelector('.price').innerText}));"

60 PRINT "Extracted products: " + products

70 REM Save to file
80 OPEN "products.json" FOR OUTPUT AS #1
90 PRINT #1, products
100 CLOSE #1
110 PRINT "Data saved!"
```

### Screenshot Testing

```basic
10 PRINT "=== Screenshot Testing ==="
20 (selenium) navigate to "https://example.com"

30 REM Desktop view
40 (selenium) set window size 1920 1080
50 (selenium) screenshot "desktop.png"

60 REM Tablet view
70 (selenium) set window size 768 1024
80 (selenium) screenshot "tablet.png"

90 REM Mobile view
100 (selenium) set window size 375 667
110 (selenium) screenshot "mobile.png"

120 PRINT "Screenshots saved!"
```

### E-commerce Testing

```basic
10 PRINT "=== E-commerce Test ==="
20 (selenium) navigate to "https://example.com/shop"

30 REM Search product
40 (selenium) type "laptop" into "#search" by "css"
50 (selenium) click element "#search-button" by "css"
60 (selenium) wait for element ".search-results" to be "visible" with timeout 10

70 REM Click first product
80 (selenium) click element ".product-item:first-child" by "css"
90 (selenium) wait for element ".product-details" to be "visible" with timeout 10

100 REM Get product info
110 LET title = (selenium) get text from ".product-title" by "css"
120 LET price = (selenium) get text from ".product-price" by "css"
130 PRINT "Product: " + title + " - Price: " + price

140 REM Add to cart
150 (selenium) select "2" from "#quantity" by "css" using "value"
160 (selenium) click element "#add-to-cart" by "css"
170 (selenium) wait for element ".cart-count" to be "visible" with timeout 5

180 LET cart_count = (selenium) get text from ".cart-count" by "css"
190 PRINT "Cart items: " + cart_count
```

### Form Validation Testing

```basic
10 PRINT "=== Form Validation Test ==="
20 (selenium) navigate to "https://example.com/register"

30 REM Test empty form
40 (selenium) click element "#submit" by "css"
50 LET has_error = (selenium) is element ".error-message" displayed by "css"
60 IF has_error THEN
70   LET error = (selenium) get text from ".error-message" by "css"
80   PRINT "Validation error: " + error
90 END IF

100 REM Test invalid email
110 (selenium) type "invalid-email" into "#email" by "css"
120 (selenium) click element "#submit" by "css"
130 LET email_error = (selenium) get text from "#email-error" by "css"
140 PRINT "Email error: " + email_error

150 REM Test valid form
160 (selenium) type "john@example.com" into "#email" by "css" with clear true
170 (selenium) type "password123" into "#password" by "css" with clear true
180 (selenium) type "password123" into "#confirm-password" by "css" with clear true
190 (selenium) click element "#submit" by "css"
200 (selenium) wait for element ".success" to be "visible" with timeout 5
210 PRINT "Form validation passed!"
```

### Dynamic Content Handling

```basic
10 PRINT "=== Dynamic Content ==="
20 (selenium) navigate to "https://example.com/ajax-demo"

30 REM Click to load data
40 (selenium) click element "#load-data" by "css"

50 REM Wait for loading to complete
60 LET i = 0
70 WHILE i < 20
80   LET still_loading = (selenium) is element ".loading" displayed by "css"
90   IF NOT still_loading THEN
100     GOTO 150
110   END IF
120   SLEEP 0.5
130   LET i = i + 1
140 WEND

150 LET data = (selenium) get text from "#data-container" by "css"
160 PRINT "Loaded data: " + data
```

### Multi-Window Testing

```basic
10 PRINT "=== Multi-Window Test ==="
20 (selenium) navigate to "https://example.com"

30 REM Get main window
40 LET windows = (selenium) get window handles
50 LET main_window = windows[0]

60 REM Open new window
70 (selenium) click element "#open-window" by "css"
80 SLEEP 1

90 REM Switch to new window
100 LET all_windows = (selenium) get window handles
110 (selenium) switch to window 1

120 REM Get title of new window
130 LET new_title = (selenium) get title
140 PRINT "New window: " + new_title

150 REM Close and switch back
160 (selenium) close window
170 (selenium) switch to window 0
180 PRINT "Back to main window"
```

---

## Best Practices

### Use Explicit Waits
Always use explicit waits for dynamic content rather than fixed sleeps:
```basic
REM Good - explicit wait
10 (selenium) wait for element "#result" to be "visible" with timeout 10

REM Bad - fixed sleep
20 SLEEP 5
```

### Prefer CSS Selectors
CSS selectors are faster and more readable than XPath:
```basic
REM Good - CSS selector
10 (selenium) click element "#submit-button" by "css"
20 (selenium) click element ".btn-primary" by "css"

REM Acceptable - XPath (when necessary)
30 (selenium) click element "//button[@id='submit']" by "xpath"
```

### Clean Up Resources
Always quit the browser to prevent memory leaks:
```basic
10 ON ERROR GOTO 900
20 (selenium) navigate to "https://example.com"
30 REM ... your automation ...
40 (selenium) quit
50 END

900 REM Error handler
910 PRINT "Error: " + _last_error
920 (selenium) quit
930 END
```

### Use Headless Mode in CI/CD
For automated testing pipelines, use headless mode:
```ini
[selenium]
HEADLESS = true
```

### Take Screenshots on Failures
Capture screenshots for debugging:
```basic
10 ON ERROR GOTO 900
20 (selenium) navigate to "https://example.com"
30 REM ... test steps ...
40 (selenium) quit
50 END

900 REM Error handler
910 PRINT "Test failed: " + _last_error
920 (selenium) screenshot "error_" + STR(_last_error_line) + ".png"
930 (selenium) quit
940 END
```

---

## Performance Tips

1. **Disable Images in Headless Mode**: Add Chrome options for faster page loads
2. **Reuse Browser Instance**: Don't quit/restart browser for every test
3. **Use JavaScript for Direct DOM Access**: Faster than WebDriver commands
4. **Set Appropriate Timeouts**: Balance speed and reliability
5. **Use Page Object Model**: Organize tests for maintainability

---

## Security Considerations

1. **Don't Hardcode Credentials**: Use environment variables or vaults
2. **Respect robots.txt**: Check website terms of service before scraping
3. **Rate Limiting**: Add delays between requests to avoid overwhelming servers
4. **HTTPS Only**: Always use secure connections for sensitive operations

---

## Troubleshooting

### Element Not Found
```basic
REM Check if element exists
10 LET exists = (selenium) is element "#button" displayed by "css"
20 IF NOT exists THEN
30   PRINT "Element not found!"
40   (selenium) screenshot "debug.png"
50 END IF
```

### Stale Element Reference
```basic
REM Re-locate element if it becomes stale
10 ON ERROR GOTO 100
20 (selenium) click element "#button" by "css"
30 GOTO 200

100 REM Re-locate and retry
110 (selenium) wait for element "#button" to be "visible" with timeout 5
120 (selenium) click element "#button" by "css"
130 GOTO 200

200 REM Continue...
```

### Timeout Issues
```basic
REM Increase timeout for slow-loading pages
10 (selenium) wait for element "#result" to be "visible" with timeout 30
```

---

## Browser Support

- **Chrome**: Recommended (fastest, best headless support)
- **Firefox**: Full support
- **Edge**: Full support (Chromium-based)
- **Safari**: macOS only, no headless mode

---

## Module Information

- **Module Name**: SeleniumModule
- **Task Type**: `(selenium)`, `(browser)`
- **Dependencies**: `selenium>=4.15.0`, `webdriver-manager>=4.0.0`
- **Supported Browsers**: Chrome, Firefox, Edge, Safari (macOS)
- **WebDriver Manager**: Automatic driver installation and management
