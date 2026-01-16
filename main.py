import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Gremmy Awards Nomination Form",
    page_icon="🏆",
    layout="wide"
)

# Google Sheets configuration
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Employee lists based on YOE
PEOPLE_LESS_THAN_1_5_YOE = [
    "Abhishhek Patil", "Karan Agarwal", "Dimple Thanvi", "Aman Nirmal",
    "Yuvrajsingh Rajpurohit", "Mihir Furiya", "Bhavana Sharma", "Samia Malik",
    "Vidhi Shah", "Sejal Suri", "Smit Mistry", "Het Ghelani",
    "Nishtha Thakkar", "Pakshal Mody", "Arya Raheja", "Rounak Bachwani",
    "Vidhi Maheshwari", "Husein Katwarawala", "Omkar Chavan", "Shriram Dayama",
    "Rajnandini Gupta", "Aayushi Lunia", "Ritika Nair", "Priyansi Sheth"
]

PEOPLE_MORE_THAN_1_5_YOE = [
    "Nivita Shetty", "Neal Shah", "Sneha Banerjee", "Prachi Thakkar",
    "Nehal Bajaj", "Muskan Jhunjhunwala", "Saanchi Bathla", "Krisha Dedhia",
    "Simoni Jain", "Megha Bansal", "Ritika Jalan", "Aakash Sethia",
    "Durgesh Singh", "Vidur Bhatnagar", "Rhea Christie Anthonyraj", "Jainee Satra",
    "Devesh Newatia", "Divijaa Talwar", "Mohammad Masbah Khan", "Nishita Kikani",
    "Janvee Shah", "Akshiti Vohra", "Raunak Makhija", "Krishu Agrawal",
    "Amisha Khetan", "Vinayak Karnawat", "Yerra Haritha", "Aditya Padia"
]

# All people combined for tracking nominations
ALL_PEOPLE = PEOPLE_LESS_THAN_1_5_YOE + PEOPLE_MORE_THAN_1_5_YOE

# Awards for Section 1 (2 nominations: one from each YOE group)
AWARDS_SECTION_1 = {
    "Just a chill guy": "Aag lagi basti mein, tera bhai masti mein",
    "ChatterBox/Essayist": "demo description",
    "Human Serotonin": "demo description",
    "Tech Related, Human Stack overflow": "demo description",
    "Sassy Comeback/One liners": "demo description",
    "Silent Killer (Less talks, more impact)": "demo description",
    "Bade miyan Chote Miyan": "demo description"
}

# Awards for Section 2 (1 nomination: anyone from any group)
AWARDS_SECTION_2 = {
    "High on Caffeine": "demo description",
    "IT Issues, Cntrl+Alt": "demo description",
    "Digital Ghost": "demo description",
    "In the Zone": "demo description",
    "Jack of All": "Google se bhi zyada gyaan",
    "Seedha": "demo description",
    "Tedha": "demo description",
    "Likely to laugh at their own jokes": "demo description",
    "Karam to Kaand": "demo description",
    "Jugaadu": "demo description"
}

def get_section_1_selections():
    """Get all current selections from Section 1 only"""
    selections = []
    for i in range(len(AWARDS_SECTION_1)):
        key_less = f"sec1_less_{i}"
        key_more = f"sec1_more_{i}"
        
        value_less = st.session_state.get(key_less, "Select...")
        value_more = st.session_state.get(key_more, "Select...")
        
        if value_less and value_less != "Select...":
            selections.append(value_less)
        if value_more and value_more != "Select...":
            selections.append(value_more)
    
    return selections

def get_section_2_selections():
    """Get all current selections from Section 2 only"""
    selections = []
    for i in range(len(AWARDS_SECTION_2)):
        key = f"sec2_{i}"
        value = st.session_state.get(key, "Select...")
        if value and value != "Select...":
            selections.append(value)
    
    return selections

def get_nomination_count_section_1():
    """Get count of nominations for each person in Section 1 only"""
    selections = get_section_1_selections()
    nomination_count = {}
    for person in selections:
        nomination_count[person] = nomination_count.get(person, 0) + 1
    return nomination_count

def get_nomination_count_section_2():
    """Get count of nominations for each person in Section 2 only"""
    selections = get_section_2_selections()
    nomination_count = {}
    for person in selections:
        nomination_count[person] = nomination_count.get(person, 0) + 1
    return nomination_count

