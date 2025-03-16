from flask import Flask, render_template, jsonify, request
import aiohttp
import asyncio
import threading

app = Flask(__name__)

# Default URL (fallback in case no URL is provided)
default_url = "http://www.example.com"

# Number of requests to send every second
requests_per_second = 1000

# Variable to control the request-sending process
request_thread = None
stop_event = None
current_url = default_url  # Initially, use the default URL

# Asynchronous function to send requests
async def send_request(session):
    try:
        async with session.get(current_url) as response:
            pass  # Optionally, log or process the response
    except Exception as e:
        print(f"An error occurred: {e}")

# Function to handle sending requests concurrently
async def send_requests():
    # Increase the connection limit
    connector = aiohttp.TCPConnector(limit_per_host=10000)
    async with aiohttp.ClientSession(connector=connector) as session:
        while not stop_event.is_set():
            tasks = [send_request(session) for _ in range(requests_per_second)]
            await asyncio.gather(*tasks)
            await asyncio.sleep(1)  # Control the request rate

# Route to serve the HTML page (if needed for debugging)
@app.route('/')
def home():
    return "Flask Backend Running"

# Route to start sending requests with a custom URL
@app.route('/start_requests', methods=['GET'])
def start_requests():
    global request_thread, stop_event, current_url

    # Get the custom URL from the query parameters, if provided
    user_url = request.args.get('url')
    if user_url:
        current_url = user_url  # Set the URL to the user-provided URL

    if request_thread is None or not request_thread.is_alive():
        stop_event = asyncio.Event()
        # Run the asynchronous event loop in a separate thread
        request_thread = threading.Thread(target=lambda: asyncio.run(send_requests()))
        request_thread.start()

        return jsonify({"message": f"Requests started to {current_url}!"})
    else:
        return jsonify({"message": "Requests are already running!"})

# Route to stop sending requests
@app.route('/stop_requests', methods=['GET'])
def stop_requests():
    global stop_event

    if stop_event:
        stop_event.set()  # Set the stop event to stop the requests
        return jsonify({"message": f"Requests stopped to {current_url}!"})
    else:
        return jsonify({"message": "No requests are running!"})

if __name__ == "__main__":
    app.run(debug=True)
