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

# Employee ID to Name mapping - REPLACE THIS WITH YOUR ACTUAL DATA
EMPLOYEE_ID_TO_NAME = {
    "G14174": "Nivita Shetty",
    "G14312": "Neal Shah",
    "G14330": "Sneha Banerjee",
    "G14340": "Prachi Thakkar",
    "G14404": "Nehal Bajaj",
    "G14426": "Muskan Jhunjhunwala",
    "G15884": "Saanchi Bathla",
    "G16130": "Krisha Dedhia",
    "G19514": "Simoni Jain",
    "G19767": "Megha Bansal",
    "G20008": "Ritika Jalan",
    "G21147": "Aakash Sethia",
    "G21048": "Durgesh Singh",
    "G26093": "Abhishhek Patil",
    "G14209": "Vidur Bhatnagar",
    "G14269": "Rhea Christie Anthonyraj",
    "G17106": "Jainee Satra",
    "G19788": "Devesh Newatia",
    "G21598": "Divijaa Talwar",
    "G22645": "Mohammad Masbah Khan",
    "G23865": "Karan Agarwal",
    "G26519": "Dimple Thanvi",
    "G14310": "Nishita Kikani",
    "G21830": "Janvee Shah",
    "G20379": "Akshiti Vohra",
    "G21200": "Raunak Makhija",
    "G21469": "Krishu Agrawal",
    "G22699": "Amisha Khetan",
    "G23279": "Vinayak Karnawat",
    "G26179": "Aman Nirmal",
    "G26432": "Yuvrajsingh Rajpurohit",
    "G13710": "Yerra Haritha",
    "G23453": "Aditya Padia",
    "G23926": "Mihir Furiya",
    "G24978": "Bhavana Sharma",
    "G25335": "Samia Malik",
    "G27570": "Vidhi Shah",
    "G27786": "Sejal Suri",
    "G27854": "Smit Mistry",
    "G27413": "Het Ghelani",
    "G27924": "Nishtha Thakkar",
    "G28031": "Pakshal Mody",
    "G28258": "Arya Raheja",
    "G28346": "Rounak Bachwani",
    "G29193": "Vidhi Maheshwari",
    "G29440": "Husein Katwarawala",
    "G29048": "Omkar Chavan",
    "G29399": "Shriram Dayama",
    "G29866": "Rajnandini Gupta",
    "G30220": "Aayushi Lunia",
    "G30202": "Ritika Nair",
    "G30589": "Priyansi Sheth",
    "G30986": "Avanti Joshi"
}

# Employee lists based on YOE (sorted alphabetically)
PEOPLE_LESS_THAN_1_5_YOE = sorted([
    "Abhishhek Patil", "Karan Agarwal", "Dimple Thanvi", "Aman Nirmal",
    "Yuvrajsingh Rajpurohit", "Mihir Furiya", "Bhavana Sharma", "Samia Malik",
    "Vidhi Shah", "Sejal Suri", "Smit Mistry", "Het Ghelani",
    "Nishtha Thakkar", "Pakshal Mody", "Arya Raheja", "Rounak Bachwani",
    "Vidhi Maheshwari", "Husein Katwarawala", "Omkar Chavan", "Shriram Dayama",
    "Rajnandini Gupta", "Aayushi Lunia", "Ritika Nair", "Priyansi Sheth", "Avanti Joshi"
])

PEOPLE_MORE_THAN_1_5_YOE = sorted([
    "Nivita Shetty", "Neal Shah", "Sneha Banerjee", "Prachi Thakkar",
    "Nehal Bajaj", "Muskan Jhunjhunwala", "Saanchi Bathla", "Krisha Dedhia",
    "Simoni Jain", "Megha Bansal", "Ritika Jalan", "Aakash Sethia",
    "Durgesh Singh", "Vidur Bhatnagar", "Rhea Christie Anthonyraj", "Jainee Satra",
    "Devesh Newatia", "Divijaa Talwar", "Mohammad Masbah Khan", "Nishita Kikani",
    "Janvee Shah", "Akshiti Vohra", "Raunak Makhija", "Krishu Agrawal",
    "Amisha Khetan", "Vinayak Karnawat", "Yerra Haritha", "Aditya Padia"
])

# All people combined for tracking nominations
ALL_PEOPLE = sorted(PEOPLE_LESS_THAN_1_5_YOE + PEOPLE_MORE_THAN_1_5_YOE)

