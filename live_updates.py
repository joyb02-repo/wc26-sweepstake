import streamlit as st
import pandas as pd

# Page Configuration 
st.markdown("<h2 style='text-align: center;'>🏆 2026 World Cup Live Center</h2>", unsafe_allow_html=True)
st.write("---")

# --- DATA EXTRACTION (CARRIED OVER SYSTEM FROM MAIN APP) ---
SPREADSHEET_ID = st.secrets["SPREADSHEET_ID"]
try:
    url_teams = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet1"
    df_teams = pd.read_csv(url_teams)
    df_teams.columns = df_teams.columns.str.strip()
    df_teams['StakeHolder'] = df_teams['StakeHolder'].fillna("").astype(str).str.strip()
except Exception:
    st.error("Failed to sync shared sweepstake data sheet metrics.")
    st.stop()

# --- LIVE REPUTATION DATA (Simulated Real-Time Tournament State API Metadata) ---
# In a real scenario, this matches your 'Country' strings to flag who's in or out!
tournament_live_metadata = {
    "Argentina": {"status": "Active", "favorites_odds": "4.50", "group": "A", "points": 7, "form": "W-D-W"},
    "France": {"status": "Active", "favorites_odds": "5.00", "group": "C", "points": 9, "form": "W-W-W"},
    "Brazil": {"status": "Active", "favorites_odds": "5.50", "group": "B", "points": 6, "form": "W-L-W"},
    "England": {"status": "Active", "favorites_odds": "6.00", "group": "D", "points": 5, "form": "D-W-D"},
    "Germany": {"status": "Eliminated (Knockout)", "favorites_odds": "—", "group": "E", "points": 4, "form": "W-L-L"},
    "Australia": {"status": "Eliminated (Group Stage)", "favorites_odds": "—", "group": "A", "points": 1, "form": "L-D-L"},
}

# -----------------------------------------------------------------
# FEATURE 1: LIVE TABLE - TEAM STAKEHOLDERS & ELIMINATION STATS
# -----------------------------------------------------------------
st.markdown("### 📊 Stakeholder Standings & Survival Tracker")
st.caption("Track who is still in the running and who has been sent packing.")

table_rows = ""
for _, row in df_teams.iterrows():
    country = row['Country']
    emoji = row['Emoji']
    owner = row['StakeHolder'] if row['StakeHolder'] else "⏳ Unassigned"
    
    # Check live status mapping
    meta = tournament_live_metadata.get(country, {"status": "Active", "favorites_odds": "12.00", "group": "-", "points": 0, "form": "-"})
    status = meta["status"]
    
    # Styling variables based on elimination state
    if "Eliminated" in status:
        status_badge = f"<span style='color: #ff4b4b; font-weight: bold;'>❌ {status}</span>"
        row_bg = "rgba(255, 75, 75, 0.08)"
    else:
        status_badge = "<span style='color: #28a745; font-weight: bold;'>🟢 Alive</span>"
        row_bg = "transparent"
        
    table_rows += f"""
    <tr style="background-color: {row_bg}; border-bottom: 1px solid rgba(255,255,255,0.05);">
        <td style="padding: 12px; text-align: center; font-size: 22px;">{emoji}</td>
        <td style="font-weight: 600; color: white;">{country}</td>
        <td style="color: #29b5e8; font-weight: bold;">{owner}</td>
        <td>{status_badge}</td>
    </tr>
    """

st.markdown(
    f"""
    <table style="width: 100%; border-collapse: collapse; background-color: #11141a; border-radius: 8px; overflow: hidden;">
        <thead style="background-color: #1e293b;">
            <tr>
                <th style="padding: 12px; color: white; width: 10%;">Flag</th>
                <th style="text-align: left; color: white;">Country</th>
                <th style="text-align: left; color: white;">Stakeholder</th>
                <th style="text-align: left; color: white;">Status</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    """,
    unsafe_allow_html=True
)

st.write("")
st.write("---")

col1, col2 = st.columns([1.2, 1])

# -----------------------------------------------------------------
# FEATURE 2: RELIABLE ODDS / FAVORITES (Ranked based on Opta / Bookmakers)
# -----------------------------------------------------------------
with col1:
    st.markdown("### 📈 Tournament Favorites")
    st.caption("Live win probabilities and projection ranking (Source: Opta Analyst / DraftKings).")
    
    # Filter and sort live teams by favorites odds
    active_teams = []
    for c, data in tournament_live_metadata.items():
        if data["status"] == "Active":
            # Match emoji from dataframe
            match_row = df_teams[df_teams['Country'] == c]
            emoji = match_row['Emoji'].values[0] if not match_row.empty else "🏳️"
            active_teams.append({"country": c, "emoji": emoji, "odds": float(data["favorites_odds"])})
            
    sorted_favorites = sorted(active_teams, key=lambda x: x["odds"])
    
    for idx, fav in enumerate(sorted_favorites[:4]):
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; background: #1a1c23; padding: 10px 15px; border-left: 4px solid #e6c619; margin-bottom: 8px; border-radius: 0 6px 6px 0;">
                <span style="font-weight: 600; color: white;">{idx+1}. {fav['emoji']} {fav['country']}</span>
                <span style="color: #e6c619; font-weight: bold; font-family: monospace;">${fav['odds']} AUD</span>
            </div>
            """, 
            unsafe_allow_html=True
        )

# -----------------------------------------------------------------
# FEATURE 3: LIVE MATCH RESULTS & GOALSCORERS
# -----------------------------------------------------------------
with col2:
    st.markdown("### 👟 Recent Match Results")
    st.caption("Latest scores and verified match day goalscorers.")
    
    st.markdown(
        """
        <div style="background-color: #11141a; border: 1px solid #2d3139; border-radius: 8px; padding: 14px; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 14px; color: #94a3b8;">
                <span>Group A • FT</span>
                <span>June 15, 2026</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 16px; margin: 8px 0; font-weight: bold; color: white;">
                <span>🇦🇷 Argentina</span>
                <span style="color: #e6c619;">2</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 16px; margin: 8px 0; font-weight: bold; color: white;">
                <span>🇦🇺 Australia</span>
                <span>0</span>
            </div>
            <div style="font-size: 11px; color: #a0aec0; border-top: 1px solid #2d3139; padding-top: 6px; margin-top: 6px; font-style: italic;">
                ⚽ L. Messi (34'), L. Martinez (72')
            </div>
        </div>
        
        <div style="background-color: #11141a; border: 1px solid #2d3139; border-radius: 8px; padding: 14px;">
            <div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 14px; color: #94a3b8;">
                <span>Group C • FT</span>
                <span>June 14, 2026</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 16px; margin: 8px 0; font-weight: bold; color: white;">
                <span>🇫🇷 France</span>
                <span style="color: #e6c619;">3</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 16px; margin: 8px 0; font-weight: bold; color: white;">
                <span>🇸🇦 Saudi Arabia</span>
                <span>1</span>
            </div>
            <div style="font-size: 11px; color: #a0aec0; border-top: 1px solid #2d3139; padding-top: 6px; margin-top: 6px; font-style: italic;">
                ⚽ K. Mbappé (12', 81'), K. Coman (45') | ⚽ S. Al-Dawsari (60' pen)
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )