import streamlit as st
import pandas as pd
import urllib.parse
import urllib.request
import random
import time
import base64
import os

# Page config
st.set_page_config(page_title="2026 World Cup Sweepstake", page_icon="icon.png", layout="centered")

# Initialize session state for our custom toggle button
if "show_draw_form" not in st.session_state:
    st.session_state.show_draw_form = False

# --- FORCE DARK MODE BY DEFAULT ---
st.markdown(
    """
    <script>
        if (!window.localStorage.getItem('stLocalStorageSyncv1-theme')) {
            window.localStorage.setItem('stLocalStorageSyncv1-theme', '{"theme":"dark"}');
        }
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

# --- SAFE BASE64 IMAGE PROCESSING FOR THE UNIFIED HEADER ---
try:
    possible_paths = ["wclogo.png", "app/static/wclogo.png", "static/wclogo.png"]
    found_path = None
    for path in possible_paths:
        if os.path.exists(path):
            found_path = path
            break
            
    if found_path:
        with open(found_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center; align-items: center; width: 100%; margin-bottom: 12px;">
                <img src="data:image/png;base64,{encoded_string}" style="width: 35vw; max-width: 220px; min-width: 110px; height: auto;">
            </div>
            """,
            unsafe_allow_html=True
        )
except Exception:
    pass

