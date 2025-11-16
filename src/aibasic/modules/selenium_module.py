"""
Selenium Module for AIbasic
Provides comprehensive web browser automation and testing capabilities.

Module Type: (selenium) or (browser)
Primary Use Cases: Web scraping, automated testing, browser automation, form filling

Author: AIbasic Development Team
Version: 1.0.0
"""

import os
import time
import threading
from typing import Dict, Any, List, Optional, Union
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
    StaleElementReferenceException
)


class SeleniumModule:
    """
    Selenium module for web browser automation and testing.

    Features:
    - Multi-browser support (Chrome, Firefox, Edge, Safari)
    - Headless mode support
    - Element location strategies (ID, CSS, XPath, etc.)
    - Wait strategies (explicit, implicit, fluent)
    - Screenshot and page source capture
    - Cookie management
    - JavaScript execution
    - File uploads and downloads
    - Mouse and keyboard actions
    - Window and frame management
    - Alert handling

    Configuration (aibasic.conf):
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
    """

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls):
        """Singleton pattern to ensure only one instance exists."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the Selenium module."""
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    self.driver = None
                    self.wait = None
                    self.actions = None

                    # Configuration
                    self.browser = os.getenv('SELENIUM_BROWSER', 'chrome').lower()
                    self.headless = os.getenv('SELENIUM_HEADLESS', 'false').lower() == 'true'
                    self.window_size = os.getenv('SELENIUM_WINDOW_SIZE', '1920x1080')
                    self.implicit_wait = int(os.getenv('SELENIUM_IMPLICIT_WAIT', '10'))
                    self.page_load_timeout = int(os.getenv('SELENIUM_PAGE_LOAD_TIMEOUT', '30'))
                    self.download_dir = os.getenv('SELENIUM_DOWNLOAD_DIR', './downloads')

                    # Driver paths
                    self.chrome_driver_path = os.getenv('SELENIUM_CHROME_DRIVER_PATH', '')
                    self.firefox_driver_path = os.getenv('SELENIUM_FIREFOX_DRIVER_PATH', '')
                    self.edge_driver_path = os.getenv('SELENIUM_EDGE_DRIVER_PATH', '')

                    self._initialized = True

    def _ensure_driver(self):
        """Ensure driver is initialized (lazy loading)."""
        if self.driver is None:
            self._initialize_driver()

    def _initialize_driver(self):
        """Initialize the web driver based on configuration."""
        if self.browser == 'chrome':
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument('--headless=new')
            options.add_argument(f'--window-size={self.window_size}')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

            # Set download directory
            prefs = {
                'download.default_directory': os.path.abspath(self.download_dir),
                'download.prompt_for_download': False,
                'download.directory_upgrade': True,
                'safebrowsing.enabled': True
            }
            options.add_experimental_option('prefs', prefs)

            if self.chrome_driver_path:
                from selenium.webdriver.chrome.service import Service
                service = Service(executable_path=self.chrome_driver_path)
                self.driver = webdriver.Chrome(service=service, options=options)
            else:
                self.driver = webdriver.Chrome(options=options)

        elif self.browser == 'firefox':
            options = webdriver.FirefoxOptions()
            if self.headless:
                options.add_argument('--headless')

            # Set download directory
            options.set_preference('browser.download.folderList', 2)
            options.set_preference('browser.download.dir', os.path.abspath(self.download_dir))
            options.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/pdf,application/zip')

            if self.firefox_driver_path:
                from selenium.webdriver.firefox.service import Service
                service = Service(executable_path=self.firefox_driver_path)
                self.driver = webdriver.Firefox(service=service, options=options)
            else:
                self.driver = webdriver.Firefox(options=options)

        elif self.browser == 'edge':
            options = webdriver.EdgeOptions()
            if self.headless:
                options.add_argument('--headless=new')
            options.add_argument(f'--window-size={self.window_size}')

            if self.edge_driver_path:
                from selenium.webdriver.edge.service import Service
                service = Service(executable_path=self.edge_driver_path)
                self.driver = webdriver.Edge(service=service, options=options)
            else:
                self.driver = webdriver.Edge(options=options)

        elif self.browser == 'safari':
            self.driver = webdriver.Safari()

        else:
            raise ValueError(f"Unsupported browser: {self.browser}")

        # Set timeouts
        self.driver.implicitly_wait(self.implicit_wait)
        self.driver.set_page_load_timeout(self.page_load_timeout)

        # Initialize wait and actions
        self.wait = WebDriverWait(self.driver, self.implicit_wait)
        self.actions = ActionChains(self.driver)

    def navigate(self, url: str) -> bool:
        """
        Navigate to a URL.

        Args:
            url: The URL to navigate to

        Returns:
            True if successful
        """
        self._ensure_driver()
        self.driver.get(url)
        return True

    def click(self, locator: str, by: str = 'css', wait: Optional[int] = None) -> bool:
        """
        Click an element.

        Args:
            locator: The locator string
            by: Locator strategy (css, xpath, id, name, class, tag, link_text, partial_link_text)
            wait: Optional wait time in seconds

        Returns:
            True if successful
        """
        self._ensure_driver()
        element = self._find_element(locator, by, wait)
        element.click()
        return True

    def type_text(self, locator: str, text: str, by: str = 'css',
                  clear: bool = True, wait: Optional[int] = None) -> bool:
        """
        Type text into an element.

        Args:
            locator: The locator string
            text: The text to type
            by: Locator strategy
            clear: Whether to clear existing text first
            wait: Optional wait time in seconds

        Returns:
            True if successful
        """
        self._ensure_driver()
        element = self._find_element(locator, by, wait)
        if clear:
            element.clear()
        element.send_keys(text)
        return True

    def get_text(self, locator: str, by: str = 'css', wait: Optional[int] = None) -> str:
        """
        Get text from an element.

        Args:
            locator: The locator string
            by: Locator strategy
            wait: Optional wait time in seconds

        Returns:
            The element text
        """
        self._ensure_driver()
        element = self._find_element(locator, by, wait)
        return element.text

    def get_attribute(self, locator: str, attribute: str, by: str = 'css',
                     wait: Optional[int] = None) -> Optional[str]:
        """
        Get an attribute value from an element.

        Args:
            locator: The locator string
            attribute: The attribute name
            by: Locator strategy
            wait: Optional wait time in seconds

        Returns:
            The attribute value
        """
        self._ensure_driver()
        element = self._find_element(locator, by, wait)
        return element.get_attribute(attribute)

    def is_displayed(self, locator: str, by: str = 'css', wait: Optional[int] = None) -> bool:
        """
        Check if an element is displayed.

        Args:
            locator: The locator string
            by: Locator strategy
            wait: Optional wait time in seconds

        Returns:
            True if displayed
        """
        self._ensure_driver()
        try:
            element = self._find_element(locator, by, wait)
            return element.is_displayed()
        except (NoSuchElementException, TimeoutException):
            return False

    def is_enabled(self, locator: str, by: str = 'css', wait: Optional[int] = None) -> bool:
        """
        Check if an element is enabled.

        Args:
            locator: The locator string
            by: Locator strategy
            wait: Optional wait time in seconds

        Returns:
            True if enabled
        """
        self._ensure_driver()
        element = self._find_element(locator, by, wait)
        return element.is_enabled()

    def wait_for_element(self, locator: str, by: str = 'css',
                        timeout: int = 10, condition: str = 'visible') -> bool:
        """
        Wait for an element to meet a condition.

        Args:
            locator: The locator string
            by: Locator strategy
            timeout: Wait timeout in seconds
            condition: Condition to wait for (visible, clickable, present)

        Returns:
            True if condition met
        """
        self._ensure_driver()
        wait = WebDriverWait(self.driver, timeout)
        by_type = self._get_by_type(by)

        try:
            if condition == 'visible':
                wait.until(EC.visibility_of_element_located((by_type, locator)))
            elif condition == 'clickable':
                wait.until(EC.element_to_be_clickable((by_type, locator)))
            elif condition == 'present':
                wait.until(EC.presence_of_element_located((by_type, locator)))
            else:
                raise ValueError(f"Unknown condition: {condition}")
            return True
        except TimeoutException:
            return False

    def select_dropdown(self, locator: str, value: str, by: str = 'css',
                       select_by: str = 'value', wait: Optional[int] = None) -> bool:
        """
        Select an option from a dropdown.

        Args:
            locator: The locator string
            value: The value to select
            by: Locator strategy
            select_by: Selection method (value, text, index)
            wait: Optional wait time in seconds

        Returns:
            True if successful
        """
        self._ensure_driver()
        element = self._find_element(locator, by, wait)
        select = Select(element)

        if select_by == 'value':
            select.select_by_value(value)
        elif select_by == 'text':
            select.select_by_visible_text(value)
        elif select_by == 'index':
            select.select_by_index(int(value))
        else:
            raise ValueError(f"Unknown select_by method: {select_by}")

        return True

    def execute_script(self, script: str, *args) -> Any:
        """
        Execute JavaScript code.

        Args:
            script: The JavaScript code to execute
            *args: Arguments to pass to the script

        Returns:
            The script return value
        """
        self._ensure_driver()
        return self.driver.execute_script(script, *args)

    def take_screenshot(self, filename: str) -> bool:
        """
        Take a screenshot.

        Args:
            filename: The filename to save the screenshot

        Returns:
            True if successful
        """
        self._ensure_driver()
        return self.driver.save_screenshot(filename)

    def get_page_source(self) -> str:
        """
        Get the page source.

        Returns:
            The page source HTML
        """
        self._ensure_driver()
        return self.driver.page_source

    def get_current_url(self) -> str:
        """
        Get the current URL.

        Returns:
            The current URL
        """
        self._ensure_driver()
        return self.driver.current_url

    def get_title(self) -> str:
        """
        Get the page title.

        Returns:
            The page title
        """
        self._ensure_driver()
        return self.driver.title

    def back(self) -> bool:
        """Navigate back."""
        self._ensure_driver()
        self.driver.back()
        return True

    def forward(self) -> bool:
        """Navigate forward."""
        self._ensure_driver()
        self.driver.forward()
        return True

    def refresh(self) -> bool:
        """Refresh the page."""
        self._ensure_driver()
        self.driver.refresh()
        return True

    def switch_to_frame(self, frame: Union[str, int]) -> bool:
        """
        Switch to a frame.

        Args:
            frame: Frame name, ID, or index

        Returns:
            True if successful
        """
        self._ensure_driver()
        if isinstance(frame, int):
            self.driver.switch_to.frame(frame)
        else:
            self.driver.switch_to.frame(frame)
        return True

    def switch_to_default_content(self) -> bool:
        """Switch back to the main content."""
        self._ensure_driver()
        self.driver.switch_to.default_content()
        return True

    def switch_to_window(self, window: Union[str, int]) -> bool:
        """
        Switch to a window.

        Args:
            window: Window handle or index

        Returns:
            True if successful
        """
        self._ensure_driver()
        if isinstance(window, int):
            handles = self.driver.window_handles
            self.driver.switch_to.window(handles[window])
        else:
            self.driver.switch_to.window(window)
        return True

    def get_window_handles(self) -> List[str]:
        """
        Get all window handles.

        Returns:
            List of window handles
        """
        self._ensure_driver()
        return self.driver.window_handles

    def close_window(self) -> bool:
        """Close the current window."""
        self._ensure_driver()
        self.driver.close()
        return True

    def accept_alert(self) -> bool:
        """Accept an alert dialog."""
        self._ensure_driver()
        alert = self.driver.switch_to.alert
        alert.accept()
        return True

    def dismiss_alert(self) -> bool:
        """Dismiss an alert dialog."""
        self._ensure_driver()
        alert = self.driver.switch_to.alert
        alert.dismiss()
        return True

    def get_alert_text(self) -> str:
        """
        Get alert text.

        Returns:
            The alert text
        """
        self._ensure_driver()
        alert = self.driver.switch_to.alert
        return alert.text

    def send_alert_text(self, text: str) -> bool:
        """
        Send text to an alert prompt.

        Args:
            text: The text to send

        Returns:
            True if successful
        """
        self._ensure_driver()
        alert = self.driver.switch_to.alert
        alert.send_keys(text)
        return True

    def add_cookie(self, name: str, value: str, **kwargs) -> bool:
        """
        Add a cookie.

        Args:
            name: Cookie name
            value: Cookie value
            **kwargs: Additional cookie attributes (domain, path, expiry, etc.)

        Returns:
            True if successful
        """
        self._ensure_driver()
        cookie = {'name': name, 'value': value}
        cookie.update(kwargs)
        self.driver.add_cookie(cookie)
        return True

    def get_cookie(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a cookie by name.

        Args:
            name: Cookie name

        Returns:
            Cookie dictionary or None
        """
        self._ensure_driver()
        return self.driver.get_cookie(name)

    def get_all_cookies(self) -> List[Dict[str, Any]]:
        """
        Get all cookies.

        Returns:
            List of cookie dictionaries
        """
        self._ensure_driver()
        return self.driver.get_cookies()

    def delete_cookie(self, name: str) -> bool:
        """
        Delete a cookie.

        Args:
            name: Cookie name

        Returns:
            True if successful
        """
        self._ensure_driver()
        self.driver.delete_cookie(name)
        return True

    def delete_all_cookies(self) -> bool:
        """Delete all cookies."""
        self._ensure_driver()
        self.driver.delete_all_cookies()
        return True

    def hover(self, locator: str, by: str = 'css', wait: Optional[int] = None) -> bool:
        """
        Hover over an element.

        Args:
            locator: The locator string
            by: Locator strategy
            wait: Optional wait time in seconds

        Returns:
            True if successful
        """
        self._ensure_driver()
        element = self._find_element(locator, by, wait)
        self.actions.move_to_element(element).perform()
        return True

    def drag_and_drop(self, source_locator: str, target_locator: str,
                     by: str = 'css', wait: Optional[int] = None) -> bool:
        """
        Drag and drop an element.

        Args:
            source_locator: Source element locator
            target_locator: Target element locator
            by: Locator strategy
            wait: Optional wait time in seconds

        Returns:
            True if successful
        """
        self._ensure_driver()
        source = self._find_element(source_locator, by, wait)
        target = self._find_element(target_locator, by, wait)
        self.actions.drag_and_drop(source, target).perform()
        return True

    def scroll_to_element(self, locator: str, by: str = 'css', wait: Optional[int] = None) -> bool:
        """
        Scroll to an element.

        Args:
            locator: The locator string
            by: Locator strategy
            wait: Optional wait time in seconds

        Returns:
            True if successful
        """
        self._ensure_driver()
        element = self._find_element(locator, by, wait)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        return True

    def upload_file(self, locator: str, file_path: str, by: str = 'css',
                   wait: Optional[int] = None) -> bool:
        """
        Upload a file.

        Args:
            locator: File input locator
            file_path: Path to the file to upload
            by: Locator strategy
            wait: Optional wait time in seconds

        Returns:
            True if successful
        """
        self._ensure_driver()
        element = self._find_element(locator, by, wait)
        element.send_keys(os.path.abspath(file_path))
        return True

    def find_elements(self, locator: str, by: str = 'css') -> int:
        """
        Count elements matching a locator.

        Args:
            locator: The locator string
            by: Locator strategy

        Returns:
            Number of matching elements
        """
        self._ensure_driver()
        by_type = self._get_by_type(by)
        elements = self.driver.find_elements(by_type, locator)
        return len(elements)

    def set_window_size(self, width: int, height: int) -> bool:
        """
        Set window size.

        Args:
            width: Window width
            height: Window height

        Returns:
            True if successful
        """
        self._ensure_driver()
        self.driver.set_window_size(width, height)
        return True

    def maximize_window(self) -> bool:
        """Maximize the browser window."""
        self._ensure_driver()
        self.driver.maximize_window()
        return True

    def minimize_window(self) -> bool:
        """Minimize the browser window."""
        self._ensure_driver()
        self.driver.minimize_window()
        return True

    def quit(self) -> bool:
        """Quit the browser and close all windows."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.wait = None
            self.actions = None
        return True

    def _find_element(self, locator: str, by: str = 'css', wait: Optional[int] = None):
        """
        Find an element using the specified locator strategy.

        Args:
            locator: The locator string
            by: Locator strategy
            wait: Optional wait time in seconds

        Returns:
            WebElement
        """
        by_type = self._get_by_type(by)

        if wait:
            wait_obj = WebDriverWait(self.driver, wait)
            return wait_obj.until(EC.presence_of_element_located((by_type, locator)))
        else:
            return self.driver.find_element(by_type, locator)

    def _get_by_type(self, by: str):
        """Convert string to By type."""
        by_map = {
            'css': By.CSS_SELECTOR,
            'xpath': By.XPATH,
            'id': By.ID,
            'name': By.NAME,
            'class': By.CLASS_NAME,
            'tag': By.TAG_NAME,
            'link_text': By.LINK_TEXT,
            'partial_link_text': By.PARTIAL_LINK_TEXT
        }
        return by_map.get(by.lower(), By.CSS_SELECTOR)

    def __del__(self):
        """Cleanup when object is destroyed."""
        self.quit()


def execute(task_hint: str, params: Dict[str, Any]) -> Any:
    """
    Execute Selenium module tasks.

    Args:
        task_hint: The task type hint (selenium, browser)
        params: Task parameters

    Returns:
        Task result
    """
    module = SeleniumModule()

    # Parse the command
    action = params.get('action', '').lower()

    # Navigation
    if action in ['navigate', 'goto', 'open']:
        return module.navigate(params['url'])

    # Element interactions
    elif action == 'click':
        return module.click(
            params['locator'],
            params.get('by', 'css'),
            params.get('wait')
        )

    elif action in ['type', 'input', 'send_keys']:
        return module.type_text(
            params['locator'],
            params['text'],
            params.get('by', 'css'),
            params.get('clear', True),
            params.get('wait')
        )

    elif action in ['get_text', 'text']:
        return module.get_text(
            params['locator'],
            params.get('by', 'css'),
            params.get('wait')
        )

    elif action in ['get_attribute', 'attribute']:
        return module.get_attribute(
            params['locator'],
            params['attribute'],
            params.get('by', 'css'),
            params.get('wait')
        )

    # Waits
    elif action in ['wait', 'wait_for']:
        return module.wait_for_element(
            params['locator'],
            params.get('by', 'css'),
            params.get('timeout', 10),
            params.get('condition', 'visible')
        )

    # Dropdowns
    elif action in ['select', 'dropdown']:
        return module.select_dropdown(
            params['locator'],
            params['value'],
            params.get('by', 'css'),
            params.get('select_by', 'value'),
            params.get('wait')
        )

    # JavaScript
    elif action in ['execute_script', 'js']:
        return module.execute_script(params['script'], *params.get('args', []))

    # Screenshots
    elif action in ['screenshot', 'capture']:
        return module.take_screenshot(params['filename'])

    # Page info
    elif action in ['get_url', 'current_url']:
        return module.get_current_url()

    elif action in ['get_title', 'title']:
        return module.get_title()

    elif action in ['get_source', 'source']:
        return module.get_page_source()

    # Navigation controls
    elif action == 'back':
        return module.back()

    elif action == 'forward':
        return module.forward()

    elif action == 'refresh':
        return module.refresh()

    # Frames
    elif action in ['switch_frame', 'frame']:
        return module.switch_to_frame(params['frame'])

    elif action == 'default_content':
        return module.switch_to_default_content()

    # Windows
    elif action in ['switch_window', 'window']:
        return module.switch_to_window(params['window'])

    elif action == 'close_window':
        return module.close_window()

    # Alerts
    elif action in ['accept_alert', 'accept']:
        return module.accept_alert()

    elif action in ['dismiss_alert', 'dismiss']:
        return module.dismiss_alert()

    elif action == 'get_alert_text':
        return module.get_alert_text()

    # Cookies
    elif action == 'add_cookie':
        return module.add_cookie(params['name'], params['value'], **params.get('options', {}))

    elif action == 'get_cookie':
        return module.get_cookie(params['name'])

    elif action == 'get_all_cookies':
        return module.get_all_cookies()

    elif action == 'delete_cookie':
        return module.delete_cookie(params['name'])

    elif action == 'delete_all_cookies':
        return module.delete_all_cookies()

    # Mouse actions
    elif action == 'hover':
        return module.hover(
            params['locator'],
            params.get('by', 'css'),
            params.get('wait')
        )

    elif action == 'drag_and_drop':
        return module.drag_and_drop(
            params['source'],
            params['target'],
            params.get('by', 'css'),
            params.get('wait')
        )

    # Scrolling
    elif action in ['scroll', 'scroll_to']:
        return module.scroll_to_element(
            params['locator'],
            params.get('by', 'css'),
            params.get('wait')
        )

    # File upload
    elif action in ['upload', 'upload_file']:
        return module.upload_file(
            params['locator'],
            params['file_path'],
            params.get('by', 'css'),
            params.get('wait')
        )

    # Window management
    elif action == 'set_window_size':
        return module.set_window_size(params['width'], params['height'])

    elif action == 'maximize':
        return module.maximize_window()

    elif action == 'minimize':
        return module.minimize_window()

    # Quit
    elif action == 'quit':
        return module.quit()

    else:
        raise ValueError(f"Unknown action: {action}")