# Awards for Section 1 (2 nominations: one from each YOE group)
AWARDS_SECTION_1 = {
    "Just a Chill Guy/Girl": "Aag lagi basti mei, yeh rahe masti mei.",
    "ChatterBox": "The podcast without a mic.",
    "Human Serotonin": "Golden retreiver energy.",
    "Human Stack Overflow": "For the legend who replies in solutions, thinks in code.",
    "Sassy Comeback": "Mic drop master. Savage one liners.",
    "Silent Killer": "Less talks, more impact.",
    "Bade Miyan Chote Miyan": "Office ki iconic jodi—Bade Miyan ki calm aur Chote Miyan ki charm, dono saath ho toh kaam bhi hota hai aur comedy bhi!" 
}

# Awards for Section 2 (1 nomination: anyone from any group)
AWARDS_SECTION_2 = {
    "High on Caffeine": "Always ready. Always charged.",
    "IT Issues": "Kaam toh full josh mein karne ka hai, bas IT issues har dusre din brake laga dete hain.",
    "Digital Ghost": "Nazar kamm ata hai, but kahani sab jaanta hai.",
    "No Filter, Full Volume": "Dil mein jo aata hai, woh zabaan par...bina kisi filter ke.",
    "Jack of All": "Google se bhi zyada gyaan.",
    "Too Pure for this World": "Ekdum innocent seedha sa thoda naive baccha.",
    "Overqualified for Seedha Life": "Jalebi jitna seedha.",
    "Self-Appreciation": "Likely to laugh at their own jokes.",
    "Karam to Kaand": "Starts with good intention...but somehow always ends in chaos.",
    "Jugaadu": "If there is a problem, this person will find a workaround no matter what."
}

def get_all_selections():
    """Get all current selections from both sections"""
    selections = []
    
    # Section 1: Get both <1.5 and >1.5 selections for each award
    for i in range(len(AWARDS_SECTION_1)):
        key_less = f"sec1_less_{i}"
        key_more = f"sec1_more_{i}"
        
        value_less = st.session_state.get(key_less, "Select...")
        value_more = st.session_state.get(key_more, "Select...")
        
        if value_less and value_less != "Select...":
            selections.append(value_less)
        if value_more and value_more != "Select...":
            selections.append(value_more)
    
    # Section 2: Get single selection for each award
    for i in range(len(AWARDS_SECTION_2)):
        key = f"sec2_{i}"
        value = st.session_state.get(key, "Select...")
        if value and value != "Select...":
            selections.append(value)
    
    return selections

