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
    with st.expander("👋 Click here to enter your PIN & draw a team!", expanded=False):
        with st.form(key="sweepstake_form", clear_on_submit=True):
            user_name = st.text_input("Enter Your Full Name:", placeholder="e.g., Jane Doe").strip()
            user_pin = st.text_input("Enter Your Unique 5-Digit PIN:", type="password", placeholder="xxxx").strip()
            submit_button = st.form_submit_button(label="Verify & Draw My Country!")

        if submit_button:
            if not user_name or not user_pin:
                st.warning("Please fill out both details.")
            else:
                # --- NEW COUNT-BASED MAXIMUM CHECK ---
                # Check how many times this specific name appears in the sheet (case-insensitive)
                existing_draws = df_teams[df_teams['StakeHolder'].str.lower() == user_name.lower()]
                draw_count = len(existing_draws)
                
                if draw_count >= 5:
                    drawn_countries = ", ".join([f"{row['Emoji']} {row['Country']}" for _, row in existing_draws.iterrows()])
                    st.error(f"🚨 **{user_name}**, you have reached the maximum limit of 5 entries! You already own: {drawn_countries}")
                else:
                    # Target pin lookup row
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
                            
                            # Trigger Form Submissions to update the sheets via Web Requests
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

# --- SCOREBOARD VIEW ---
st.write("---")
st.markdown("<h3 style='text-align: center;'>Live Sweepstake Scoreboard</h3>", unsafe_allow_html=True)
st.write("")

m_col1, m_col2, m_col3, m_col4 = st.columns([1, 2, 2, 1])

with m_col2:
    st.markdown(
        f"""
        <div style="text-align: center; background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px;">
            <p style="font-size: 14px; margin-bottom: 0px; color: gray;">Countries Remaining</p>
            <h2 style="margin-top: 0px; font-size: 32px; color: #ff4b4b;">{remaining_count} / 48</h2>
        </div>
        """, 
        unsafe_allow_html=True
    )

with m_col3:
    st.markdown(
        f"""
        <div style="text-align: center; background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px;">
            <p style="font-size: 14px; margin-bottom: 0px; color: gray;">Total Confirmed Entries</p>
            <h2 style="margin-top: 0px; font-size: 32px; color: #29b5e8;">{len(allocated_df)}</h2>
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

# --- STYLED LIVE DATA TABLE ---
table_head = """<style>
.sweepstake-table {width: 100%; border-collapse: collapse; margin-top: 15px; font-family: sans-serif;}
.sweepstake-table th {background-color: rgba(255, 255, 255, 0.08); color: #ffffff !important; text-align: center; padding: 14px; font-weight: 600; font-size: 15px; border-bottom: 2px solid rgba(255, 255, 255, 0.15);}
.sweepstake-table td {padding: 16px; text-align: center; vertical-align: middle !important; border-bottom: 1px solid rgba(255, 255, 255, 0.05);}
.emoji-cell {font-size: 38px; line-height: 1; display: inline-block; vertical-align: middle;}
.status-available {color: #888888; font-style: italic;}
.status-owned {font-weight: bold; color: #29b5e8;}
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
    
    # Extract the new columns from your Google Sheet data frame safely
    # Using .get() or fillna ensures the app doesn't crash if a row is missing data
    rating = str(row.get('Rating', '')).replace('nan', '').strip()
    star_player = str(row.get('Star Player', '')).replace('nan', '').strip()
    
    # Handle fallbacks for empty rows
    if not star_player:
        star_player = "-"
    if not rating:
        rating = "-"

    if owner == "":
        owner_display = "<span class='status-available'>⏳ Available</span>"
    else:
        owner_display = f"<span class='status-owned'>👤 {owner}</span>"
        
    # Append the row with the two new cells injected in the middle
    table_rows += f"""<tr>
        <td><span class='emoji-cell'>{emoji}</span></td>
        <td style='font-size: 16px; font-weight: 500; color: white;'>{country}</td>
        <td style='font-size: 15px; color: #ffbf00; font-weight: bold;'>{rating}</td>
        <td style='font-size: 15px; color: #ffffff;'>⭐ {star_player}</td>
        <td style='font-size: 16px;'>{owner_display}</td>
    </tr>"""

table_foot = "</tbody></table>"

# Assemble the pieces seamlessly
complete_table_html = table_head + table_rows + table_foot

# Render inside the sandboxed HTML component to keep formatting locked in
st.components.v1.html(complete_table_html, height=700, scrolling=True)