# --- RENDER THE LOCKED TITLE VIA ADAPTIVE CSS VARIABLE ---
st.markdown(
    """
    <style>
        .adaptive-title {
            font-size: clamp(20px, 5.2vw, 40px); 
            font-weight: bold; 
            color: #ffffff; /* Default Dark Mode */
            text-align: center;
            white-space: nowrap !important;
            overflow: hidden;
            text-overflow: ellipsis;
            width: 100%;
        }
        /* Light Mode Text Override */
        @media (prefers-color-scheme: light) {
            .adaptive-title {
                color: #111111 !important;
            }
        }
    </style>
    <div style="display: flex; justify-content: center; align-items: center; width: 100%; margin-bottom: 25px; box-sizing: border-box;">
        <div class="adaptive-title">2026 World Cup Sweepstake</div>
    </div>
    """,
    unsafe_allow_html=True
)


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
        .rules-content ul { margin: 0; padding-left: 20px; }
        .rules-content li { margin-bottom: 8px; }

        /* Light Mode Rules Tweaks */
        @media (prefers-color-scheme: light) {
            .rules-dropdown {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
            }
            .rules-dropdown summary { color: #495057; }
            .rules-dropdown summary:hover { color: #000000; }
            .rules-content {
                color: #212529;
                border-top: 1px solid #dee2e6;
            }
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
    # --- BULLETPROOF NATIVE OVERRIDES FOR THE MAIN DRAW BUTTON ---
    st.markdown(
        """
        <style>
            a { display: none !important; }
            .stMarkdown a, button a, div[data-testid="stMarkdownContainer"] a { display: none !important; }
            
            /* --- FORM CONTAINER --- */
            div[data-testid="stForm"] {
                border: 1px solid #2d3139 !important;
                border-radius: 12px !important;
                box-shadow: none !important;
                padding: 20px !important;
                background-color: #11141a !important;
                margin-top: 15px !important;
            }
            div[data-testid="InputInstructions"] { display: none !important; }

            /* ========================================================
               FORCE STREAMLIT'S NATIVE BUTTON TO BE BIG AND WHITE
               ======================================================== */
            /* Force layout blocks to break open to 100% full width */
            div[data-testid="stMainBlockContainer"] div[data-testid="stButton"],
            div[data-testid="stMainBlockContainer"] div[data-testid="stButton"] button {
                width: 100% !important;
                max-width: 100% !important;
                display: block !important;
            }

            /* Style the button directly */
            div[data-testid="stButton"] button:not([type="submit"]) {
                background-color: #ffffff !important;
                border: 1px solid #dee2e6 !important;
                border-radius: 12px !important;
                padding: 14px 20px !important; 
                min-height: 74px !important;
                height: auto !important;
                box-shadow: 0px 4px 14px rgba(0, 0, 0, 0.18) !important;
                transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease !important;
            }

            /* Style the text inside the button */
            div[data-testid="stButton"] button:not([type="submit"]) p {
                font-size: clamp(16px, 4.6vw, 22px) !important; 
                font-weight: 800 !important;
                color: #111111 !important;
                text-align: center !important;
                line-height: 1.3 !important;
                margin: 0px !important;
            }

            /* Hover states */
            div[data-testid="stButton"] button:not([type="submit"]):hover {
                background-color: #e6c619 !important;
                border-color: #e6c619 !important;
            }
            div[data-testid="stButton"] button:not([type="submit"]):hover p {
                color: #ffffff !important;
            }

            /* Submit Button Configuration inside the form */
            div[data-testid="stForm"] button[type="submit"], .stFormSubmitButton > button {
                font-size: 15px !important; font-weight: 600 !important;
                padding: 0.5rem 2.5rem !important; 
                background-color: #28a745 !important; color: #ffffff !important;
                border: 1px solid #218838 !important; border-radius: 6px !important;
                width: auto !important; min-height: unset !important;
            }
            div[data-testid="stForm"] button[type="submit"] p, .stFormSubmitButton > button p {
                color: #ffffff !important; font-size: 15px !important; font-weight: 600 !important;
            }

            @media (prefers-color-scheme: light) {
                div[data-testid="stForm"] {
                    background-color: #fdfdfd !important;
                    border: 1px solid #ced4da !important;
                }
            }
            @media (max-width: 480px) {
                div[data-testid="stForm"] button[type="submit"], .stFormSubmitButton > button { width: 100% !important; }
            }
        </style>
        """, 
        unsafe_allow_html=True
    )
    
    # Clean native streamlit execution path
    if st.button("👋 Click here to enter your PIN & draw a team!"):
        st.session_state.show_draw_form = not st.session_state.show_draw_form
        st.rerun()

    if st.session_state.show_draw_form:
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
        <div style="text-align: center; background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1);">
            <p style="font-size: 14px; margin-bottom: 5px; color: gray;">Countries Remaining</p>
            <span style="font-size: 32px; font-weight: bold; color: #ff4b4b; display: block; margin-top: 5px;">{remaining_count} / 48</span>
        </div>
        """, 
        unsafe_allow_html=True
    )

with m_col3:
    st.markdown(
        f"""
        <div style="text-align: center; background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1);">
            <p style="font-size: 14px; margin-bottom: 5px; color: gray;">Total Confirmed Entries</p>
            <span style="font-size: 32px; font-weight: bold; color: #29b5e8; display: block; margin-top: 5px;">{len(allocated_df)}</span>
        </div>
        """, 
        unsafe_allow_html=True
    )

st.write("")

# --- PERFECT UNTOUCHED CENTERED REFRESH COMPONENT ---
st.components.v1.html(
    """
    <style>
        body {
            margin: 0; padding: 0;
            background: transparent;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100%;
            overflow: hidden;
            font-family: system-ui, -apple-system, sans-serif;
        }
        .refresh-btn {
            background-color: #1f232b;
            border: 1px solid #343a46;
            color: #a0aec0;
            border-radius: 6px;
            padding: 0 18px;
            height: 34px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease;
            outline: none;
            user-select: none;
        }
        .refresh-btn:hover {
            background-color: #2d333f;
            color: #fafafa;
            border-color: #4a5568;
        }
        @media (prefers-color-scheme: light) {
            .refresh-btn {
                background-color: #f1f3f5;
                border: 1px solid #ced4da;
                color: #495057;
            }
            .refresh-btn:hover {
                background-color: #e9ecef;
                color: #111111;
                border-color: #adb5bd;
            }
        }
    </style>
    <button class="refresh-btn" onclick="window.parent.location.reload();">
        <span>🔄</span> Refresh Data
    </button>
    """,
    height=45
)

st.write("")

# --- BULLETPROOF FIXED HEADERS VIA IN-VIEW SCROLL WRAPPER ---
table_head = """<style>
html, body { 
    margin: 0; padding: 0; 
    background-color: transparent; 
    font-family: sans-serif; 
    overflow: hidden; 
}

.table-container { 
    width: 100%; 
    height: 98vh; 
    overflow-y: auto !important; 
    overflow-x: hidden; 
    box-sizing: border-box; 
    position: relative;
}

.sweepstake-table { 
    width: 100%; 
    border-collapse: collapse; 
    margin-top: 0px; 
    table-layout: auto; 
}

.sweepstake-table thead th {
    position: sticky !important;
    top: 0px !important;
    z-index: 999 !important;
    background-color: #0e1117 !important; 
    color: #ffffff !important;
    text-align: center;
    padding: 12px 6px;
    font-weight: 600;
    font-size: 13px;
    border-bottom: 2px solid rgba(255, 255, 255, 0.15);
    white-space: nowrap;
}

.sweepstake-table td { padding: 10px 4px; text-align: center; vertical-align: middle !important; border-bottom: 1px solid rgba(255, 255, 255, 0.05); box-sizing: border-box; }
.emoji-cell { font-size: 26px; line-height: 1; display: inline-block; vertical-align: middle; }

.country-text { font-size: 14px; font-weight: 500; color: white; }
.player-text { font-size: 12px; color: #cccccc; }

.status-available { color: #a8ffb2; font-weight: 500; font-size: 12px; } 
.status-owned { font-weight: bold; color: #29b5e8; font-size: 12px; word-break: break-word; }
.row-taken { background-color: rgba(255, 75, 75, 0.12) !important; } 
.row-available { background-color: rgba(40, 167, 69, 0.12) !important; } 

/* --- ADAPTIVE LIGHT MODE ANCHORS --- */
@media (prefers-color-scheme: light) {
    .sweepstake-table thead th { 
        background-color: #f8f9fa !important; 
        color: #111111 !important; 
        border-bottom: 2px solid #ced4da !important;
    }
    .sweepstake-table td { 
        border-bottom: 1px solid #dee2e6 !important; 
    }
    .country-text { color: #111111 !important; }
    .player-text { color: #495057 !important; }
    
    .row-taken { background-color: #f8d7da !important; }
    .row-available { background-color: #d1e7dd !important; }
    
    .status-available { color: #0f5132 !important; }
    .status-owned { color: #0b5ed7 !important; }
}

@media (max-width: 480px) {
    .sweepstake-table th { font-size: 11px; padding: 10px 4px; }
    .sweepstake-table td { font-size: 12px; padding: 8px 2px; }
    .emoji-cell { font-size: 22px; }
    .hide-mobile { display: none !important; }
}
</style>
<div class="table-container">
<table class="sweepstake-table">
<thead>
    <tr>
        <th style="width: 10%;">Flag</th>
        <th>Country</th>
        <th style="width: 12%;">Rating</th>
        <th class="hide-mobile">Star Player</th>
        <th style="width: 30%;">Owner Account</th>
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
        <td class='country-text'>{country}</td>
        <td style='font-size: 14px; color: #ffbf00; font-weight: bold;'>{rating}</td>
        <td class="hide-mobile player-text">{star_player}</td>
        <td>{owner_display}</td>
    </tr>"""

table_foot = "</tbody></table></div>"
complete_table_html = table_head + table_rows + table_foot
st.components.v1.html(complete_table_html, height=720, scrolling=False)
