import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from statsmodels.formula.api import ols
import statsmodels.api as sm
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

DATA_PATH = "Analysis/crime_summary.csv"
RAW_DATA_PATH = "cleaned_data/master_crime_data.csv"

CRIME_CATEGORIES = {
    "Violent":  ["Assault", "Robbery", "Homicide", "Sexual Assault", "Kidnapping", "Family Offense"],
    "Property": ["Theft", "Breaking & Entering", "Property Crime", "Fraud", "Alarm", "Vehicle Theft"],
    "Drugs":    ["Drugs", "Liquor"],
}

GRADIENTS = {
    "All":      [[0.1, "#0c2461"], [0.35, "#1565c0"], [0.55, "#2e7d32"], [0.72, "#fdd835"], [0.88, "#fb8c00"], [1.0, "#b71c1c"]],
    "Violent":  [[0.1, "#3e2723"], [0.35, "#c62828"], [0.55, "#e53935"], [0.75, "#ff9800"], [0.9, "#ffeb3b"], [1.0, "#fff9c4"]],
    "Property": [[0.1, "#0d47a1"], [0.35, "#1976d2"], [0.55, "#42a5f5"], [0.72, "#81d4fa"], [0.88, "#fff59d"], [1.0, "#ff9800"]],
    "Drugs":    [[0.1, "#1b5e20"], [0.35, "#388e3c"], [0.55, "#7cb342"], [0.72, "#cddc39"], [0.88, "#fbc02d"], [1.0, "#d84315"]],
}

st.set_page_config(
    page_title="Utah Crime Analysis",
    page_icon="🔍",
    layout="wide",
)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["year"] = df["year"].astype(int)
    return df


@st.cache_data
def load_raw_data():
    df = pd.read_csv(RAW_DATA_PATH, low_memory=False)
    df = df.dropna(subset=["latitude", "longitude"])
    df = df[df["longitude"].between(-114.2, -109.0) & df["latitude"].between(36.8, 42.1)]
    df["year"] = pd.to_datetime(df["date"], format="%m/%d/%Y", errors="coerce").dt.year
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)
    df = df[df["year"].between(2007, 2019)]
    df["latitude"] = df["latitude"].round(4)
    df["longitude"] = df["longitude"].round(4)

    def assign_category(parent_type):
        if pd.isna(parent_type):
            return "Other"
        for cat, types in CRIME_CATEGORIES.items():
            if parent_type in types:
                return cat
        return "Other"

    df["category"] = df["parent_incident_type"].map(assign_category)
    return df


df = load_data()

st.title("Utah Crime Incident Rate Analysis (2007–2019)")
st.markdown(
    "Exploring how crime incident rates (per 100,000 residents) vary by **city**, **year**, and **season** "
    "across Utah municipalities."
)

# --- Sidebar ---
st.sidebar.header("Filters")
all_cities = sorted(df["city"].unique())
selected_cities = st.sidebar.multiselect("Cities", all_cities, default=all_cities[:8])
year_range = st.sidebar.slider("Year range", int(df["year"].min()), int(df["year"].max()), (2010, 2019))

filtered = df[
    df["city"].isin(selected_cities) &
    df["year"].between(year_range[0], year_range[1])
]

# --- Tabs ---
tab_trends, tab_season, tab_analysis, tab_heatmap = st.tabs(["Trends", "Season Comparison", "ANOVA Analysis", "Heatmap"])