def get_available_people(people_list, current_key, current_value, section):
    """
    Returns list of people available for selection from given people_list.
    People who have been selected 2 times in the SAME section are excluded.
    section: 1 or 2
    """
    if section == 1:
        nomination_count = get_nomination_count_section_1()
    else:
        nomination_count = get_nomination_count_section_2()
    
    # Remove current selection from count to allow keeping it
    if current_value and current_value != "Select...":
        if current_value in nomination_count:
            nomination_count[current_value] = nomination_count.get(current_value, 0) - 1
    
    # Build available list
    available = []
    for person in people_list:
        count = nomination_count.get(person, 0)
        if count < 2:
            available.append(person)
    
    return available

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
    """Submit form data to Google Sheets with retry logic"""
    import time
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            spreadsheet = client.open(spreadsheet_name)
            
            try:
                worksheet = spreadsheet.worksheet(worksheet_name)
            except gspread.exceptions.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=50)
                
                # Build headers
                headers = ["Timestamp", "Full Name", "Employee ID", "Email ID"]
                
                # Section 1 headers (2 columns per award)
                for award_name in AWARDS_SECTION_1.keys():
                    headers.append(f"{award_name} (<1.5 YOE)")
                    headers.append(f"{award_name} (>1.5 YOE)")
                
                # Section 2 headers (1 column per award)
                for award_name in AWARDS_SECTION_2.keys():
                    headers.append(award_name)
                
                worksheet.append_row(headers)
            
            result = worksheet.append_row(data)
            
            if result:
                return True
            else:
                return False
                
        except gspread.exceptions.APIError as e:
            error_message = str(e)
            
            if "RESOURCE_EXHAUSTED" in error_message or "Quota exceeded" in error_message or "429" in error_message:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + (attempt * 0.5)
                    st.warning(f"⏳ Server is busy. Retrying in {wait_time:.1f} seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    st.error("❌ Server is too busy right now. Please wait 30 seconds and try again.")
                    return False
            else:
                st.error(f"❌ Google Sheets API Error: {error_message}")
                return False
                
        except gspread.exceptions.SpreadsheetNotFound:
            st.error(f"❌ Spreadsheet '{spreadsheet_name}' not found. Please check the name.")
            return False
            
        except Exception as e:
            st.error(f"❌ Error submitting to Google Sheets: {str(e)}")
            return False
    
    return False

def main():
    # Initialize form submission state
    if 'form_submitted' not in st.session_state:
        st.session_state['form_submitted'] = False
    if 'show_success' not in st.session_state:
        st.session_state['show_success'] = False
    
    st.title("🏆 Gremmy Awards Nomination Form")
    
    # Show success message if form was just submitted
    if st.session_state['show_success']:
        st.success("✅ Form submitted successfully!")
        st.balloons()
        st.info("✅ Thank you! Your nominations have been recorded.")
        st.session_state['show_success'] = False
    
    st.markdown("---")
    
    # Load Google Sheets configuration from secrets
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
    
    # First row - labels and inputs
    col1, col2 = st.columns(2)
    
    with col1:
        full_name = st.text_input("Full Name *", placeholder="Enter your full name", key="full_name")
    
    with col2:
        employee_id = st.text_input("Employee ID *", placeholder="Enter your employee ID", key="employee_id")
    
    # Second row - email
    st.markdown("Email *")
    col_email, col_domain = st.columns([4, 2])
    with col_email:
        email_username = st.text_input("Email username", placeholder="username", key="email_username", label_visibility="collapsed")
    with col_domain:
        email_domain = st.selectbox(
            "Email domain",
            options=["@ajg.com", "@penunderwriting.com", "@artexrisk.com", "@rpsins.com", "@GallagherRe.com"],
            key="email_domain",
            label_visibility="collapsed"
        )
    email_id = email_username + email_domain if email_username else ""
    
    st.markdown("---")
    
    # SECTION 1: Awards with 2 nominations (one from each YOE group)
    st.header("🎖️ Section 1: Awards with YOE-Based Nominations")
    st.markdown("*Each award requires 2 nominations: one from <1.5 YOE and one from >1.5 YOE*")
    st.markdown("---")
    
    answers_section_1 = []
    for i, (award_name, description) in enumerate(AWARDS_SECTION_1.items()):
        st.subheader(f"🏅 {award_name}")
        st.markdown(f"*{description}*")
        
        col1, col2 = st.columns(2)
        
        # Dropdown for <1.5 YOE
        with col1:
            key_less = f"sec1_less_{i}"
            current_value_less = st.session_state.get(key_less, "Select...")
            available_less = get_available_people(PEOPLE_LESS_THAN_1_5_YOE, key_less, current_value_less, section=1)
            options_less = ["Select..."] + available_less
            
            if current_value_less and current_value_less != "Select..." and current_value_less not in options_less:
                options_less.append(current_value_less)
            
            try:
                default_index_less = options_less.index(current_value_less) if current_value_less in options_less else 0
            except ValueError:
                default_index_less = 0
            
            selected_less = st.selectbox(
                "Nominate from <1.5 YOE *",
                options=options_less,
                key=key_less,
                index=default_index_less
            )
            
            answers_section_1.append(selected_less if selected_less != "Select..." else "")
        
        # Dropdown for >1.5 YOE
        with col2:
            key_more = f"sec1_more_{i}"
            current_value_more = st.session_state.get(key_more, "Select...")
            available_more = get_available_people(PEOPLE_MORE_THAN_1_5_YOE, key_more, current_value_more, section=1)
            options_more = ["Select..."] + available_more
            
            if current_value_more and current_value_more != "Select..." and current_value_more not in options_more:
                options_more.append(current_value_more)
            
            try:
                default_index_more = options_more.index(current_value_more) if current_value_more in options_more else 0
            except ValueError:
                default_index_more = 0
            
            selected_more = st.selectbox(
                "Nominate from >1.5 YOE *",
                options=options_more,
                key=key_more,
                index=default_index_more
            )
            
            answers_section_1.append(selected_more if selected_more != "Select..." else "")
        
        st.markdown("---")
    
    # SECTION 2: Awards with 1 nomination (anyone)
    st.header("🎯 Section 2: Awards with Open Nominations")
    st.markdown("*Each award requires 1 nomination from anyone*")
    st.markdown("---")
    
    answers_section_2 = []
    for i, (award_name, description) in enumerate(AWARDS_SECTION_2.items()):
        st.subheader(f"🏅 {award_name}")
        st.markdown(f"*{description}*")
        
        key = f"sec2_{i}"
        current_value = st.session_state.get(key, "Select...")
        available_all = get_available_people(ALL_PEOPLE, key, current_value, section=2)
        options_all = ["Select..."] + available_all
        
        if current_value and current_value != "Select..." and current_value not in options_all:
            options_all.append(current_value)
        
        try:
            default_index = options_all.index(current_value) if current_value in options_all else 0
        except ValueError:
            default_index = 0
        
        selected = st.selectbox(
            "Nominate *",
            options=options_all,
            key=key,
            index=default_index
        )
        
        answers_section_2.append(selected if selected != "Select..." else "")
        st.markdown("---")
    
    # Display nomination summary
    with st.expander("📊 Your Nominations Summary", expanded=False):
        # Section 1 Summary
        st.markdown("#### 🎖️ Section 1: YOE-Based Awards")
        
        sec1_data = []
        for i, (award_name, description) in enumerate(AWARDS_SECTION_1.items()):
            key_less = f"sec1_less_{i}"
            key_more = f"sec1_more_{i}"
            
            nominee_less = st.session_state.get(key_less, "Select...")
            nominee_more = st.session_state.get(key_more, "Select...")
            
            less_display = nominee_less if nominee_less != "Select..." else "—"
            more_display = nominee_more if nominee_more != "Select..." else "—"
            
            sec1_data.append({
                "Award": award_name,
                "<1.5 YOE": less_display,
                ">1.5 YOE": more_display
            })
        
        if sec1_data:
            import pandas as pd
            df_sec1 = pd.DataFrame(sec1_data)
            st.dataframe(df_sec1, use_container_width=True, hide_index=True)
        else:
            st.write("*No nominations yet*")
        
        st.markdown("---")
        
        # Section 2 Summary
        st.markdown("#### 🎯 Section 2: Open Awards")
        
        sec2_data = []
        for i, (award_name, description) in enumerate(AWARDS_SECTION_2.items()):
            key = f"sec2_{i}"
            nominee = st.session_state.get(key, "Select...")
            
            nominee_display = nominee if nominee != "Select..." else "—"
            
            sec2_data.append({
                "Award": award_name,
                "Nominee": nominee_display
            })
        
        if sec2_data:
            import pandas as pd
            df_sec2 = pd.DataFrame(sec2_data)
            st.dataframe(df_sec2, use_container_width=True, hide_index=True)
        else:
            st.write("*No nominations yet*")
    
    # Submit button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        submit_button = st.button(
            "Submit Form" if not st.session_state['form_submitted'] else "Already Submitted ✓",
            type="primary",
            use_container_width=True,
            disabled=st.session_state['form_submitted']
        )
    
    if submit_button:
        # Validation
        errors = []
        
        if not full_name or not full_name.strip():
            errors.append("Full Name is required")
        
        if not employee_id or not employee_id.strip():
            errors.append("Employee ID is required")
        
        if not email_username or not email_username.strip():
            errors.append("Email is required")
        elif "@" in email_username:
            errors.append("Email username should not contain @ symbol. Please use only the username part.")
        
        # Check Section 1 answers (all pairs must be answered)
        for i in range(len(AWARDS_SECTION_1)):
            less_idx = i * 2
            more_idx = i * 2 + 1
            
            if not answers_section_1[less_idx]:
                errors.append(f"Section 1, Award {i+1}: <1.5 YOE nomination is required")
            if not answers_section_1[more_idx]:
                errors.append(f"Section 1, Award {i+1}: >1.5 YOE nomination is required")
        
        # Check Section 2 answers
        for i, answer in enumerate(answers_section_2):
            if not answer:
                errors.append(f"Section 2, Award {i+1} is required")
        
        if errors:
            st.error("Please fix the following errors:")
            for error in errors:
                st.error(f"• {error}")
        else:
            if not credentials_json:
                st.error("Please configure Google Sheets credentials")
            else:
                with st.spinner("Submitting form..."):
                    client = connect_to_google_sheets(credentials_json)
                    
                    if client:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        data = [timestamp, full_name, employee_id, email_id] + answers_section_1 + answers_section_2
                        
                        if submit_to_google_sheets(client, spreadsheet_name, worksheet_name, data):
                            st.session_state['form_submitted'] = True
                            st.session_state['show_success'] = True
                            st.rerun()
                        else:
                            st.error("❌ Failed to submit form. Please try again.")

if __name__ == "__main__":
    main()