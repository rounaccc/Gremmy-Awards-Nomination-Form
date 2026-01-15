# Nomination Form - Streamlit App

A Streamlit-based nomination form application that collects responses and stores them in Google Sheets.

## Features

- 📋 Form with personal information (Name, Email)
- 📝 20 questions divided into two sections:
  - 10 questions for <1.5 years of experience
  - 10 questions for >1.5 years of experience
- 🔄 Dynamic dropdowns that prevent selecting the same person more than 2 times
- ✅ All fields are required
- 📊 Real-time nomination count tracking
- 📤 Google Sheets integration for data storage

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Google Sheets Setup

1. **Create a Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable Google Sheets API:**
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Sheets API" and enable it
   - Search for "Google Drive API" and enable it

3. **Create Service Account:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in the service account details and create it
   - Click on the created service account
   - Go to "Keys" tab > "Add Key" > "Create new key"
   - Choose JSON format and download the key file

4. **Share Google Spreadsheet:**
   - Create a new Google Spreadsheet or use an existing one
   - Share it with the service account email (found in the JSON file, looks like `xxx@xxx.iam.gserviceaccount.com`)
   - Give it "Editor" permissions

5. **Add Credentials to App:**
   - Open the downloaded JSON file
   - Copy its entire contents
   - Paste it in the sidebar of the Streamlit app when running

### 3. Customize the App

Edit `app.py` to customize:

- **PEOPLE_LIST**: Replace with your actual list of people
- **QUESTIONS_LESS_THAN_1_5_YOE**: Replace with your actual questions for <1.5 YOE
- **QUESTIONS_MORE_THAN_1_5_YOE**: Replace with your actual questions for >1.5 YOE

### 4. Run the App

```bash
streamlit run app.py
```

The app will open in your default web browser at `http://localhost:8501`

## How It Works

1. **Dynamic Dropdowns**: The app tracks how many times each person has been nominated. Once a person reaches 2 nominations, they are removed from all dropdown options.

2. **Form Validation**: All fields are required. The form validates:
   - Full name is not empty
   - Email contains "@" symbol
   - All 20 questions have been answered

3. **Data Storage**: When submitted, the form data is appended to the specified Google Sheet with:
   - Timestamp
   - Full Name
   - Email ID
   - All 20 answers

## File Structure

```
.
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Notes

- The nomination count resets when the page is refreshed
- Each person can be nominated a maximum of 2 times per form submission
- The Google Spreadsheet must be shared with the service account email for the app to work