with tab_trends:
    st.subheader("Incident Rate by Year")
    yearly = (
        filtered.groupby(["city", "year"])["incident_rate_per_100k"]
        .mean()
        .reset_index()
    )
    fig_line = px.line(
        yearly,
        x="year",
        y="incident_rate_per_100k",
        color="city",
        markers=True,
        labels={"incident_rate_per_100k": "Incidents per 100k", "year": "Year"},
    )
    fig_line.update_layout(legend_title="City", hovermode="x unified")
    st.plotly_chart(fig_line, use_container_width=True)

    st.subheader("Average Incident Rate by City")
    city_avg = (
        filtered.groupby("city")["incident_rate_per_100k"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    fig_bar = px.bar(
        city_avg,
        x="city",
        y="incident_rate_per_100k",
        labels={"incident_rate_per_100k": "Avg Incidents per 100k", "city": "City"},
        color="incident_rate_per_100k",
        color_continuous_scale="Reds",
    )
    fig_bar.update_layout(coloraxis_showscale=False, xaxis_tickangle=-35)
    st.plotly_chart(fig_bar, use_container_width=True)

with tab_season:
    st.subheader("Incident Rate by Season")
    st.markdown(
        "Box plots show the distribution of incident rates across all city-year combinations "
        "within each season. Our ANOVA found **season is not a statistically significant predictor** "
        "of crime rate."
    )
    season_order = ["Spring", "Summer", "Fall", "Winter"]
    season_data = filtered[filtered["season"].isin(season_order)].copy()
    fig_box = px.box(
        season_data,
        x="season",
        y="incident_rate_per_100k",
        category_orders={"season": season_order},
        color="season",
        labels={"incident_rate_per_100k": "Incidents per 100k", "season": "Season"},
        points="outliers",
    )
    fig_box.update_layout(showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

    season_means = (
        filtered.groupby("season")["incident_rate_per_100k"]
        .agg(["mean", "median", "std"])
        .rename(columns={"mean": "Mean", "median": "Median", "std": "Std Dev"})
        .round(1)
    )
    st.dataframe(season_means, use_container_width=True)

with tab_analysis:
    st.subheader("Two-Way ANOVA Results")
    st.markdown(
        "We fit a two-way ANOVA model with a log-transformed incident rate to test whether "
        "**city**, **year**, and **season** significantly predict crime rates."
    )

    anova_data = df.copy()
    anova_data["log_incident_rate"] = np.log1p(anova_data["incident_rate_per_100k"])
    anova_data["year"] = anova_data["year"].astype("category")
    anova_data["season"] = anova_data["season"].astype("category")
    anova_data["city"] = anova_data["city"].astype("category")

    try:
        log_model = ols(
            "log_incident_rate ~ C(season) + C(city) + C(year)",
            data=anova_data,
        ).fit()
        anova_table = sm.stats.anova_lm(log_model, typ=3)

        display_table = anova_table[["sum_sq", "df", "F", "PR(>F)"]].copy()
        display_table.columns = ["Sum Sq", "df", "F-statistic", "p-value"]
        display_table = display_table.round(4)

        def highlight_sig(val):
            if isinstance(val, float) and val < 0.05:
                return "background-color: #d4edda"
            return ""

        st.dataframe(
            display_table.style.map(highlight_sig, subset=["p-value"]),
            use_container_width=True,
        )

        st.markdown("**Key Takeaways:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            season_p = anova_table.loc["C(season)", "PR(>F)"]
            sig = "significant" if season_p < 0.05 else "NOT significant"
            st.metric("Season", f"p = {season_p:.4f}", sig)
        with col2:
            city_p = anova_table.loc["C(city)", "PR(>F)"]
            sig = "significant" if city_p < 0.05 else "NOT significant"
            st.metric("City", f"p = {city_p:.4f}", sig)
        with col3:
            year_p = anova_table.loc["C(year)", "PR(>F)"]
            sig = "significant" if year_p < 0.05 else "NOT significant"
            st.metric("Year", f"p = {year_p:.4f}", sig)

        st.info(
            "Crime incident rates differ significantly by **city** and **year**, "
            "but **season has no significant effect** on crime rates in Utah (2007–2019)."
        )

    except Exception as e:
        st.error(f"Could not fit ANOVA model: {e}")

with tab_heatmap:
    st.subheader("Crime Spatial Heatmap (2007–2019)")
    st.markdown("Geographic density of crime incidents across Utah. Each point represents a reported incident.")

    raw_df = load_raw_data()

    hm_col1, hm_col2 = st.columns(2)
    with hm_col1:
        selected_year = st.selectbox("Year", list(range(2007, 2020)), index=6, key="hm_year")
    with hm_col2:
        selected_cat = st.selectbox("Crime Type", ["All", "Violent", "Property", "Drugs"], key="hm_cat")

    subset = raw_df[raw_df["year"] == selected_year]
    if selected_cat != "All":
        subset = subset[subset["category"] == selected_cat]

    MAX_PTS = 5000
    if len(subset) > MAX_PTS:
        subset = subset.sample(MAX_PTS, random_state=42)

    heat_pts = subset[["latitude", "longitude"]].values.tolist()

    gradient = {str(stop): color for stop, color in GRADIENTS[selected_cat]}

    m = folium.Map(location=[40.58, -111.85], zoom_start=9, tiles="CartoDB positron")

    if heat_pts:
        HeatMap(heat_pts, min_opacity=0.35, radius=18, blur=22, gradient=gradient).add_to(m)

    city_markers = [
        (40.7608, -111.8910, "Salt Lake City"),
        (40.3916, -111.8508, "Lehi"),
        (40.6461, -111.4980, "Park City"),
        (40.5621, -111.9294, "South Jordan"),
        (40.7182, -111.8882, "S. Salt Lake"),
        (41.2230, -111.9738, "Ogden"),
        (40.2338, -111.6585, "Provo"),
    ]
    for lat, lon, name in city_markers:
        folium.Marker(
            [lat, lon],
            icon=folium.DivIcon(html=f'<div style="color:#263238;font-size:10px;font-family:Segoe UI,sans-serif;background:rgba(255,255,255,0.92);padding:2px 5px;border-radius:3px;white-space:nowrap;border:1px solid #b0bec5;">{name}</div>'),
        ).add_to(m)

    st_folium(m, use_container_width=True, height=550, returned_objects=[])

st.markdown("---")
st.caption(
    "Data: Utah Open Data Portal (opendata.utah.gov) + U.S. Census Bureau population estimates. "
    "Source code: [GitHub](https://github.com/mitchja23/386FinalProject)"
)
