import streamlit as st
import pandas as pd
import urllib.parse
import urllib.request
import random
import time
import re

# Page config
st.set_page_config(page_title="2026 World Cup Sweepstake", page_icon="⚽", layout="centered")

# --- CENTERING THE LOGO ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("wclogo.png", use_container_width=True)
    except Exception:
        st.write("") 

st.markdown("<h1 style='text-align: center;'>2026 World Cup Sweepstake</h1>", unsafe_allow_html=True)
st.write("") 

# --- USER CONFIGURATION ---
SPREADSHEET_ID = "17PNVdOezXPwPmhV3vM1uWmeKsY9lJhFHKM3mBCyUJqU"
FORM_ID = "1FAIpQLScZsUCEPlh6YqzhGTb5JfLNA_oNeb6wGksMejlrMlWnjPUYoQ"

ENTRY_ACTION = "entry.1179688956"  
ENTRY_ROW = "entry.870831797"     
ENTRY_VALUE = "entry.931377367"    
# -----------------------------------------------------------

# Read data anonymously using basic web endpoints
try:
    url_teams = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet1"
    url_pins = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Pins"
    
    df_teams = pd.read_csv(url_teams)
    df_pins = pd.read_csv(url_pins)
except Exception:
    st.error("Failed to extract data. Double check that your Sheet settings are set to 'Anyone with the link can view'.")
    st.stop()

df_teams.columns = df_teams.columns.str.strip()
df_pins.columns = df_pins.columns.str.strip()

df_teams['StakeHolder'] = df_teams['StakeHolder'].fillna("").astype(str).str.strip()
df_pins['PIN'] = df_pins['PIN'].astype(str).str.strip()
df_pins['Status'] = df_pins['Status'].fillna("Active").astype(str).str.strip()

allocated_df = df_teams[df_teams['StakeHolder'] != ""]
remaining_count = 48 - len(allocated_df)

if remaining_count > 0:
    # --- STYLED COLLAPSED HEADER (INVERSE COLORS) ---
    st.markdown(
        """
        <style>
            /* 1. Target the collapsed header bar only (Light background) */
            div[data-testid="stExpander"] button {
                background-color: #f8f9fa !important;
                border: 1px solid #e0e0e0 !important;
                border-radius: 8px !important;
                padding: 0.5rem 1rem !important;
                transition: background-color 0.2s ease;
            }
            
            /* Hover effect for the header button */
            div[data-testid="stExpander"] button:hover {
                background-color: #eaeaea !important;
            }

            /* 2. Make the text and the small arrow icon dark inside the header */
            div[data-testid="stExpander"] button p, 
            div[data-testid="stExpander"] button svg {
                color: #111111 !important;
                fill: #111111 !important;
            }
            
            /* Boost the font size and weight of the header text */
            div[data-testid="stExpander"] button p {
                font-size: 19px !important;
                font-weight: 600 !important;
            }

            /* 3. Keep the expanded interior details box dark as original */
            div[data-testid="stExpanderDetails"] {
                background-color: rgba(255, 255, 255, 0.03) !important;
                color: #ffffff !important;
                border-bottom-left-radius: 8px !important;
                border-bottom-right-radius: 8px !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-top: none !important; /* Seamless connection to the light header */
                padding: 20px !important;
            }

            /* Ensure labels inside the form remain white */
            div[data-testid="stExpanderDetails"] label p {
                color: #ffffff !important;
            }
            
            /* Clean up the form container borders */
            div[data-testid="stExpanderDetails"] div[data-testid="stForm"] {
                border: none !important;
                background: transparent !important;
                padding: 0px !important;
            }
        </style>
        """, 
        unsafe_allow_html=True
    )
    
    with st.expander("👋 Click here to enter your PIN & draw a team!", expanded=False):
        with st.form(key="sweepstake_form", clear_on_submit=True):
            user_name = st.text_input("Enter Your Full Name:", placeholder="e.g., Jane Doe").strip()
            user_pin = st.text_input("Enter Your Unique 5-Digit PIN:", type="password", placeholder="xxxxx").strip()
            submit_button = st.form_submit_button(label="Verify & Draw My Country!")

        if submit_button:
            if not user_name or not user_pin:
                st.warning("Please fill out both details.")
            else:
                # --- COUNT-BASED MAXIMUM CHECK (UP TO 5) ---
                existing_draws = df_teams[df_teams['StakeHolder'].str.lower() == user_name.lower()]
                draw_count = len(existing_draws)
                
                if draw_count >= 5:
                    drawn_countries = ", ".join([f"{row['Emoji']} {row['Country']}" for _, row in existing_draws.iterrows()])
                    st.error(f"🚨 **{user_name}**, you have reached the maximum limit of 5 entries! You already own: {drawn_countries}")
                else:
                    pin_match = df_pins[df_pins['PIN'] == user_pin]
                    
                    if pin_match.empty:
                        st.error("❌ Invalid PIN.")
                    elif pin_match.iloc[0]['Status'] == "Used":
                        st.error("❌ This PIN has already been used!")
                    else:
                        available_teams = df_teams[df_teams['StakeHolder'] == ""]
                        
                        if not available_teams.empty:
                            chosen_team_row = available_teams.sample(n=1)
                            chosen_country = chosen_team_row['Country'].values[0]
                            chosen_emoji = chosen_team_row['Emoji'].values[0]
                            
                            team_sheet_row = int(chosen_team_row.index[0]) + 2
                            pin_sheet_row = int(pin_match.index[0]) + 2
                            
                            # Animation Sequence
                            animation_placeholder = st.empty()
                            all_emojis = df_teams['Emoji'].tolist()
                            for i in range(25):
                                animation_placeholder.markdown(f"<h1 style='text-align: center; font-size: 100px;'>{random.choice(all_emojis)}</h1>", unsafe_allow_html=True)
                                time.sleep(0.04 + (i * 0.01))
                            
                            animation_placeholder.markdown(f"<h1 style='text-align: center; font-size: 120px;'>{chosen_emoji}</h1>", unsafe_allow_html=True)
                            
                            form_url = f"https://docs.google.com/forms/d/e/{FORM_ID}/formResponse"
                            
                            try:
                                # 1. Update Team Allocation
                                data_team = {ENTRY_ACTION: "CLAIM_TEAM", ENTRY_ROW: str(team_sheet_row), ENTRY_VALUE: user_name}
                                req_team = urllib.request.Request(form_url, data=urllib.parse.urlencode(data_team).encode())
                                urllib.request.urlopen(req_team)
                                
                                # 2. Burn PIN
                                data_pin = {ENTRY_ACTION: "USE_PIN", ENTRY_ROW: str(pin_sheet_row), ENTRY_VALUE: "Used"}
                                req_pin = urllib.request.Request(form_url, data=urllib.parse.urlencode(data_pin).encode())
                                urllib.request.urlopen(req_pin)
                                
                                st.balloons()
                                st.success(f"🎉 **Congratulations {user_name}!** (Draw {draw_count + 1}/5)")
                                st.subheader(f"Your country: **{chosen_country}**")
                                time.sleep(4)
                                st.rerun()
                            except Exception:
                                st.error("Submission failed. Connection issue.")
else:
    st.info("🎉 All 48 countries have been claimed!")
