from flask import Flask, request, jsonify
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager  
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
import psutil


app = Flask(__name__)

# Store browser instances
browsers = {}

# Function to get a WebDriver instance
def get_driver(app_name):
    if app_name.lower() == "chrome":
        options = webdriver.ChromeOptions()
        return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    elif app_name.lower() == "firefox":
        options = webdriver.FirefoxOptions()
        return webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    return None

@app.route("/check")
def check_func():
  return "Api is fine"

# API 1: Start a browser
@app.route("/start", methods=["GET"])
def start_browser():
    app_name = request.args.get("app")
    if not app_name:
        return jsonify({"error": "Missing 'app' parameter"}), 400

    if app_name.lower() not in ["chrome", "firefox"]:
        return jsonify({"error": "Invalid browser name"}), 400

    if app_name.lower() in browsers:
        return jsonify({"message": f"{app_name} is already running"}), 200

    driver = get_driver(app_name)
    if driver:
        browsers[app_name.lower()] = driver
        return jsonify({"message": f"Started {app_name} browser"}), 200
    else:
        return jsonify({"error": f"Failed to start {app_name}"}), 500

# API 2: Stop a browser
@app.route("/stop", methods=["GET"])
def stop_browser():
    app_name = request.args.get("app")

    if not app_name:
        return jsonify({"error": "Missing 'app' parameter"}), 400

    if app_name.lower() not in ["chrome", "firefox"]:
        return jsonify({"error": "Invalid browser name"}), 400

    if app_name.lower() not in browsers:
        return jsonify({"error": f"{app_name} browser is not running"}), 400

    driver = browsers.pop(app_name.lower())
    driver.quit()

    # Kill process manually if still running
    for proc in psutil.process_iter():
        try:
            if app_name.lower() in proc.name().lower():
                proc.kill()
        except psutil.NoSuchProcess:
            pass

    return jsonify({"message": f"Stopped {app_name} browser"}), 200


@app.route("/open",methods=["GET"])
def open_url():
  app_name=request.args.get("app")
  url=request.args.get("url")
  if not app_name or not url:
    return jsonify({"error": "Missing 'app' or 'url' parameter"}), 400

  if app_name.lower() not in browsers:
    return jsonify({"error": f"{app_name} browser is not running"}), 400
  
  driver = browsers[app_name.lower()]
  driver.get(url)
  return jsonify({"message: " f"Opened {url} in {app_name}"}), 200

# Run the server
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)