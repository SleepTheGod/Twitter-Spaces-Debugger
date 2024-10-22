import os
import subprocess
import sys
import json
import time
import undetected_chromedriver.v2 as uc
from flask import Flask, render_template, jsonify, request
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

app = Flask(__name__)

def install(package):
    """Install a package using pip."""
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def install_chromedriver():
    """Install ChromeDriver that matches the installed Chrome version."""
    # Check Chrome version
    try:
        from selenium import webdriver
        chrome = webdriver.Chrome()
        chrome_version = chrome.capabilities['browserVersion']
        major_version = chrome_version.split('.')[0]
    except Exception as e:
        print(f"Error determining Chrome version: {e}")
        return

    # Download ChromeDriver
    chromedriver_url = f"https://chromedriver.storage.googleapis.com/{major_version}/chromedriver_win32.zip"
    
    # Download and extract ChromeDriver
    subprocess.run(['curl', '-O', chromedriver_url])
    subprocess.run(['unzip', 'chromedriver_win32.zip'])
    subprocess.run(['move', 'chromedriver.exe', os.getcwd()])  # Move to current directory
    subprocess.run(['del', 'chromedriver_win32.zip'])  # Delete the zip file

def log_request(request):
    return {
        "url": request['url'],
        "method": request['method'],
        "headers": request['headers'],
        "postData": request.get('postData', '')
    }

def log_response(response):
    return {
        "url": response['url'],
        "status": response['status'],
        "headers": response['headers'],
        "body": response.get('body', '')
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_debug', methods=['POST'])
def start_debug():
    # Install necessary packages
    install('selenium')
    install('undetected-chromedriver')

    # Install ChromeDriver
    install_chromedriver()

    # Set up Chrome options
    options = uc.ChromeOptions()
    options.add_argument("--headless")  # Uncomment if you want to run in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    # Enable performance logging
    caps = DesiredCapabilities().CHROME
    caps["goog:loggingPrefs"] = {"performance": "ALL", "browser": "ALL"}
    caps["goog:chromeOptions"] = {"w3c": False}

    # Start Chrome
    driver = uc.Chrome(options=options, desired_capabilities=caps)

    # Navigate to Twitter Spaces
    driver.get('https://twitter.com/i/spaces')  # Change to your Spaces URL if needed

    # Wait for a while to capture logs
    time.sleep(30)  # Adjust this time as needed for your use case

    # Capture performance logs
    performance_logs = driver.get_log('performance')
    requests = []
    responses = []

    for entry in performance_logs:
        log_entry = json.loads(entry['message'])['message']
        if 'Network.requestWillBeSent' in log_entry['method']:
            requests.append(log_request(log_entry['params']['request']))
        elif 'Network.responseReceived' in log_entry['method']:
            responses.append(log_response(log_entry['params']['response']))

    # Capture console logs
    console_logs = driver.get_log('browser')

    # Close the driver
    driver.quit()

    return jsonify({
        'requests': requests,
        'responses': responses,
        'console_logs': [entry['message'] for entry in console_logs]
    })

if __name__ == '__main__':
    app.run(debug=True)
