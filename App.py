import streamlit as st
import pandas as pd
import urllib.parse
import urllib.request
import random
import time
import re

# Page config
st.set_page_config(page_title="2026 World Cup Sweepstake", page_icon="icon.png", layout="centered")

# --- CENTERING THE LOGO ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("wclogo.png", use_container_width=True)
    except Exception:
        st.write("") 

# --- TITLE WITHOUT MARKDOWN HOVER ANCHORS ---
st.markdown("<div style='text-align: center; font-size: 40px; font-weight: bold; color: white; margin-bottom: 25px;'>2026 World Cup Sweepstake</div>", unsafe_allow_html=True)

# --- CLEAN CUSTOM CSS INJECTION ---
st.markdown(
    """
    <style>
        /* ABSOLUTE FORCE: Hide native hover anchor links */
        a { display: none !important; }
        .stMarkdown a, button a, div[data-testid="stMarkdownContainer"] a { display: none !important; }
        svg.css-6q9sum, svg.e1tzwq550, .st-emotion-cache-b698xo a { display: none !important; }

        /* General Expander Styling (Centering text) */
        div[data-testid="stExpander"] summary {
            display: flex !important;
            justify-content: center !important; 
            align-items: center !important;
            border-radius: 8px !important;
        }

        /* --- FIRST EXPANDER (INFO TAB): Dark & Small --- */
        div[data-testid="stExpander"]:nth-of-type(1) summary {
            background-color: #1e1e1e !important; /* Dark Background */
            border: 1px solid #333333 !important;
            padding: 0.2rem 1rem !important; /* Smaller Padding */
            margin-bottom: 10px;
        }
        div[data-testid="stExpander"]:nth-of-type(1) summary p {
            font-size: 14px !important; /* Smaller Font */
            color: #ffffff !important; /* Light Text */
            font-weight: normal !important;
            margin: 0px !important;
        }
        div[data-testid="stExpander"]:nth-of-type(1) summary svg {
            fill: #ffffff !important; /* White arrow icon */
            width: 14px !important;
            height: 14px !important;
        }

        /* --- SECOND EXPANDER (DRAW TAB): Light & Large --- */
        div[data-testid="stExpander"]:nth-of-type(2) summary {
            background-color: #f8f9fa !important; /* Light Background */
            border: 1px solid #e0e0e0 !important;
            padding: 0.5rem 1rem !important; /* Larger Padding */
        }
        div[data-testid="stExpander"]:nth-of-type(2) summary p {
            font-size: 26px !important; /* Large Font */
            font-weight: bold !important;
            color: #111111 !important; /* Dark Text */
            margin: 0px !important;
        }
        div[data-testid="stExpander"]:nth-of-type(2) summary svg {
            fill: #111111 !important; /* Dark arrow icon */
        }

        /* --- FORM & BUTTON STYLING --- */
        div[data-testid="InputInstructions"] { display: none !important; }

        div[data-testid="stForm"] button[kind="primary"],
        div[data-testid="stForm"] button[type="submit"],
        .stFormSubmitButton > button {
            font-size: 15px !important; 
            font-weight: 600 !important;
            padding: 0.5rem 2.5rem !important; 
            background-color: #28a745 !important; 
            color: #ffffff !important;
            border: 1px solid #218838 !important;
            border-radius: 6px !important;
            transition: background-color 0.2s ease;
        }
        div[data-testid="stForm"] button:hover {
            background-color: #218838 !important; 
        }
    </style>
    """, 
    unsafe_allow_html=True
)

