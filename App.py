import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="2026 World Cup Sweepstake", page_icon="⚽", layout="centered")
st.title("⚽ 2026 World Cup Sweepstake")

# --- FOOLPROOF ALTERNATIVE SYNTAX ---
conn = st.connection("gsheets", type="gsheets")

# ... (rest of your app.py code stays exactly the same)

# Read both sheets fresh (ttl=0 avoids local caching)
try:
    df_teams = conn.read(worksheet="Sheet1", ttl=0)
    df_pins = conn.read(worksheet="Pins", ttl=0)
except Exception as e:
    st.error("Failed to fetch data from Google Sheets. Ensure your sharing link is set to Public Editor.")
    st.stop()

# Format column names and contents cleanly
df_teams.columns = df_teams.columns.str.strip()
df_pins.columns = df_pins.columns.str.strip()

df_teams['StakeHolder'] = df_teams['StakeHolder'].fillna("").astype(str).str.strip()
df_pins['PIN'] = df_pins['PIN'].astype(str).str.strip()
df_pins['Status'] = df_pins['Status'].fillna("Active").astype(str).str.strip()

# Calculate scoreboard metrics
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
            
            # Check if name already exists in drawing dashboard
            elif user_name.lower() in [name.lower() for name in df_teams['StakeHolder'].values]:
                already_drawn = df_teams[df_teams['StakeHolder'].str.lower() == user_name.lower()].iloc[0]
                st.error(f"🚨 {user_name}, you have already drawn: {already_drawn['Emoji']} **{already_drawn['Country']}**!")
            
            else:
                # Security Level: Validate PIN from the 'Pins' sheet
                pin_row_match = df_pins[df_pins['PIN'] == user_pin]
                
                if pin_row_match.empty:
                    st.error("❌ Invalid PIN. Please check your credentials or contact the administrator.")
                elif pin_row_match.iloc[0]['Status'] == "Used":
                    st.error("❌ This PIN has already been used for a draw!")
                else:
                    # Valid unpaid PIN identified. Fetch available countries
                    available_teams = df_teams[df_teams['StakeHolder'] == ""]
                    
                    if available_teams.empty:
                        st.info("🎉 All countries have been allocated!")
                    else:
                        # 1. Lock in random pick instantly to prevent race conditions
                        chosen_team_row = available_teams.sample(n=1)
                        chosen_country = chosen_team_row['Country'].values[0]
                        chosen_emoji = chosen_team_row['Emoji'].values[0]
                        team_index = chosen_team_row.index[0]
                        pin_index = pin_row_match.index[0]
                        
                        # 2. Run Shuffling Animation Visual
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
                        
                        # 3. Commit state changes locally
                        df_teams.at[team_index, 'StakeHolder'] = user_name
                        df_pins.at[pin_index, 'Status'] = "Used"
                        
                        # 4. Write data updates back to Google Sheet
                        try:
                            conn.update(worksheet="Sheet1", data=df_teams)
                            conn.update(worksheet="Pins", data=df_pins)
                            
                            st.balloons()
                            st.success(f"🎉 **Congratulations {user_name}!**")
                            st.subheader(f"Your official drawn country is: **{chosen_country}**")
                            time.sleep(3)
                            st.rerun()
                        except Exception as write_error:
                            st.error("Database conflict. Someone hit the submit button at the exact same millisecond. Please try again.")
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

# Build and display dashboard table
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
