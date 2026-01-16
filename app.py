import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Nomination Form",
    page_icon="📋",
    layout="wide"
)

# Initialize session state (no need for form_selections as Streamlit handles widget state automatically)

# Google Sheets configuration
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Sample list of people - replace with your actual list
PEOPLE_LIST = [
    "Person 1", "Person 2", "Person 3", "Person 4", "Person 5",
    "Person 6", "Person 7", "Person 8", "Person 9", "Person 10",
    "Person 11", "Person 12", "Person 13", "Person 14", "Person 15",
    "Person 16", "Person 17", "Person 18", "Person 19", "Person 20"
]

# Questions for <1.5 years of experience
QUESTIONS_LESS_THAN_1_5_YOE = [
    "Question 1 (<1.5 YOE)",
    "Question 2 (<1.5 YOE)",
    "Question 3 (<1.5 YOE)",
    "Question 4 (<1.5 YOE)",
    "Question 5 (<1.5 YOE)",
    "Question 6 (<1.5 YOE)",
    "Question 7 (<1.5 YOE)",
    "Question 8 (<1.5 YOE)",
    "Question 9 (<1.5 YOE)",
    "Question 10 (<1.5 YOE)"
]

# Questions for >1.5 years of experience
QUESTIONS_MORE_THAN_1_5_YOE = [
    "Question 1 (>1.5 YOE)",
    "Question 2 (>1.5 YOE)",
    "Question 3 (>1.5 YOE)",
    "Question 4 (>1.5 YOE)",
    "Question 5 (>1.5 YOE)",
    "Question 6 (>1.5 YOE)",
    "Question 7 (>1.5 YOE)",
    "Question 8 (>1.5 YOE)",
    "Question 9 (>1.5 YOE)",
    "Question 10 (>1.5 YOE)"
]

def get_current_selections():
    """Get all current selections from session state"""
    selections = []
    # Check all question keys
    for i in range(len(QUESTIONS_LESS_THAN_1_5_YOE)):
        key = f"less_1_5_{i}"
        value = st.session_state.get(key, "Select...")
        if value and value != "Select...":
            selections.append(value)
    
    for i in range(len(QUESTIONS_MORE_THAN_1_5_YOE)):
        key = f"more_1_5_{i}"
        value = st.session_state.get(key, "Select...")
        if value and value != "Select...":
            selections.append(value)
    
    return selections

def get_available_people(current_key, current_value):
    """
    Returns list of people available for selection.
    People who have been selected 2 times are excluded.
    """
    # Get all current selections except the current one being edited
    all_selections = []
    
    # Check all question keys except current
    for i in range(len(QUESTIONS_LESS_THAN_1_5_YOE)):
        key = f"less_1_5_{i}"
        if key != current_key:
            value = st.session_state.get(key, "Select...")
            if value and value != "Select...":
                all_selections.append(value)
    
    for i in range(len(QUESTIONS_MORE_THAN_1_5_YOE)):
        key = f"more_1_5_{i}"
        if key != current_key:
            value = st.session_state.get(key, "Select...")
            if value and value != "Select...":
                all_selections.append(value)
    
    # Count nominations
    nomination_count = {}
    for person in all_selections:
        nomination_count[person] = nomination_count.get(person, 0) + 1
    
    # Build available list
    available = []
    for person in PEOPLE_LIST:
        count = nomination_count.get(person, 0)
        # Include if count < 2 OR if it's the currently selected person (to allow keeping selection)
        if count < 2 or person == current_value:
            available.append(person)
    
    return available

def get_nomination_summary():
    """Get summary of current nominations"""
    all_selections = get_current_selections()
    nomination_count = {}
    for person in all_selections:
        nomination_count[person] = nomination_count.get(person, 0) + 1
    return nomination_count