# --- NEW COLLAPSABLE INFORMATION TAB (First Expander) ---
with st.expander("ℹ️ How the Sweepstake Works (Rules & Entry Details)", expanded=False):
    st.markdown(
        """
        Welcome to the **2026 World Cup Sweepstake**! Here is everything you need to know to get started:
        
        * **Entry Fee:** Join the sweepstake by paying **$5 per entry** via cash or PayID to **benjoy@up.me**. 
        * **Prize Pool:** 100% of the entry fees go directly into the competitive prize pool.
        * **Entry Limit:** You can purchase a **maximum of 5 entries** per person.
        * **How to Draw:** For each entry paid, you will receive a **unique 5-digit PIN**. Enter your PIN below to trigger the automated shuffling system and draw a random country.
        * **Exclusivity:** Once you draw a country, it is permanently allocated to you and locked so no other player can claim it.
        * **Winning the Pool:** If your allocated country wins the World Cup final on **July 20th**, you take home the **entire cash prize pool**!
        * **The Safety Net:** If the tournament is won by a country that was left unassigned/undrawn by the end of the sweepstake, **all entry fees will be fully refunded** to the players.
        """
    )

st.write("")

# --- SECURE USER CONFIGURATION ---
SPREADSHEET_ID = st.secrets["SPREADSHEET_ID"]
FORM_ID = st.secrets["FORM_ID"]
ENTRY_ACTION = st.secrets["ENTRY_ACTION"]  
ENTRY_ROW = st.secrets["ENTRY_ROW"]     
ENTRY_VALUE = st.secrets["ENTRY_VALUE"]    

# Read data
try:
    url_teams = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet1"
    url_pins = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Pins"
    df_teams = pd.read_csv(url_teams)
    df_pins = pd.read_csv(url_pins)
except Exception:
    st.error("Failed to extract data.")
    st.stop()

df_teams.columns = df_teams.columns.str.strip()
df_pins.columns = df_pins.columns.str.strip()
df_teams['StakeHolder'] = df_teams['StakeHolder'].fillna("").astype(str).str.strip()
df_pins['PIN'] = df_pins['PIN'].astype(str).str.strip()
df_pins['Status'] = df_pins['Status'].fillna("Active").astype(str).str.strip()

allocated_df = df_teams[df_teams['StakeHolder'] != ""]
remaining_count = 48 - len(allocated_df)

if remaining_count > 0:
    # DRAW TAB (Second Expander)
    with st.expander("👋 Click here to enter your PIN & draw a team!", expanded=False):
        with st.form(key="sweepstake_form", clear_on_submit=False):
            form_col1, form_col2 = st.columns([1.2, 1])
            with form_col1:
                user_name = st.text_input("Enter Your Full Name:", placeholder="e.g., Jane Doe", max_chars=22).strip()
            with form_col2:
                user_pin = st.text_input("Enter Your Unique 5-Digit PIN:", type="password", placeholder="xxxxx", max_chars=5).strip()
            submit_button = st.form_submit_button(label="Verify & Draw My Country!")

        if submit_button:
            if not user_name or not user_pin:
                st.warning("Please fill out both details.")
            else:
                existing_draws = df_teams[df_teams['StakeHolder'].str.lower() == user_name.lower()]
                draw_count = len(existing_draws)
                if draw_count >= 5:
                    drawn_countries = ", ".join([f"{row['Emoji']} {row['Country']}" for _, row in existing_draws.iterrows()])
                    st.error(f"🚨 **{user_name}**, you have reached the maximum limit of 5 entries!")
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
                            
                            animation_placeholder = st.empty()
                            all_emojis = df_teams['Emoji'].tolist()
                            for i in range(25):
                                animation_placeholder.markdown(f"<div style='text-align: center; font-size: 100px;'>{random.choice(all_emojis)}</div>", unsafe_allow_html=True)
                                time.sleep(0.04 + (i * 0.01))
                            animation_placeholder.markdown(f"<div style='text-align: center; font-size: 120px;'>{chosen_emoji}</div>", unsafe_allow_html=True)
                            
                            form_url = f"https://docs.google.com/forms/d/e/{FORM_ID}/formResponse"
                            try:
                                data_team = {ENTRY_ACTION: "CLAIM_TEAM", ENTRY_ROW: str(team_sheet_row), ENTRY_VALUE: user_name}
                                urllib.request.urlopen(urllib.request.Request(form_url, data=urllib.parse.urlencode(data_team).encode()))
                                data_pin = {ENTRY_ACTION: "USE_PIN", ENTRY_ROW: str(pin_sheet_row), ENTRY_VALUE: "Used"}
                                urllib.request.urlopen(urllib.request.Request(form_url, data=urllib.parse.urlencode(data_pin).encode()))
                                st.balloons()
                                st.success(f"🎉 **Congratulations {user_name}!**")
                                st.subheader(f"Your country: **{chosen_country}**")
                                time.sleep(4)
                                st.rerun()
                            except Exception:
                                st.error("Submission failed.")
