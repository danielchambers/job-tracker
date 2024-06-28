# Job Tracker
Application that enables users to save and organize job postings from various ATS job boards.

## Demo

https://github.com/danielchambers/jobtracker/assets/10182848/b700311d-f513-4bba-b4ac-4000e0d11b49

# Browser Extension

This browser extension allows users to easily save job postings from various job boards (BambooHR, Greenhouse, Lever, and SmartRecruiters) to a Google Sheet. It injects a user-friendly interface into supported job listing pages, enabling quick selection of the destination document and sheet for each job application.

## Installation

1. Clone this repository to your local machine.
2. Open Firefox and navigate to `about:debugging#/runtime/this-firefox`.
3. Click on "Load Temporary Add-on" and select the `manifest.json` file from the cloned repository.
4. The extension should now be active and ready to use on supported job board websites.

## Usage

1. Navigate to a supported job listing page.
2. Use the dropdown menus in the injected header to select the destination document and sheet.
3. Click the "Save" button to add the current job listing to your selected Google Sheet.

# Flask Server

This Flask server component works in conjunction with the browser extension. It handles requests to add job listings to a Google Sheets document, facilitating seamless job application tracking.

## Installation

1. Clone this repository to your local machine.
2. Navigate to the server directory.
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment:
- On Windows: `venv\Scripts\activate`
- On macOS and Linux: `source venv/bin/activate`
5. Install the required dependencies: `python server.py`
6. Set up your Google Sheets API credentials and save them as `client_secret.json` in the server directory.

## Usage

1. Ensure your virtual environment is activated.
2. Run the server: `python server.py`
3. The server will start running on `http://localhost:5000`.
4. Keep the server running while using the browser extension to add job listings to your Google Sheet.

Note: Make sure the server is running before attempting to save job listings through the browser extension.  
