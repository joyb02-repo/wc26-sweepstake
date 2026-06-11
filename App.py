import streamlit as st
import pandas as pd
import urllib.parse
import urllib.request
import random
import time
import re

# Page config
st.set_page_config(page_title="2026 World Cup Sweepstake", page_icon="icon.png", layout="centered")

# --- FORCE DARK MODE GLOBALLY ---
st.markdown(
    """
    <script>
        window.localStorage.setItem('stLocalStorageSyncv1-theme', '{"theme":"dark"}');
    </script>
    <style>
        :root {
            --st-theme-primary: #ff4b4b;
            --st-theme-backgroundColor: #0e1117;
            --st-theme-secondaryBackgroundColor: #262730;
            --st-theme-textColor: #fafafa;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- CENTERING THE LOGO ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("wclogo.png", use_container_width=True)
    except Exception:
        st.write("") 

# --- TITLE WITHOUT MARKDOWN HOVER ANCHORS ---
st.markdown("<div style='text-align: center; font-size: 40px; font-weight: bold; color: white; margin-bottom: 25px;'>2026 World Cup Sweepstake</div>", unsafe_allow_html=True)


# --- 1. RULES DROP-DOWN ---
st.markdown(
    """
    <style>
        .rules-dropdown {
            background-color: #1a1c23;
            border: 1px solid #2d3139;
            border-radius: 6px;
            margin-bottom: 5px;
            font-family: sans-serif;
        }
        .rules-dropdown summary {
            padding: 10px 15px;
            font-size: 14px;
            color: #8a92a6;
            cursor: pointer;
            font-weight: 500;
            user-select: none;
            outline: none;
        }
        .rules-dropdown summary:hover {
            color: #cccccc;
        }
        .rules-content {
            padding: 15px 20px;
            font-size: 14px;
            color: #e0e0e0;
            border-top: 1px solid #2d3139;
            line-height: 1.6;
        }
        .rules-content ul {
            margin: 0;
            padding-left: 20px;
        }
        .rules-content li {
            margin-bottom: 8px;
        }
    </style>
    
    <details class="rules-dropdown">
        <summary>ℹ️ How the Sweepstake Works (Rules & Entry Details)</summary>
        <div class="rules-content">
            <p>Welcome to the <strong>2026 World Cup Sweepstake</strong>! Here is everything you need to know to get started:</p>
            <ul>
                <li><strong>Entry Fee:</strong> Join the sweepstake by paying <strong>$5 per entry</strong> via cash or PayID to <strong>benjoy@up.me</strong>.</li>
                <li><strong>Prize Pool:</strong> 100% of the entry fees go directly into the competitive prize pool.</li>
                <li><strong>Entry Limit:</strong> You can purchase a <strong>maximum of 5 entries</strong> per person.</li>
                <li><strong>How to Draw:</strong> For each entry paid, you will receive a <strong>unique 5-digit PIN</strong>. Enter your PIN below to trigger the automated shuffling system and draw a random country.</li>
                <li><strong>Exclusivity:</strong> Once you draw a country, it is permanently allocated to you and locked so no other player can claim it.</li>
                <li><strong>Winning the Pool:</strong> If your allocated country wins the World Cup final on <strong>July 20th</strong>, you take home the <strong>entire cash prize pool</strong>!</li>
                <li><strong>The Safety Net:</strong> If the tournament is won by a country that was left unassigned/undrawn by the end of the sweepstake, <strong>all entry fees will be fully refunded</strong> to the players.</li>
            </ul>
            <p style="margin-top: 10px; font-style: italic; color: #aaa;">Good luck! Ensure your entry fees are sent before drawing your team.</p>
        </div>
    </details>
    """,
    unsafe_allow_html=True
)


# --- SECURE USER CONFIGURATION VIA STREAMLIT SECRETS ---
SPREADSHEET_ID = st.secrets["SPREADSHEET_ID"]
FORM_ID = st.secrets["FORM_ID"]

ENTRY_ACTION = st.secrets["ENTRY_ACTION"]  
ENTRY_ROW = st.secrets["ENTRY_ROW"]     
ENTRY_VALUE = st.secrets["ENTRY_VALUE"]    
# -----------------------------------------------------------

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
    # --- EXPANDER & FORM STYLE INJECTION ---
    st.markdown(
        """
        <style>
            /* Hide every single native hover anchor link on the screen globally */
            a { display: none !important; }
            .stMarkdown a, button a, div[data-testid="stMarkdownContainer"] a { display: none !important; }
            svg.css-6q9sum, svg.e1tzwq550, .st-emotion-cache-b698xo a { display: none !important; }

            /* --- REMOVE EXPANDER OUTLINE STROKES & NATIVE BORDERS --- */
            div[data-testid="stExpander"], 
            div[data-testid="stExpander"] * {
                border: none !important;
                border-color: transparent !important;
                box-shadow: none !important;
                outline: none !important;
            }
            
            div[data-testid="stExpanderDetails"] {
                padding-left: 0px !important;
                padding-right: 0px !important;
            }

            /* --- TARGET AND REMOVE THE PERSISTENT NATIVE FORM CONTAINER BORDER --- */
            div[data-testid="stForm"] {
                border: none !important;
                box-shadow: none !important;
                padding: 10px 0px 0px 0px !important;
            }

            /* --- THE BIG WHITE CONTAINER BUTTON (RESPONSIVE) --- */
            div[data-testid="stExpander"] summary {
                background-color: #ffffff !important;
                border: none !important;
                outline: none !important;
                border-radius: 12px !important;
                padding: 8px 16px !important; 
                min-height: 70px !important; 
                height: auto !important; 
                
                display: flex !important;
                justify-content: center !important; 
                align-items: center !important;
                position: relative !important;
                box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.15) !important;
                transition: background-color 0.25s ease !important;
            }

            /* Completely wipe out native icons/chevron layouts */
            div[data-testid="stExpander"] summary svg,
            div[data-testid="stExpander"] summary [data-testid="stExpanderToggleIcon"] {
                display: none !important;
            }

            /* Strip absolute positions on inner structural div blocks */
            div[data-testid="stExpander"] summary > div {
                position: relative !important;
                left: unset !important;
                right: unset !important;
                top: unset !important;
                bottom: unset !important;
                display: flex !important;
                justify-content: center !important;
                align-items: center !important;
                width: 100% !important;
                max-width: 100% !important;
                margin: 0px !important;
                padding: 0px !important;
            }
            
            div[data-testid="stExpander"] summary > div > div {
                display: flex !important;
                justify-content: center !important;
                align-items: center !important;
                width: 100% !important;
            }

            /* Fluid Typography Header Row Formatting */
            div[data-testid="stExpander"] summary p,
            div[data-testid="stExpander"] summary span {
                font-size: clamp(15px, 4.5vw, 22px) !important; 
                font-weight: 800 !important;
                color: #111111 !important;
                margin: 0px !important;
                padding: 0px !important;
                text-align: center !important; 
                white-space: normal !important; 
                word-wrap: break-word !important;
                display: inline-block !important;
                width: auto !important;
                transition: color 0.25s ease !important;
            }

            /* --- HOVER INTERACTION --- */
            div[data-testid="stExpander"] summary:hover {
                background-color: #e6c619 !important; /* Light Golden */
                cursor: pointer;
            }
            
            div[data-testid="stExpander"] summary:hover p,
            div[data-testid="stExpander"] summary:hover span {
                color: #ffffff !important;
            }
            
            div[data-testid="InputInstructions"] {
                display: none !important;
            }

            /* Responsive tweaks for form field blocks */
            @media (max-width: 640px) {
                div[data-testid="stForm"] {
                    padding: 5px 0px !important;
                }
                div[data-testid="element-container"] {
                    width: 100% !important;
                }
            }

            /* Submission Form Button Elements */
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
                box-shadow: none !important;
                transition: background-color 0.2s ease, border-color 0.2s ease !important;
                width: auto !important;
            }

            @media (max-width: 480px) {
                div[data-testid="stForm"] button[kind="primary"],
                div[data-testid="stForm"] button[type="submit"],
                .stFormSubmitButton > button {
                    width: 100% !important;
                }
            }

            div[data-testid="stForm"] button[kind="primary"]:hover,
            div[data-testid="stForm"] button[type="submit"]:hover,
            .stFormSubmitButton > button:hover {
                background-color: #218838 !important; 
                border-color: #1e7e34 !important;
                color: #ffffff !important;
            }
        </style>
        """, 
        unsafe_allow_html=True
    )
    
    # --- THE BIG DRAW EXPANDER ---
    with st.expander("👋 Click here to enter your PIN & draw a team! ▾", expanded=False):
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
                            
                            animation_placeholder = st.empty()
                            all_emojis = df_teams['Emoji'].tolist()
                            for i in range(25):
                                animation_placeholder.markdown(f"<div style='text-align: center; font-size: 100px;'>{random.choice(all_emojis)}</div>", unsafe_allow_html=True)
                                time.sleep(0.04 + (i * 0.01))
                            
                            animation_placeholder.markdown(f"<div style='text-align: center; font-size: 120px;'>{chosen_emoji}</div>", unsafe_allow_html=True)
                            
                            form_url = f"https://docs.google.com/forms/d/e/{FORM_ID}/formResponse"
                            
                            try:
                                data_team = {ENTRY_ACTION: "CLAIM_TEAM", ENTRY_ROW: str(team_sheet_row), ENTRY_VALUE: user_name}
                                req_team = urllib.request.Request(form_url, data=urllib.parse.urlencode(data_team).encode())
                                urllib.request.urlopen(req_team)
                                
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

# --- TABLE VIEW ---
table_head = """<style>
::-webkit-scrollbar { width: 10px !important; height: 10px !important; }
::-webkit-scrollbar-track { background: rgba(255, 255, 255, 0.05) !important; border-radius: 10px !important; }
::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.4) !important; border: 2px solid rgba(0, 0, 0, 0.2) !important; border-radius: 10px !important; }
::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.6) !important; }