else:
    st.info("🎉 All 48 countries have been claimed!")

# --- SCOREBOARD VIEW ---
st.write("---")
st.markdown("<h3 style='text-align: center;'>Live Sweepstake Scoreboard</h3>", unsafe_allow_html=True)
st.write("")

m_col1, m_col2, m_col3, m_col4 = st.columns([1, 2, 2, 1])
with m_col2:
    st.markdown(f'<div style="text-align: center; background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px;"><p style="font-size: 14px; margin-bottom: 5px; color: gray;">Countries Remaining</p><span style="font-size: 32px; font-weight: bold; color: #ff4b4b; display: block; margin-top: 5px;">{remaining_count} / 48</span></div>', unsafe_allow_html=True)
with m_col3:
    st.markdown(f'<div style="text-align: center; background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px;"><p style="font-size: 14px; margin-bottom: 5px; color: gray;">Total Confirmed Entries</p><span style="font-size: 32px; font-weight: bold; color: #29b5e8; display: block; margin-top: 5px;">{len(allocated_df)}</span></div>', unsafe_allow_html=True)

st.write("")
if st.button("🔄 Refresh", use_container_width=True):
    st.rerun()

# --- TABLE VIEW ---
table_head = """<style>
::-webkit-scrollbar { width: 10px; }
::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.4); border-radius: 10px; }
.sweepstake-table {width: 100%; border-collapse: collapse; margin-top: 15px;}
.sweepstake-table th {background-color: rgba(255, 255, 255, 0.08); color: white; padding: 14px; font-size: 15px; border-bottom: 2px solid rgba(255, 255, 255, 0.15);}
.sweepstake-table td {padding: 16px; text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.05);}
.emoji-cell {font-size: 38px;}
.status-available {color: #a8ffb2; font-weight: 500;} 
.status-owned {font-weight: bold; color: #29b5e8;}
.owner-cell {font-size: 13px;} 
.row-taken {background-color: rgba(255, 75, 75, 0.12) !important;} 
.row-available {background-color: rgba(40, 167, 69, 0.12) !important;} 
</style>
<table class="sweepstake-table">
<thead><tr><th>Flag</th><th>Country</th><th>Rating</th><th>Star Player</th><th>Owner Account</th></tr></thead><tbody>"""

table_rows = ""
for _, row in df_teams.iterrows():
    rating = str(row.get('Rating', '')).replace('nan', '') or "-"
    star = str(row.get('Star Player', '')).replace('nan', '') or "-"
    if row['StakeHolder'] == "":
        r_cls, o_disp = "row-available", "<span class='status-available'>⏳ Available</span>"
    else:
        r_cls, o_disp = "row-taken", f"<span class='status-owned'>👤 {row['StakeHolder']}</span>"
    table_rows += f"<tr class='{r_cls}'><td><span class='emoji-cell'>{row['Emoji']}</span></td><td style='color: white;'>{row['Country']}</td><td style='color: #ffbf00; font-weight: bold;'>{rating}</td><td style='color: #cccccc; font-size: 13px;'>{star}</td><td class='owner-cell'>{o_disp}</td></tr>"

st.components.v1.html(table_head + table_rows + "</tbody></table>", height=700, scrolling=True)
