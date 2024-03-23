# Import necessary modules
from flask import Flask, request, jsonify

# Create a Flask application
app = Flask(__name__)

# Define a route for webhook requests
@app.route('/webhook', methods=['POST'])
def webhook():
    # Get JSON data from the incoming request
    data = request.json
    
    # Log the received data (you might want to process it instead)
    print("Received webhook data:", data)
    
    # Respond back with a success message
    return jsonify({'status': 'success', 'data': data}), 200

# Run the Flask application on port 5000
if __name__ == '__main__':
    app.run(port=5000, debug=True)
print("Done")