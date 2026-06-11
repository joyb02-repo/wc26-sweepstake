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

st.markdown("<div style='text-align: center; font-size: 40px; font-weight: bold; color: white; margin-bottom: 10px;'>2026 World Cup Sweepstake</div>", unsafe_allow_html=True)
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
    # --- UNIVERSAL STYLING FOR FORM ELEMENTS & BUTTONS ---
    st.markdown(
        """
        <style>
            /* Make text input fields smaller and more compact */
            div[data-testid="stTextInput"] input {
                padding: 6px 10px !important;
                height: 38px !important;
                font-size: 14px !important;
            }

            /* Shrink password visibility eye icon container and snap right */
            div[data-testid="stTextInput"] button[aria-label="View password text"] {
                transform: scale(0.75) !important;
                right: 0px !important;
                top: 2px !important;
                background: transparent !important;
            }
            
            /* Completely wipe the "Press Enter to submit" prompt */
            div[data-testid="InputInstructions"] {
                display: none !important;
            }

            /* Custom Styling for the Container Form area */
            .custom-form-container {
                background-color: rgba(255, 255, 255, 0.03) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
                padding: 20px 24px !important;
                margin-top: -8px; /* Tightly couples form underneath header */
            }

            /* Style white label text explicitly */
            .custom-form-container label p {
                color: #ffffff !important;
                font-size: 14px !important;
                font-weight: 500 !important;
            }
        </style>
        """, 
        unsafe_allow_html=True
    )

    # Maintain expander toggle state completely native using query parameters
    is_open = st.query_params.get("expanded", "false") == "true"
    toggle_label = "🔽 Click here to enter your PIN & draw a team!" if is_open else "👋 Click here to enter your PIN & draw a team!"

    # 1. CRISP INVERTED, LARGE, PERFECTLY CENTERED HEADER BAR BUTTON
    if st.button(toggle_label, use_container_width=True, type="secondary"):
        st.query_params["expanded"] = "false" if is_open else "true"
        st.rerun()

    # Injecting precise button styling properties directly onto the wrapper
    st.markdown(
        """
        <style>
            /* Force secondary action buttons to adapt light inverse styles */
            div.element-container button[kind="secondary"] {
                background-color: #f8f9fa !important;
                color: #111111 !important;
                border: 1px solid #e0e0e0 !important;
                border-radius: 8px !important;
                font-size: 26px !important; /* Prominent clean large text */
                font-weight: 700 !important;
                padding: 0.75rem 1rem !important;
                text-align: center !important;
                display: block !important;
            }
            div.element-container button[kind="secondary"]:hover {
                background-color: #eaeaea !important;
                border-color: #cccccc !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 2. RENDER THE DARK SECTION CONTAINER IF OPENED
    if is_open:
        st.markdown('<div class="custom-form-container">', unsafe_allow_html=True)
        
        with st.form(key="sweepstake_form", clear_on_submit=False):
            # Dynamic side-by-side arrangement
            form_col1, form_col2 = st.columns([1.2, 1])
            
            with form_col1:
                user_name = st.text_input("Enter Your Full Name:", placeholder="e.g., Jane Doe", max_chars=22).strip()
            with form_col2:
                user_pin = st.text_input("Enter Your Unique 5-Digit PIN:", type="password", placeholder="xxxxx", max_chars=5).strip()
                
            st.write("")
            
            # Form submission layouts
            btn_space1, btn_space2, btn_space3 = st.columns([1, 1.5, 1])
            with btn_space2:
                submit_button = st.form_submit_button(label="Verify & Draw My Country!", use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

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
                                st.query_params["expanded"] = "false"
                                st.rerun()
                            except Exception:
                                st.error("Submission failed. Connection issue.")
else:
    st.info("🎉 All 48 countries have been claimed!")

# --- SCOREBOARD VIEW ---
st.write("---")
st.markdown("<h3 style='text-align: center;'>Live Sweepstake Scoreboard</h3>", unsafe_allow_html=True)
st.write("")

m_col1, m_col2, m_col3, m_col4 = st.columns([1, 2, 2, 1])

with m_col2:
    st.markdown(
        f"""
        <div style="text-align: center; background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px;">
            <p style="font-size: 14px; margin-bottom: 5px; color: gray;">Countries Remaining</p>
            <span style="font-size: 32px; font-weight: bold; color: #ff4b4b; display: block; margin-top: 5px;">{remaining_count} / 48</span>
        </div>
        """, 
        unsafe_allow_html=True
    )

with m_col3:
    st.markdown(
        f"""
        <div style="text-align: center; background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px;">
            <p style="font-size: 14px; margin-bottom: 5px; color: gray;">Total Confirmed Entries</p>
            <span style="font-size: 32px; font-weight: bold; color: #29b5e8; display: block; margin-top: 5px;">{len(allocated_df)}</span>
        </div>
        """, 
        unsafe_allow_html=True
    )

st.write("")
st.write("")

c_btn1, c_btn2, c_btn3 = st.columns([2, 1, 2])
with c_btn2:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

st.write("")

# --- STYLED LIVE DATA TABLE WITH CUSTOM HIGH-VIS SCROLLBAR ---
table_head = """<style>
/* Custom Light Shade Webkit Scrollbar Configuration */
::-webkit-scrollbar {
    width: 10px !important;
    height: 10px !important;
}
::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05) !important;
    border-radius: 10px !important;
}
::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.4) !important; 
    border: 2px solid rgba(0, 0, 0, 0.2) !important;
    border-radius: 10px !important;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.6) !important;
}

