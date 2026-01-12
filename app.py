"""
Conflux Community Member Tracking Dashboard
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz

from src.data.database import MemberDatabase
from src.data.scraper import MemberScraper

# Page configuration
st.set_page_config(
    page_title="Conflux Community Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Country-themed color palette
COUNTRY_COLORS = {
    "Africa (TG)": "#E8B923",  # Gold (pan-African colors)
    "Arabic (TG)": "#00843D",  # Green (Arab League)
    "China Official (TG)": "#DE2910",  # Red (China flag)
    "China Web3 Community (TG)": "#FFDE00",  # Yellow (China flag stars)
    "English (Discord)": "#5865F2",  # Discord blurple
    "English (TG)": "#012169",  # Blue (UK flag)
    "French (TG)": "#0055A4",  # Blue (France flag)
    "Indonesia (TG)": "#FF0000",  # Red (Indonesia flag)
    "Korea (TG)": "#003478",  # Blue (South Korea flag)
    "LATAM (TG)": "#FCD116",  # Yellow (Colombia - represents LATAM)
    "Persia (TG)": "#239F40",  # Green (Iran flag)
    "Russian (TG)": "#0039A6",  # Blue (Russia flag)
    "Turkey (TG)": "#E30A17",  # Red (Turkey flag)
    "Ukraine (TG)": "#0057B7",  # Blue (Ukraine flag)
    "Vietnam (TG)": "#DA251D",  # Red (Vietnam flag)
}

# Custom CSS for Google Analytics style dark theme
st.markdown("""
<style>
    /* Dark theme background */
    .stApp {
        background-color: #1a1a1a;
    }

    /* Metric cards styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 600;
        color: #e8eaed;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        color: #9aa0a6;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.9rem;
    }

    /* Regional container - outer box */
    .regional-container {
        background-color: #3a3a3a !important;
        border-radius: 12px !important;
        padding: 0 !important;
        margin-bottom: 1rem !important;
        overflow: hidden !important;
        border: 2px solid rgba(255, 255, 255, 0.15) !important;
    }

    /* Main regional header - dark top section */
    .regional-main-header {
        background-color: #1e1e1e !important;
        padding: 1.5rem 1.5rem 1.5rem 1.5rem !important;
        border-left: 4px solid #5865F2 !important;
    }

    .regional-main-header [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
    }

    .regional-main-header [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        color: #9aa0a6 !important;
    }

    .regional-main-header [data-testid="stMetricDelta"] {
        font-size: 1rem !important;
        font-weight: 600 !important;
    }

    /* Sub-groups grid section */
    .regional-subs-grid {
        background-color: #2d2d2d !important;
        padding: 1rem !important;
        display: grid !important;
        gap: 0.5rem !important;
    }

    /* Sub-group metrics - smaller, grid items */
    .regional-sub-item {
        background-color: #252525 !important;
        border-radius: 6px !important;
        padding: 0.75rem !important;
    }

    .regional-sub-item [data-testid="stMetricValue"] {
        font-size: 1.4rem !important;
        font-weight: 500 !important;
        color: #e8eaed !important;
    }

    .regional-sub-item [data-testid="stMetricLabel"] {
        font-size: 0.7rem !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        color: #9aa0a6 !important;
    }

    .regional-sub-item [data-testid="stMetricDelta"] {
        font-size: 0.75rem !important;
        font-weight: 400 !important;
    }

    /* Remove card-like containers (no gray blocks) */
    div[data-testid="stVerticalBlock"] > div {
        background-color: transparent;
        border-radius: 0;
        padding: 0;
    }

    /* Section containers */
    .section-container {
        background-color: #2d2d2d;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #3c4043;
    }

    /* Headers */
    h1, h2, h3 {
        color: #e8eaed !important;
    }

    h1 {
        font-size: 1.8rem !important;
        font-weight: 400 !important;
        margin-bottom: 1.5rem !important;
    }

    h2 {
        font-size: 1.3rem !important;
        font-weight: 400 !important;
        margin-top: 0 !important;
        margin-bottom: 1rem !important;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #3c4043;
    }

    /* Text color */
    p, label, span {
        color: #e8eaed;
    }

    /* Dividers */
    hr {
        border-color: #3c4043;
        margin: 1.5rem 0;
    }

    /* Radio buttons horizontal */
    div[role="radiogroup"] {
        gap: 0.5rem;
    }

    /* Select boxes */
    div[data-baseweb="select"] {
        background-color: #2d2d2d;
    }

    /* Buttons */
    .stButton button {
        background-color: #1a73e8;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
    }

    .stButton button:hover {
        background-color: #1557b0;
    }

    /* Text area */
    textarea {
        background-color: #2d2d2d !important;
        color: #e8eaed !important;
        border: 1px solid #3c4043 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
@st.cache_resource
def get_database():
    """Get database connection (cached)"""
    return MemberDatabase()

db = get_database()

# Initialize session state for dialog
if 'show_collect_dialog' not in st.session_state:
    st.session_state.show_collect_dialog = False
if 'confirm_collect' not in st.session_state:
    st.session_state.confirm_collect = False

# Dialog function
@st.dialog("Confirm Data Collection")
def show_confirmation_dialog(days_since):
    st.write("Are you sure you want to collect the latest data and update all information?")
    st.write(f"**It's been {days_since} day{'s' if days_since != 1 else ''} since the last refresh.**")

    col_yes, col_no = st.columns(2)
    with col_yes:
        if st.button("✅ Yes, Collect Data", use_container_width=True, type="primary"):
            st.session_state.confirm_collect = True
            st.session_state.show_collect_dialog = False
            st.rerun()
    with col_no:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.show_collect_dialog = False
            st.rerun()

# Compact header
col1, col2 = st.columns([2.5, 1])
with col1:
    st.title("📊 Conflux Community Tracker")
with col2:
    # Collect button in header
    if st.button("🔄 Collect Data", use_container_width=True, type="primary"):
        # Get latest timestamp to show days since last refresh
        temp_data = db.get_all_data()
        if not temp_data.empty:
            temp_data['timestamp'] = pd.to_datetime(temp_data['timestamp'])
            last_refresh = temp_data['timestamp'].max()
            days_since = (datetime.now() - last_refresh).days
            st.session_state.days_since_refresh = days_since
            st.session_state.show_collect_dialog = True
        else:
            # No data yet, collect immediately without confirmation
            st.session_state.confirm_collect = True

# Show dialog if needed
if st.session_state.show_collect_dialog:
    show_confirmation_dialog(st.session_state.days_since_refresh)

# Execute collection if confirmed
if st.session_state.confirm_collect:
    st.session_state.confirm_collect = False
    with st.spinner("Scraping..."):
        scraper = MemberScraper()
        counts = scraper.scrape_all()
        successful = {k: v for k, v in counts.items() if v is not None}
        failed = [k for k, v in counts.items() if v is None]

        if successful:
            db.add_member_counts(successful)
            st.success(f"✅ {len(successful)}/15 groups")
        if failed:
            st.warning(f"⚠️ Failed: {', '.join(failed)}")
        st.rerun()

# Get data
all_data = db.get_all_data()

if all_data.empty:
    st.info("👋 No data yet! Click **'Collect Data'** to get started.")
    st.stop()

all_data['timestamp'] = pd.to_datetime(all_data['timestamp'])

# Get latest collection per day (only show one per day)
all_data['date_only'] = all_data['timestamp'].dt.date
latest_per_day = all_data.groupby('date_only')['timestamp'].max()
collection_times = sorted([pd.Timestamp(t) for t in latest_per_day.values], reverse=True)

# === Overview Metrics (Google Analytics style) ===
st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.subheader("📊 Overview")

# Calculate key metrics
latest_data = all_data[all_data['timestamp'] == collection_times[0]]
latest_total = latest_data['member_count'].sum()

if len(collection_times) >= 2:
    previous_data = all_data[all_data['timestamp'] == collection_times[1]]
    previous_total = previous_data['member_count'].sum()
    growth = latest_total - previous_total
    growth_pct = (growth / previous_total * 100) if previous_total > 0 else 0
else:
    growth = 0
    growth_pct = 0

# Top row metrics
metric_cols = st.columns(4)

with metric_cols[0]:
    st.metric("TOTAL MEMBERS", f"{latest_total:,}", f"{growth:+,} ({growth_pct:+.1f}%)")

with metric_cols[1]:
    st.metric("TOTAL GROUPS", f"{len(latest_data)}")

with metric_cols[2]:
    avg_per_group = latest_total / len(latest_data) if len(latest_data) > 0 else 0
    st.metric("AVG PER GROUP", f"{avg_per_group:,.0f}")

with metric_cols[3]:
    largest_group = latest_data.nlargest(1, 'member_count')
    if not largest_group.empty:
        st.metric("LARGEST GROUP",
                  f"{largest_group.iloc[0]['member_count']:,}",
                  largest_group.iloc[0]['group_name'].split(' (')[0][:15])

st.markdown('</div>', unsafe_allow_html=True)

# === Compact Summary Section ===
st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.subheader("📋 Latest Counts")

# Date range selector - always show
col_from, col_to = st.columns(2)

with col_from:
    # If only one day, show same options for both
    from_options = collection_times[1:] if len(collection_times) >= 2 else collection_times
    from_date = st.selectbox(
        "From (Previous):",
        from_options,
        index=0,
        format_func=lambda x: x.strftime("%b %d, %Y %I:%M %p")
    )

with col_to:
    to_date = st.selectbox(
        "To (Latest):",
        collection_times,
        index=0,
        format_func=lambda x: x.strftime("%b %d, %Y %I:%M %p")
    )

# Get counts for selected dates
from_data = all_data[all_data['timestamp'] == from_date]
to_data = all_data[all_data['timestamp'] == to_date]

# Build dictionaries for comparison
from_counts = dict(zip(from_data['group_name'], from_data['member_count']))
to_counts = dict(zip(to_data['group_name'], to_data['member_count']))

# Regional breakdown
regions = {
    "Africa": ["Africa (TG)"],
    "Asia": ["Indonesia (TG)", "Korea (TG)", "Vietnam (TG)"],
    "China": ["China Official (TG)", "China Web3 Community (TG)"],
    "EU + Russian + Ukraine": ["French (TG)", "Russian (TG)", "Ukraine (TG)"],
    "Global (English)": ["English (TG)", "English (Discord)"],
    "Middle East": ["Arabic (TG)", "Persia (TG)", "Turkey (TG)"],
    "Spanish (LATAM)": ["LATAM (TG)"]
}

# Calculate regional totals
regional_data = []
for region, groups in regions.items():
    current_total = sum(to_counts.get(g, 0) for g in groups)
    previous_total = sum(from_counts.get(g, 0) for g in groups)
    delta = current_total - previous_total
    regional_data.append({
        "region": region,
        "current": current_total,
        "delta": delta,
        "groups": groups
    })

# Sort by current count
regional_data.sort(key=lambda x: x['current'], reverse=True)

# Copy-pastable summary text
col_title, col_button = st.columns([3, 1])
with col_title:
    st.subheader("📋 Text Summary")
with col_button:
    st.write("")  # Spacing

summary_items = []
all_groups = sorted(to_counts.keys())

for group_name in all_groups:
    current_count = to_counts[group_name]
    prev_count = from_counts.get(group_name, current_count)
    delta = current_count - prev_count
    delta_str = f"({delta:+d})" if delta != 0 else "(0)"
    summary_items.append(f"{group_name}: {current_count} {delta_str}")

summary_text = "\n".join(summary_items)

# Text area and copy button
col_text, col_copy = st.columns([4, 1])
with col_text:
    st.text_area("Summary:", summary_text, height=300, label_visibility="collapsed")
with col_copy:
    if st.button("📋 Copy", use_container_width=True, key="copy_summary"):
        st.write("")  # Button click handled by browser
    # Add JavaScript to copy to clipboard
    st.markdown(f"""
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        const copyBtn = document.querySelector('[data-testid="stButton"] button');
        if (copyBtn && copyBtn.textContent.includes('Copy')) {{
            copyBtn.addEventListener('click', function() {{
                navigator.clipboard.writeText(`{summary_text}`);
            }});
        }}
    }});
    </script>
    """, unsafe_allow_html=True)

st.subheader("🌍 Regional Distribution")

# Regional cards in 3 columns - redesigned with header + grid
region_cols = st.columns(3)
for idx, region_info in enumerate(regional_data):
    with region_cols[idx % 3]:
        # Outer container
        st.markdown('<div class="regional-container">', unsafe_allow_html=True)

        # Main regional header (dark section at top)
        st.markdown('<div class="regional-main-header">', unsafe_allow_html=True)
        delta_color = "normal" if region_info['delta'] >= 0 else "inverse"
        st.metric(
            region_info['region'],
            f"{region_info['current']:,}",
            f"{region_info['delta']:+,}",
            delta_color=delta_color
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # Sub-groups grid section
        st.markdown('<div class="regional-subs-grid">', unsafe_allow_html=True)

        # Create sub-columns for grid layout
        if len(region_info['groups']) > 1:
            sub_cols = st.columns(2)
        else:
            sub_cols = [st.container()]

        for sub_idx, group_name in enumerate(region_info['groups']):
            if group_name in to_counts:
                current_count = to_counts[group_name]
                prev_count = from_counts.get(group_name, current_count)
                delta = current_count - prev_count
                delta_color_group = "normal" if delta >= 0 else "inverse"

                # Keep (TG) and (Discord) labels
                display_name = group_name

                # Each sub-metric in its grid cell
                with sub_cols[sub_idx % len(sub_cols)]:
                    st.markdown('<div class="regional-sub-item">', unsafe_allow_html=True)
                    st.metric(
                        display_name,
                        f"{current_count:,}",
                        f"{delta:+,}",
                        delta_color=delta_color_group
                    )
                    st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)  # Close grid
        st.markdown('</div>', unsafe_allow_html=True)  # Close container

st.markdown('</div>', unsafe_allow_html=True)

# === Compact Aggregated Growth Chart ===
st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.subheader("📈 Total Growth")

aggregated_data = db.get_aggregated_totals()

if not aggregated_data.empty:
    # Time range filter (more compact)
    time_range = st.radio(
        "Time Range",
        ["All Time", "2 Weeks", "Month", "Quarter", "6 Months", "Year", "Custom"],
        horizontal=True,
        index=0,
        label_visibility="collapsed"
    )

    # Filter data
    filtered_data = aggregated_data.copy()
    now = datetime.now()

    time_map = {
        "2 Weeks": 14,
        "Month": 30,
        "Quarter": 90,
        "6 Months": 180,
        "Year": 365
    }

    if time_range == "Custom":
        # Show custom date range selectors
        col_from_growth, col_to_growth = st.columns(2)

        with col_from_growth:
            from_options_growth = collection_times[1:] if len(collection_times) >= 2 else collection_times
            from_date_growth = st.selectbox(
                "From:",
                from_options_growth,
                index=0,
                format_func=lambda x: x.strftime("%b %d, %Y %I:%M %p"),
                key="growth_from_date"
            )

        with col_to_growth:
            to_date_growth = st.selectbox(
                "To:",
                collection_times,
                index=0,
                format_func=lambda x: x.strftime("%b %d, %Y %I:%M %p"),
                key="growth_to_date"
            )

        # Filter by custom date range
        filtered_data = filtered_data[(filtered_data['timestamp'] >= from_date_growth) &
                                       (filtered_data['timestamp'] <= to_date_growth)]
    elif time_range in time_map:
        cutoff = now - timedelta(days=time_map[time_range])
        filtered_data = filtered_data[filtered_data['timestamp'] >= cutoff]

    # Modern chart with gradient
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=filtered_data['timestamp'],
        y=filtered_data['total_members'],
        mode='lines+markers',
        name='Total Members',
        line=dict(color='#5865F2', width=3),
        marker=dict(size=8, color='#5865F2'),
        fill='tozeroy',
        fillcolor='rgba(88, 101, 242, 0.1)',
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Members: %{y:,}<extra></extra>'
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=20, b=0),
        hovermode='x unified',
        showlegend=False,
        plot_bgcolor='#2d2d2d',
        paper_bgcolor='#2d2d2d',
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            color='#9aa0a6'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            color='#9aa0a6'
        ),
        font=dict(color='#e8eaed')
    )

    st.plotly_chart(fig, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# === Compact Individual Charts ===
st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.subheader("📊 Individual Groups")

# Compact time filter
time_range_ind = st.radio(
    "Time Range",
    ["All Time", "2 Weeks", "Month", "Quarter", "6 Months", "Year", "Custom"],
    horizontal=True,
    index=0,
    key="individual_time_range",
    label_visibility="collapsed"
)

# Custom date range for individual groups
if time_range_ind == "Custom":
    col_from_ind, col_to_ind = st.columns(2)

    with col_from_ind:
        from_options_ind = collection_times[1:] if len(collection_times) >= 2 else collection_times
        from_date_ind = st.selectbox(
            "From:",
            from_options_ind,
            index=0,
            format_func=lambda x: x.strftime("%b %d, %Y %I:%M %p"),
            key="individual_from_date"
        )

    with col_to_ind:
        to_date_ind = st.selectbox(
            "To:",
            collection_times,
            index=0,
            format_func=lambda x: x.strftime("%b %d, %Y %I:%M %p"),
            key="individual_to_date"
        )

# Use all groups from latest counts (correct nomenclature)
selected_groups = sorted(to_counts.keys())

if selected_groups:
    # Filter by time
    filtered_all_data = all_data.copy()

    if time_range_ind == "Custom":
        # Filter by custom date range
        filtered_all_data = filtered_all_data[(filtered_all_data['timestamp'] >= from_date_ind) &
                                               (filtered_all_data['timestamp'] <= to_date_ind)]
    elif time_range_ind in time_map:
        cutoff = now - timedelta(days=time_map[time_range_ind])
        filtered_all_data = filtered_all_data[filtered_all_data['timestamp'] >= cutoff]

    # Create compact grid (3 columns)
    cols_per_row = 3

    for i in range(0, len(selected_groups), cols_per_row):
        cols = st.columns(cols_per_row)

        for j, col in enumerate(cols):
            group_idx = i + j
            if group_idx >= len(selected_groups):
                break

            group_name = selected_groups[group_idx]
            group_data = filtered_all_data[filtered_all_data['group_name'] == group_name]

            if not group_data.empty:
                with col:
                    # Get color for this country
                    color = COUNTRY_COLORS.get(group_name, '#999999')

                    # Compact metric
                    if len(group_data) > 1:
                        growth = group_data['member_count'].iloc[-1] - group_data['member_count'].iloc[0]
                        st.metric(
                            group_name,
                            f"{group_data['member_count'].iloc[-1]:,.0f}",
                            f"{growth:+,}"
                        )
                    else:
                        st.metric(
                            group_name,
                            f"{group_data['member_count'].iloc[-1]:,.0f}"
                        )

                    # Compact modern chart
                    fig = go.Figure()

                    fig.add_trace(go.Scatter(
                        x=group_data['timestamp'],
                        y=group_data['member_count'],
                        mode='lines+markers',
                        line=dict(color=color, width=2),
                        marker=dict(size=5, color=color),
                        fill='tozeroy',
                        fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1)',
                        hovertemplate='%{y:,}<extra></extra>'
                    ))

                    fig.update_layout(
                        height=150,
                        margin=dict(l=0, r=0, t=0, b=0),
                        showlegend=False,
                        plot_bgcolor='#2d2d2d',
                        paper_bgcolor='#2d2d2d',
                        xaxis=dict(showticklabels=False, showgrid=False, color='#9aa0a6'),
                        yaxis=dict(showticklabels=False, showgrid=False, color='#9aa0a6'),
                        font=dict(color='#e8eaed')
                    )

                    st.plotly_chart(fig, use_container_width=True, key=f"chart_{group_name}")

