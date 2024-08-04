from selenium.webdriver import Chrome, ChromeOptions
import threading

noogleDriver = None


def proxy_browser():
    options = ChromeOptions()
#     options.add_argument('--proxy-server={proxy}'.format(proxy=proxy))
    options.add_argument('log-level=3')
    options.add_argument("--window-size=1880x1020")
    ##for screen scrape
    # options.add_argument(f'user-agent={userAgent}')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--disable-extensions')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-infobars')
    options.add_argument('--start-maximized')
    options.add_argument("--disable-notifications")
    options.add_argument('--disable-popup-blocking')


    prefs = {"profile.default_content_setting_values.notifications" : 2,
    "webrtc.ip_handling_policy" : "disable_non_proxied_udp",
    "webrtc.multiple_routes_enabled": False,
    "webrtc.nonproxied_udp_enabled" : False,
    "profile.default_content_setting_values.geolocation" :2}
    options.add_experimental_option("prefs",prefs)
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    driver=Chrome(options=options)
    return driver

driverReady = threading.Event()
def DriverInfinite():
    global noogleDriver
    print("Starting driver management thread...")
    while True:
        try:
            if noogleDriver is None or not noogleDriver.service.is_connectable():
                # if no driver exists or unresponsive, create a new one
                noogleDriver = proxy_browser()
                driverReady.set()
                print("New instance initiated")
        except Exception as e:
            print(e)
            try:
                noogleDriver.quit()
            except:# Ensure a clean exit for the old driver
                noogleDriver = None
        
        
        
        
driverThread = threading.Thread(target=DriverInfinite, daemon=True)
driverThread.start()