.sweepstake-table {width: 100%; border-collapse: collapse; margin-top: 15px; font-family: sans-serif;}
.sweepstake-table th {background-color: rgba(255, 255, 255, 0.08); color: #ffffff !important; text-align: center; padding: 14px; font-weight: 600; font-size: 15px; border-bottom: 2px solid rgba(255, 255, 255, 0.15);}
.sweepstake-table td {padding: 16px; text-align: center; vertical-align: middle !important; border-bottom: 1px solid rgba(255, 255, 255, 0.05);}
.emoji-cell {font-size: 38px; line-height: 1; display: inline-block; vertical-align: middle;}
.status-available {color: #888888; font-style: italic;}
.status-owned {font-weight: bold; color: #29b5e8;}
.row-taken {background-color: rgba(255, 75, 75, 0.12) !important;} 
</style>
<table class="sweepstake-table">
<thead>
    <tr>
        <th style="width: 12%;">Flag</th>
        <th style="width: 25%;">Country</th>
        <th style="width: 13%;">Rating</th>
        <th style="width: 25%;">Star Player</th>
        <th style="width: 25%;">Owner Account</th>
    </tr>
</thead>
<tbody>"""

table_rows = ""
for _, row in df_teams.iterrows():
    country = row['Country']
    emoji = row['Emoji']
    owner = row['StakeHolder']
    
    rating = str(row.get('Rating', '')).replace('nan', '').strip()
    star_player = str(row.get('Star Player', '')).replace('nan', '').strip()
    
    if not star_player:
        star_player = "-"
    if not rating:
        rating = "-"

    row_class = "class='row-taken'" if owner != "" else ""

    if owner == "":
        owner_display = "<span class='status-available'>⏳ Available</span>"
    else:
        owner_display = f"<span class='status-owned'>👤 {owner}</span>"
        
    table_rows += f"""<tr {row_class}>
        <td><span class='emoji-cell'>{emoji}</span></td>
        <td style='font-size: 16px; font-weight: 500; color: white;'>{country}</td>
        <td style='font-size: 15px; color: #ffbf00; font-weight: bold;'>{rating}</td>
        <td style='font-size: 13px; color: #cccccc;'>{star_player}</td>
        <td style='font-size: 16px;'>{owner_display}</td>
    </tr>"""

table_foot = "</tbody></table>"
complete_table_html = table_head + table_rows + table_foot
st.components.v1.html(complete_table_html, height=700, scrolling=True)