.sweepstake-table {width: 100%; border-collapse: collapse; margin-top: 15px; font-family: sans-serif;}
.sweepstake-table th {background-color: rgba(255, 255, 255, 0.08); color: #ffffff !important; text-align: center; padding: 14px; font-weight: 600; font-size: 15px; border-bottom: 2px solid rgba(255, 255, 255, 0.15);}
.sweepstake-table td {padding: 16px; text-align: center; vertical-align: middle !important; border-bottom: 1px solid rgba(255, 255, 255, 0.05);}
.emoji-cell {font-size: 38px; line-height: 1; display: inline-block; vertical-align: middle;}
.status-available {color: #a8ffb2; font-weight: 500;} 
.status-owned {font-weight: bold; color: #29b5e8;}
.owner-cell {font-size: 13px !important;} 
.row-taken {background-color: rgba(255, 75, 75, 0.12) !important;} 
.row-available {background-color: rgba(40, 167, 69, 0.12) !important;} 
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
    
    if not star_player: star_player = "-"
    if not rating: rating = "-"

    if owner == "":
        row_class = "class='row-available'"
        owner_display = "<span class='status-available'>⏳ Available</span>"
    else:
        row_class = "class='row-taken'"
        owner_display = f"<span class='status-owned'>👤 {owner}</span>"
        
    table_rows += f"""<tr {row_class}>
        <td><span class='emoji-cell'>{emoji}</span></td>
        <td style='font-size: 16px; font-weight: 500; color: white;'>{country}</td>
        <td style='font-size: 15px; color: #ffbf00; font-weight: bold;'>{rating}</td>
        <td style='font-size: 13px; color: #cccccc;'>{star_player}</td>
        <td class='owner-cell'>{owner_display}</td>
    </tr>"""

table_foot = "</tbody></table>"
complete_table_html = table_head + table_rows + table_foot
st.components.v1.html(complete_table_html, height=700, scrolling=True)