def get_global_nomination_count():
    """Get count of nominations for each person across ALL sections"""
    all_selections = get_all_selections()
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
                headers = ["Timestamp", "Employee ID", "Full Name"]
                
                # Section 1 headers (2 columns per award)
                for award_name in AWARDS_SECTION_1.keys():
                    headers.append(f"{award_name} (<=1.5 Tenure)")
                    headers.append(f"{award_name} (>1.5 Tenure)")
                
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
    
    st.title("🏆 Gremmy's 2026 Awards Nomination Form")
    
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
    
    # Personal Information Section - Only Employee ID
    st.header("👤 Personal Information")
    
    employee_id = st.text_input("Employee ID * (case-sensitive)", placeholder="Enter your employee ID", key="employee_id")
    
    # Look up and display full name
    if employee_id and employee_id.strip():
        full_name = EMPLOYEE_ID_TO_NAME.get(employee_id.strip(), "")
        if full_name:
            st.markdown(f"*{full_name}*")
        else:
            st.warning("⚠️ Employee ID not found. Please check and try again.")
    else:
        full_name = ""
    
    st.markdown("---")
    
    # SECTION 1: Awards with 2 nominations (one from each YOE group)
    st.header("🎖️ Section 1: Awards with Tenure-Based Nominations")
    st.markdown("*Each award requires 2 nominations: one from <=1.5 Tenure and one from >1.5 Tenure, in Gallagher*")
    st.markdown("---")
    
    # Get current nomination counts
    nomination_count = get_global_nomination_count()
    
    answers_section_1 = []
    for i, (award_name, description) in enumerate(AWARDS_SECTION_1.items()):
        st.subheader(f"🏅 {award_name}")
        st.markdown(f"*{description}*")
        
        col1, col2 = st.columns(2)
        
        # Dropdown for <1.5 YOE
        with col1:
            key_less = f"sec1_less_{i}"
            current_value_less = st.session_state.get(key_less, "Select...")
            
            options_less = ["Select..."] + PEOPLE_LESS_THAN_1_5_YOE
            
            try:
                default_index_less = options_less.index(current_value_less) if current_value_less in options_less else 0
            except ValueError:
                default_index_less = 0
            
            selected_less = st.selectbox(
                "Nominate from <=1.5 Tenure *",
                options=options_less,
                key=key_less,
                index=default_index_less
            )
            
            # Check if person has been nominated 2 times
            if selected_less and selected_less != "Select...":
                count = nomination_count.get(selected_less, 0)
                # Don't count current selection
                if current_value_less == selected_less:
                    count = count - 1 if count > 0 else 0
                
                if count >= 2:
                    st.warning(f"⚠️ {selected_less} has already been nominated 2 times. Please choose another.")
            
            answers_section_1.append(selected_less if selected_less != "Select..." else "")
        
        # Dropdown for >1.5 YOE
        with col2:
            key_more = f"sec1_more_{i}"
            current_value_more = st.session_state.get(key_more, "Select...")
            
            options_more = ["Select..."] + PEOPLE_MORE_THAN_1_5_YOE
            
            try:
                default_index_more = options_more.index(current_value_more) if current_value_more in options_more else 0
            except ValueError:
                default_index_more = 0
            
            selected_more = st.selectbox(
                "Nominate from >1.5 Tenure *",
                options=options_more,
                key=key_more,
                index=default_index_more
            )
            
            # Check if person has been nominated 2 times
            if selected_more and selected_more != "Select...":
                count = nomination_count.get(selected_more, 0)
                # Don't count current selection
                if current_value_more == selected_more:
                    count = count - 1 if count > 0 else 0
                
                if count >= 2:
                    st.warning(f"⚠️ {selected_more} has already been nominated 2 times. Please choose another.")
            
            answers_section_1.append(selected_more if selected_more != "Select..." else "")
        
        st.markdown("---")
    
    # SECTION 2: Awards with 1 nomination (anyone)
    st.header("🎯 Section 2: Awards with Open Nominations")
    st.markdown("*Each award requires 1 nomination*")
    st.markdown("---")
    
    answers_section_2 = []
    for i, (award_name, description) in enumerate(AWARDS_SECTION_2.items()):
        st.subheader(f"🏅 {award_name}")
        st.markdown(f"*{description}*")
        
        key = f"sec2_{i}"
        current_value = st.session_state.get(key, "Select...")
        
        options_all = ["Select..."] + ALL_PEOPLE
        
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
        
        # Check if person has been nominated 2 times
        if selected and selected != "Select...":
            count = nomination_count.get(selected, 0)
            # Don't count current selection
            if current_value == selected:
                count = count - 1 if count > 0 else 0
            
            if count >= 2:
                st.warning(f"⚠️ {selected} has already been nominated 2 times. Please choose another.")
        
        answers_section_2.append(selected if selected != "Select..." else "")
        st.markdown("---")
    
    # Display nomination summary - ALWAYS VISIBLE (no expander)
    st.markdown("---")
    st.markdown("## 📊 Your Nominations Summary")
    
    # Section 1 Summary
    st.markdown("#### 🎖️ Section 1: Tenure-Based Awards")
    
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
            "<=1.5 Tenure": less_display,
            ">1.5 Tenure": more_display
        })
    
    if sec1_data:
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
        
        if not employee_id or not employee_id.strip():
            errors.append("Employee ID is required")
        elif not full_name:
            errors.append("Employee ID not found in system. Please check your Employee ID.")
        
        # Check Section 1 answers (all pairs must be answered)
        for i in range(len(AWARDS_SECTION_1)):
            less_idx = i * 2
            more_idx = i * 2 + 1
            
            if not answers_section_1[less_idx]:
                errors.append(f"Section 1, Award {i+1}: <=1.5 Tenure nomination is required")
            if not answers_section_1[more_idx]:
                errors.append(f"Section 1, Award {i+1}: >1.5 Tenure nomination is required")
        
        # Check Section 2 answers
        for i, answer in enumerate(answers_section_2):
            if not answer:
                errors.append(f"Section 2, Award {i+1} is required")
        
        # Check for over-nomination (more than 2 times)
        final_nomination_count = {}
        all_answers = answers_section_1 + answers_section_2
        for person in all_answers:
            if person:  # Skip empty selections
                final_nomination_count[person] = final_nomination_count.get(person, 0) + 1
        
        for person, count in final_nomination_count.items():
            if count > 2:
                errors.append(f"❌ {person} has been nominated {count} times. Maximum allowed is 2 nominations per person.")
        
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
                        data = [timestamp, employee_id, full_name] + answers_section_1 + answers_section_2
                        
                        if submit_to_google_sheets(client, spreadsheet_name, worksheet_name, data):
                            st.session_state['form_submitted'] = True
                            st.session_state['show_success'] = True
                            st.rerun()
                        else:
                            st.error("❌ Failed to submit form. Please try again.")

if __name__ == "__main__":
    main()
