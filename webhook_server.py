from flask import Flask, request, jsonify
import hmac
import hashlib
import os
from discord_integration import handle_github_webhook

app = Flask(__name__)

# Get the GitHub webhook secret from environment variable
WEBHOOK_SECRET = os.environ.get('GITHUB_WEBHOOK_SECRET')


def verify_signature(payload_body, signature_header):
    """
    Verify that the payload was sent from GitHub
    """
    if not WEBHOOK_SECRET:
        # If no secret is set, skip verification (not recommended for production)
        return True
    
    if not signature_header:
        return False
    
    hash_object = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    
    return hmac.compare_digest(expected_signature, signature_header)


@app.route('/github-webhook', methods=['POST'])
def github_webhook():
    """
    Endpoint to receive GitHub webhook events
    """
    # Get the signature from the header
    signature_header = request.headers.get('X-Hub-Signature-256')
    
    # Get the payload body
    payload_body = request.get_data()
    
    # Verify the signature
    if not verify_signature(payload_body, signature_header):
        return jsonify({"error": "Invalid signature"}), 401
    
    # Get the event type
    event_type = request.headers.get('X-GitHub-Event')
    
    # Parse the JSON payload
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({"error": "Invalid JSON payload"}), 400
    except Exception as e:
        return jsonify({"error": "Invalid JSON payload"}), 400
    
    # Handle the GitHub event
    try:
        result = handle_github_webhook(payload, event_type)
        return jsonify(result), 200
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({"status": "ok", "service": "GitHub-Discord Integration"}), 200


if __name__ == '__main__':
    # Run the Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)