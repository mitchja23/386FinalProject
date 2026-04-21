import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from statsmodels.formula.api import ols
import statsmodels.api as sm

DATA_PATH = "Analysis/crime_summary.csv"

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
tab_trends, tab_season, tab_analysis = st.tabs(["Trends", "Season Comparison", "ANOVA Analysis"])

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
            display_table.style.applymap(highlight_sig, subset=["p-value"]),
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

st.markdown("---")
st.caption(
    "Data: Utah Open Data Portal (opendata.utah.gov) + U.S. Census Bureau population estimates. "
    "Source code: [GitHub](https://github.com/mitchja23/386FinalProject)"
)
