# Requirements you must first pip install selenium and pip install undetected-chromedriver 
# You must also have https://developer.chrome.com/docs/chromedriver/downloads
import time
import json
import undetected_chromedriver.v2 as uc
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def log_request(request):
    print("Request:")
    print(f"  URL: {request['url']}")
    print(f"  Method: {request['method']}")
    print(f"  Headers: {json.dumps(request['headers'], indent=2)}")
    print(f"  Post Data: {request.get('postData', '')}\n")

def log_response(response):
    print("Response:")
    print(f"  URL: {response['url']}")
    print(f"  Status: {response['status']}")
    print(f"  Headers: {json.dumps(response['headers'], indent=2)}")
    print(f"  Body: {response.get('body', '')}\n")
options = uc.ChromeOptions()
options.add_argument("--headless")  # Uncomment if you want to run in headless mode
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
caps = DesiredCapabilities().CHROME
caps["goog:loggingPrefs"] = {"performance": "ALL", "browser": "ALL"}
caps["goog:chromeOptions"] = {"w3c": False}
driver = uc.Chrome(options=options, desired_capabilities=caps)
driver.get('https://twitter.com/i/spaces')  # Change to your Spaces URL if needed
time.sleep(30)
performance_logs = driver.get_log('performance')
for entry in performance_logs:
    log_entry = json.loads(entry['message'])['message']
    if 'Network.requestWillBeSent' in log_entry['method']:
        log_request(log_entry['params']['request'])
    elif 'Network.responseReceived' in log_entry['method']:
        log_response(log_entry['params']['response'])
console_logs = driver.get_log('browser')
for entry in console_logs:
    print(f"Console Log: {entry['message']}")
driver.quit()
