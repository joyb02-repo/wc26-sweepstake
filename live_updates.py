import streamlit as st
import pandas as pd

# Page Configuration 
st.markdown("<h2 style='text-align: center;'>🏆 2026 World Cup Live Center</h2>", unsafe_allow_html=True)
st.write("---")

# --- SECURE DATA EXTRACTION FROM GOOGLE SHEETS ---
SPREADSHEET_ID = st.secrets["SPREADSHEET_ID"]

try:
    # 1. Fetch Stakeholders sheet (Sheet1)
    url_teams = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet1"
    df_teams = pd.read_csv(url_teams)
    df_teams.columns = df_teams.columns.str.strip()
    df_teams['StakeHolder'] = df_teams['StakeHolder'].fillna("").astype(str).str.strip()
    df_teams['Country_Clean'] = df_teams['Country'].astype(str).str.strip().str.lower()
    
    # 2. Fetch Automated Live Table sheet (LiveTable)
    url_live = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=LiveTable"
    df_live = pd.read_csv(url_live)
    
except Exception as e:
    st.error("Failed to sync shared data. Ensure your 'LiveTable' tab name and credentials match perfectly.")
    st.stop()

# --- DATA CLEANING AND LOOKUP GENERATION ---
live_stats_lookup = {}
current_group = "A"

for idx, row in df_live.iterrows():
    # Detect which group section we are in based on Column A
    group_val = str(row.iloc[0]).strip()
    if group_val in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]:
        current_group = group_val
        
    team_raw = str(row.iloc[2]).strip() # Column C: Team
    
    # Filter out header labels, empty rows, or table definitions
    if not team_raw or team_raw.lower() in ["team", "nan", "val", "none"]:
        continue
        
    # Clean the points data (stripping out the *3* or *1* asterisks seen in your sheet)
    pts_raw = str(row.iloc[10]).strip() # Column K: Pts
    pts_clean = pts_raw.replace("*", "")
    
    gp_raw = str(row.iloc[3]).strip()  # Column D: GP
    gd_raw = str(row.iloc[9]).strip()  # Column J: GD
    form_raw = str(row.iloc[11]).strip() # Column L: Form
    
    lookup_name = team_raw.lower()
    
    if lookup_name == "usa":
        lookup_name = "united states"
        
    live_stats_lookup[lookup_name] = {
        "group": current_group,
        "gp": gp_raw,
        "gd": gd_raw,
        "pts": pts_clean,
        "form": form_raw if form_raw and form_raw.lower() != "nan" else "No matches yet"
    }

# -----------------------------------------------------------------
# FEATURE 1: GROUP-BY-GROUP STAKEHOLDER STANDINGS
# -----------------------------------------------------------------
st.markdown("### 📊 Stakeholder Standings & Survival Tracker")
st.caption("Live tournament standings grouped by their official tournament pools.")

# Gather all team rows with their matched live stats
all_player_teams = []
for _, row in df_teams.iterrows():
    country = row['Country']
    emoji = row['Emoji']
    owner = row['StakeHolder'] if row['StakeHolder'] else "⏳ Unassigned"
    clean_name = row['Country_Clean']
    
    stats = live_stats_lookup.get(clean_name, {"group": "Unknown", "gp": "0", "gd": "0", "pts": "0", "form": "—"})
    
    all_player_teams.append({
        "country": country,
        "emoji": emoji,
        "owner": owner,
        "group": stats["group"],
        "pts": stats["pts"],
        "gd": stats["gd"]
    })

# Group names to display sequentially
group_list = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]

