import streamlit as st
import pandas as pd
import gspread
import random
import time
import re

st.set_page_config(page_title="2026 World Cup Sweepstake", page_icon="⚽", layout="centered")
st.title("⚽ 2026 World Cup Sweepstake")

# 1. Extract Spreadsheet ID from your Streamlit Secrets URL
try:
    secret_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    # Regular expression to safely grab the unique ID between /d/ and /edit
    sheet_id = re.search(r"/d/([a-zA-Z0-9-_]+)", secret_url).group(1)
except Exception:
    st.error("Missing or malformed Google Sheet URL in Streamlit Advanced Secrets!")
    st.stop()

# 2. Connect to Google Sheets anonymously using the public edit link
try:
    gc = gspread.public_api_client()
    sh = gc.open_by_key(sheet_id)
    
    # Open both individual worksheets
    worksheet_teams = sh.worksheet("Sheet1")
    worksheet_pins = sh.worksheet("Pins")
    
    # Read data into Pandas DataFrames
    df_teams = pd.DataFrame(worksheet_teams.get_all_records())
    df_pins = pd.DataFrame(worksheet_pins.get_all_records())
except Exception as e:
    st.error("Failed to connect to Google Sheets. Double-check that your spreadsheet's Share settings are set to 'Anyone with the link can EDIT'.")
    st.stop()

# Clean up column data strings
df_teams.columns = df_teams.columns.str.strip()
df_pins.columns = df_pins.columns.str.strip()

df_teams['StakeHolder'] = df_teams['StakeHolder'].fillna("").astype(str).str.strip()
df_pins['PIN'] = df_pins['PIN'].astype(str).str.strip()
df_pins['Status'] = df_pins['Status'].fillna("Active").astype(str).str.strip()

# Calculate statistics
allocated_df = df_teams[df_teams['StakeHolder'] != ""]
remaining_count = 48 - len(allocated_df)

# --- EXPANDABLE REGISTRATION PORTAL ---
if remaining_count > 0:
    with st.expander("👋 Paid your $5? Click here to enter your PIN & Draw!", expanded=False):
        with st.form(key="sweepstake_form", clear_on_submit=True):
            user_name = st.text_input("Enter Your Full Name:", placeholder="e.g., Jane Doe").strip()
            user_pin = st.text_input("Enter Your Unique 4-Digit PIN:", type="password", placeholder="xxxx").strip()
            submit_button = st.form_submit_button(label="🎲 Verify & Draw My Country!")

        if submit_button:
            if not user_name or not user_pin:
                st.warning("Please fill out both your name and your unique security PIN.")
            elif user_name.lower() in [name.lower() for name in df_teams['StakeHolder'].values]:
                already_drawn = df_teams[df_teams['StakeHolder'].str.lower() == user_name.lower()].iloc[0]
                st.error(f"🚨 {user_name}, you have already drawn: {already_drawn['Emoji']} **{already_drawn['Country']}**!")
            else:
                # Target pin lookup row
                pin_match = df_pins[df_pins['PIN'] == user_pin]
                
                if pin_match.empty:
                    st.error("❌ Invalid PIN. Please check your credentials or contact the administrator.")
                elif pin_match.iloc[0]['Status'] == "Used":
                    st.error("❌ This PIN has already been used for a draw!")
                else:
                    available_teams = df_teams[df_teams['StakeHolder'] == ""]
                    
                    if available_teams.empty:
                        st.info("🎉 All countries have been allocated!")
                    else:
                        # Lock in choice
                        chosen_team_row = available_teams.sample(n=1)
                        chosen_country = chosen_team_row['Country'].values[0]
                        chosen_emoji = chosen_team_row['Emoji'].values[0]
                        
                        # Calculate exact Google Sheets row offsets (Index 0 is Row 2 in Sheet)
                        team_sheet_row = int(chosen_team_row.index[0]) + 2
                        pin_sheet_row = int(pin_match.index[0]) + 2
                        
                        # Run Shuffling Animation
                        animation_placeholder = st.empty()
                        all_emojis = df_teams['Emoji'].tolist()
                        
                        st.write("🎰 *Validating security token and shuffling teams...*")
                        for i in range(25): 
                            random_emoji = random.choice(all_emojis)
                            animation_placeholder.markdown(
                                f"<h1 style='text-align: center; font-size: 100px;'>{random_emoji}</h1>", 
                                unsafe_allow_html=True
                            )
                            time.sleep(0.04 + (i * 0.01)) 
                        
                        animation_placeholder.markdown(
                            f"<h1 style='text-align: center; font-size: 120px;'>{chosen_emoji}</h1>", 
                            unsafe_allow_html=True
                        )
                        
                        # Write directly to specific cells in Google Sheets
                        try:
                            # Update Stakeholder in Sheet1 (Column C is 3)
                            worksheet_teams.update_cell(team_sheet_row, 3, user_name)
                            # Update PIN status in Pins (Column B is 2)
                            worksheet_pins.update_cell(pin_sheet_row, 2, "Used")
                            
                            st.balloons()
                            st.success(f"🎉 **Congratulations {user_name}!**")
                            st.subheader(f"Your official drawn country is: **{chosen_country}**")
                            time.sleep(3)
                            st.rerun()
                        except Exception as write_error:
                            st.error("Database sync issue. Please try again.")
else:
    st.info("🎉 All 48 countries have been claimed! Check the final tournament dashboard below.")

# --- LIVE METRICS AND SCOREBOARD ---
st.write("---")
st.subheader("📊 Live Sweepstake Scoreboard")

col1, col2 = st.columns(2)
col1.metric(label="Countries Remaining", value=f"{remaining_count} / 48")
col2.metric(label="Total Confirmed Entries", value=len(allocated_df))

if st.button("🔄 Refresh Standings"):
    st.rerun()

display_df = df_teams[['Country', 'Emoji', 'StakeHolder']].copy()
display_df['StakeHolder'] = display_df['StakeHolder'].apply(lambda x: "⏳ Available" if x == "" else x)

st.dataframe(
    display_df,
    column_config={
        "Country": st.column_config.TextColumn("Country Qualified"),
        "Emoji": st.column_config.TextColumn("Flag", width="small"),
        "StakeHolder": st.column_config.TextColumn("Owner Account")
    },
    use_container_width=True,
    hide_index=True,
    height=550
)