st.markdown('</div>', unsafe_allow_html=True)

# === Future Analytics Ideas (Expandable) ===

with st.expander("💡 Future Analytics Ideas (Long-term with more data)", expanded=False):
    st.markdown("""
    ### 1. Growth Rate Analysis
    - Moving averages (7-day, 14-day, 30-day)
    - Growth velocity (acceleration/deceleration)
    - Compound Annual Growth Rate (CAGR) per group
    - Best/worst performing groups over time

    ### 2. Predictive Analytics
    - Forecast future growth using linear regression
    - Seasonal patterns (if collecting more frequently)
    - Anomaly detection (unusual spikes/drops)
    - Milestone predictions (when will X group hit Y members?)

    ### 3. Comparative Analysis
    - Group-to-group correlation (which groups grow together?)
    - Regional market share over time
    - Telegram vs Discord comparison (if adding more Discord channels)
    - Benchmark against targets/goals

    ### 4. Engagement Metrics *(requires additional data collection)*
    - Active users vs total members ratio
    - Message volume per group
    - New member retention rates
    - Peak activity times/days

    ### 5. Advanced Visualizations
    - Heatmap: Growth by region over time
    - Treemap: Relative size of all groups
    - Sankey diagram: Member flow between collection periods
    - Candlestick charts: Show high/low/open/close if collecting more frequently

    ### 6. Statistical Analysis
    - Correlation matrix between groups
    - Standard deviation and volatility
    - Percentile rankings
    - Z-scores for outlier identification

    ### 7. Reporting Features
    - Auto-generated insights ("Fastest growing region this month")
    - PDF export for stakeholders
    - Email alerts for significant changes
    - Custom KPI dashboard

    ### 8. Data Quality
    - Track scraping success rate over time
    - Identify missing data patterns
    - Data freshness indicators
    - Historical data validation

    ---

    **To implement these, you'd need:**
    - More frequent data collection (daily would unlock time-series analysis)
    - Longer history (6+ months for meaningful trends)
    - Additional data sources (engagement metrics from Telegram API)
    - Machine learning libraries (scikit-learn, prophet for forecasting)
    """)
