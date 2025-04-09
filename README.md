# Moodle Downloader

A web application that allows you to easily download course materials from your Moodle LMS instance. This tool features a React frontend and a Python backend that handles authentication and automated file downloads.

## Features

- Login to your Moodle account
- Browse available semesters and courses
- Download all materials from selected modules
- Progress tracking for downloads
- Files organized by module name

## Prerequisites

### Backend Requirements

- Python 3.8 or newer
- pip (Python package manager)
- Chrome browser (required for Playwright)

### Frontend Requirements

- Node.js 16.x or newer
- npm (Node package manager)

## Installation

### Clone the Repository

```bash
git clone https://github.com/your-username/lms-bot.git
cd lms-bot
```

### Backend Setup

1. **Install Python dependencies**:
   ```bash
   cd backend
   pip install flask flask-cors playwright requests
   ```

2. **Install Playwright browsers**:
   ```bash
   playwright install chromium
   ```

3. **Create downloads directory** (if it doesn't exist):
   ```bash
   mkdir -p downloads
   ```

### Frontend Setup

1. **Install Node.js dependencies**:
   ```bash
   cd ../frontend
   npm install
   ```

## Running the Application

### Start the Backend Server

```bash
cd backend
python app.py
```

The backend will run on http://localhost:5000

### Start the Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend will run on http://localhost:5173

## Usage

1. Open your browser and navigate to http://localhost:5173
2. Enter your Moodle credentials
3. Select a semester from the list
4. Choose a module to download materials from
5. Click "Download All Materials"
6. Wait for the download to complete

Downloaded files will be saved in the `backend/downloads` directory, organized by module name.

## Troubleshooting

- **Login Issues**: Verify your Moodle credentials
- **Download Failures**: Check the backend terminal for error messages
- **Connection Errors**: Ensure both frontend and backend servers are running
- **Browser Issues**: Make sure Chrome is installed on your system

## Notes

- The default Moodle URL is set to http://192.248.50.240 - if your institution uses a different URL, you'll need to modify the URLs in the `downloader.py` file.
- If you experience issues with downloads timing out, try increasing the timeout values in the Python code.