for g in group_list:
    # Filter teams belonging to the current group iteration
    group_teams = [t for t in all_player_teams if t["group"] == g]
    
    if not group_teams:
        continue # Skip rendering if no stakeholders are mapped to this group yet
        
    # Sort teams within the group by points (highest first)
    try:
        group_teams = sorted(group_teams, key=lambda x: int(x["pts"]), reverse=True)
    except ValueError:
        pass

    st.markdown(f"#### 🏷️ Group {g}")
    
    table_rows = ""
    for team in group_teams:
        status_badge = "<span style='color: #28a745; font-weight: bold;'>🟢 Active</span>"
        row_bg = "transparent"
            
        table_rows += f"""
        <tr style="background-color: {row_bg}; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <td style="padding: 10px; text-align: center; font-size: 20px;">{team['emoji']}</td>
            <td style="font-weight: 600; color: white;">{team['country']}</td>
            <td style="color: #29b5e8; font-weight: bold;">{team['owner']}</td>
            <td style="text-align: center; font-weight: bold; color: #e6c619;">{team['pts']}</td>
            <td style="text-align: center; color: #cbd5e1;">{team['gd']}</td>
            <td>{status_badge}</td>
        </tr>
        """

    # Render a separate structured clean table for the current group pool
    st.markdown(
        f"""
        <table style="width: 100%; border-collapse: collapse; background-color: #11141a; border-radius: 8px; overflow: hidden; margin-bottom: 25px;">
            <thead style="background-color: #1e293b;">
                <tr>
                    <th style="padding: 10px; color: white; width: 10%;">Flag</th>
                    <th style="text-align: left; color: white;">Country</th>
                    <th style="text-align: left; color: white;">Stakeholder</th>
                    <th style="text-align: center; color: white; width: 10%;">Pts</th>
                    <th style="text-align: center; color: white; width: 10%;">GD</th>
                    <th style="text-align: left; color: white; width: 15%;">Status</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
        """,
        unsafe_allow_html=True
    )

st.write("---")

col1, col2 = st.columns([1.2, 1])

# -----------------------------------------------------------------
# FEATURE 2: CURRENT TOP PERFORMERS (Sorted dynamically by Live Points)
# -----------------------------------------------------------------
with col1:
    st.markdown("### 📈 Form & Performance Tracker")
    st.caption("Active team performance highlights and match streaks recorded live.")
    
    leaderboard_data = []
    for _, row in df_teams.iterrows():
        clean_name = row['Country_Clean']
        stats = live_stats_lookup.get(clean_name, None)
        if stats:
            try:
                leaderboard_data.append({
                    "display": f"{row['Emoji']} {row['Country']} ({row['StakeHolder'] if row['StakeHolder'] else 'Unassigned'})",
                    "pts": int(stats['pts']),
                    "form": stats['form']
                })
            except ValueError:
                pass
                
    sorted_leaders = sorted(leaderboard_data, key=lambda x: x['pts'], reverse=True)
    
    if sorted_leaders:
        for idx, leader in enumerate(sorted_leaders[:5]):
            st.markdown(
                f"""
                <div style="background: #1a1c23; padding: 12px; border-left: 4px solid #29b5e8; margin-bottom: 8px; border-radius: 0 6px 6px 0;">
                    <div style="display: flex; justify-content: space-between; font-weight: 600; color: white;">
                        <span>{idx+1}. {leader['display']}</span>
                        <span style="color: #e6c619;">{leader['pts']} Pts</span>
                    </div>
                    <div style="font-size: 11px; color: #8a92a6; margin-top: 4px; font-family: monospace;">Form: {leader['form']}</div>
                </div>
                """, 
                unsafe_allow_html=True
            )
    else:
        st.info("Performance stats will populate automatically once matches register.")

# -----------------------------------------------------------------
# FEATURE 3: LIVE RECENT GAME HIGHLIGHT PANEL
# -----------------------------------------------------------------
with col2:
    st.markdown("### 👟 Recent Matches")
    st.caption("Quick overview of recent group stage results.")
    
    match_samples = [l for l in live_stats_lookup.values() if l['form'] and l['form'] != "—"]
    
    if match_samples:
        count = 0
        for item in match_samples:
            if count >= 3:
                break
            if "Won" in item['form'] or "Drew" in item['form'] or "Lost" in item['form']:
                st.markdown(
                    f"""
                    <div style="background-color: #11141a; border: 1px solid #2d3139; border-radius: 8px; padding: 12px; margin-bottom: 8px;">
                        <span style="font-size: 11px; color: #e6c619; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">Group Stage Match Log</span>
                        <div style="font-size: 14px; font-weight: 600; color: white; margin-top: 4px;">
                            {item['form']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                count += 1
    else:
        st.info("No verified match updates recorded on this loop segment yet.")