def connect_to_google_sheets(credentials_json):
    """Connect to Google Sheets using service account credentials"""
    try:
        creds_dict = json.loads(credentials_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {str(e)}")
        return None

def submit_to_google_sheets(client, spreadsheet_name, worksheet_name, data):
    """Submit form data to Google Sheets"""
    try:
        # Open the spreadsheet
        spreadsheet = client.open(spreadsheet_name)
        
        # Get or create the worksheet
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=30)
            # Add headers
            headers = ["Timestamp", "Full Name", "Email ID"] + QUESTIONS_LESS_THAN_1_5_YOE + QUESTIONS_MORE_THAN_1_5_YOE
            worksheet.append_row(headers)
        
        # Append the data
        result = worksheet.append_row(data)
        
        # Check if append was successful
        # gspread's append_row returns a dict with 'updates' key on success
        if result:
            return True
        else:
            return False
            
    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"❌ Spreadsheet '{spreadsheet_name}' not found. Please check the name.")
        return False
    except gspread.exceptions.APIError as e:
        st.error(f"❌ Google Sheets API Error: {str(e)}")
        return False
    except Exception as e:
        st.error(f"❌ Error submitting to Google Sheets: {str(e)}")
        return False

def main():
    st.title("📋 Nomination Form")
    st.markdown("---")
    
    # Sidebar for Google Sheets configuration
    # with st.sidebar:
    #     st.header("⚙️ Configuration")
    #     credentials_json = st.text_area(
    #         "Google Service Account JSON",
    #         height=200,
    #         help="Paste your Google Service Account JSON credentials here"
    #     )
    #     spreadsheet_name = st.text_input(
    #         "Google Spreadsheet Name",
    #         value="Nomination Form Responses",
    #         help="Name of the Google Spreadsheet"
    #     )
    #     worksheet_name = st.text_input(
    #         "Worksheet Name",
    #         value="Responses",
    #         help="Name of the worksheet/tab in the spreadsheet"
    #     )
    # Google Sheets configuration - Load from secrets
    try:
        credentials_dict = dict(st.secrets["gcp_service_account"])
        credentials_json = json.dumps(credentials_dict)
        spreadsheet_name = st.secrets.get("spreadsheet_name", "Gremmy Awards Nominations")
        worksheet_name = st.secrets.get("worksheet_name", "Responses")
    except Exception as e:
        st.error("⚠️ Please configure secrets.toml file with your Google credentials")
        st.stop()
    
    # Personal Information Section
    st.header("👤 Personal Information")
    col1, col2 = st.columns(2)
    
    with col1:
        full_name = st.text_input("Full Name *", placeholder="Enter your full name", key="full_name")
    
    with col2:
        email_id = st.text_input("Email ID *", placeholder="Enter your email address", key="email_id")
    
    st.markdown("---")
    
    # Questions for <1.5 years of experience
    st.header("📝 Questions for <1.5 Years of Experience")
    st.markdown("*Please select one person for each question*")
    
    answers_less_than_1_5 = []
    for i, question in enumerate(QUESTIONS_LESS_THAN_1_5_YOE):
        key = f"less_1_5_{i}"
        
        # Get current value from session state (Streamlit stores it with the key)
        current_value = st.session_state.get(key, "Select...")
        
        # Get available people based on other selections
        available_people = get_available_people(key, current_value)
        
        # Add "Select..." as first option
        options = ["Select..."] + available_people
        
        # Ensure current value is in options (if it was selected before but now unavailable)
        if current_value and current_value != "Select..." and current_value not in options:
            options.append(current_value)
        
        # Determine index
        # if current_value == "Select..." or current_value not in options:
        #     default_index = 0
        # else:
        #     default_index = options.index(current_value)

        # CHANGES MADE HERE CHECK HERE
        try:
            default_index = options.index(current_value) if current_value in options else 0
        except ValueError:
            default_index = 0
        
        selected = st.selectbox(
            f"{i+1}. {question} *",
            options=options,
            key=key,
            index=default_index
        )
        
        if selected and selected != "Select...":
            answers_less_than_1_5.append(selected)
        else:
            answers_less_than_1_5.append("")
    
    st.markdown("---")
    
    # Questions for >1.5 years of experience
    st.header("📝 Questions for >1.5 Years of Experience")
    st.markdown("*Please select one person for each question*")
    
    answers_more_than_1_5 = []
    for i, question in enumerate(QUESTIONS_MORE_THAN_1_5_YOE):
        key = f"more_1_5_{i}"
        
        # Get current value from session state (Streamlit stores it with the key)
        current_value = st.session_state.get(key, "Select...")
        
        # Get available people based on other selections
        available_people = get_available_people(key, current_value)
        
        # Add "Select..." as first option
        options = ["Select..."] + available_people
        
        # Ensure current value is in options (if it was selected before but now unavailable)
        if current_value and current_value != "Select..." and current_value not in options:
            options.append(current_value)
        
        # Determine index
        # if current_value == "Select..." or current_value not in options:
        #     default_index = 0
        # else:
        #     default_index = options.index(current_value)
        # CHANGES MADE HERE CHECK HERE
        try:
            default_index = options.index(current_value) if current_value in options else 0
        except ValueError:
            default_index = 0
        
        selected = st.selectbox(
            f"{i+1}. {question} *",
            options=options,
            key=key,
            index=default_index
        )
        
        if selected and selected != "Select...":
            answers_more_than_1_5.append(selected)
        else:
            answers_more_than_1_5.append("")
    
    st.markdown("---")
    
    # Display nomination count summary
    nomination_summary = get_nomination_summary()
    with st.expander("📊 Nomination Summary"):
        if nomination_summary:
            st.write("Current nomination counts:")
            for person, count in sorted(nomination_summary.items()):
                status = "✅ Available" if count < 2 else "❌ Limit Reached (2/2)"
                st.write(f"- **{person}**: {count}/2 {status}")
        else:
            st.write("No nominations yet.")
    
    # Submit button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        submit_button = st.button("Submit Form", type="primary", use_container_width=True)
    
    if submit_button:
        # Validation
        errors = []
        
        if not full_name or not full_name.strip():
            errors.append("Full Name is required")
        
        if not email_id or not email_id.strip():
            errors.append("Email ID is required")
        elif "@" not in email_id:
            errors.append("Please enter a valid email address")
        
        # Check all questions are answered
        for i, answer in enumerate(answers_less_than_1_5):
            if not answer or answer == "Select...":
                errors.append(f"Question {i+1} in <1.5 YOE section is required")
        
        for i, answer in enumerate(answers_more_than_1_5):
            if not answer or answer == "Select...":
                errors.append(f"Question {i+1} in >1.5 YOE section is required")
        
        if errors:
            st.error("Please fix the following errors:")
            for error in errors:
                st.error(f"• {error}")
        else:
            # Check Google Sheets configuration
            if not credentials_json:
                st.error("Please configure Google Sheets credentials")
            else:
                with st.spinner("Submitting form..."):
                    # Connect to Google Sheets
                    client = connect_to_google_sheets(credentials_json)
                    
                    if client:
                        # Prepare data
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        data = [timestamp, full_name, email_id] + answers_less_than_1_5 + answers_more_than_1_5
                        
                        # Submit to Google Sheets
                        if submit_to_google_sheets(client, spreadsheet_name, worksheet_name, data):
                            st.success("✅ Form submitted successfully!")
                            st.balloons()
                            
                            # Clear form by clearing all question keys BEFORE rerun
                            for i in range(len(QUESTIONS_LESS_THAN_1_5_YOE)):
                                key = f"less_1_5_{i}"
                                if key in st.session_state:
                                    del st.session_state[key]
                            
                            for i in range(len(QUESTIONS_MORE_THAN_1_5_YOE)):
                                key = f"more_1_5_{i}"
                                if key in st.session_state:
                                    del st.session_state[key]
                            
                            # Clear name and email
                            if 'full_name' in st.session_state:
                                del st.session_state['full_name']
                            if 'email_id' in st.session_state:
                                del st.session_state['email_id']
                            
                            # Add a small delay so user can see the success message
                            import time
                            time.sleep(2)
                            
                            # NOW rerun (only once!)
                            st.rerun()
                        else:
                            st.error("❌ Failed to submit form. Please try again.")

if __name__ == "__main__":
    main()

