import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.formula.api import ols
import statsmodels.api as sm

if __name__ == "__main__":
    crime_summary = pd.read_csv("cleaned_data/crime_summary.csv")
    crime_summary.info()

    crime_summary.boxplot(
        column="incident_rate_per_100k",
        by="season"
    )
    plt.show()

    model = ols(
        "incident_rate_per_100k ~ C(season) * C(city) + C(year)",
        data=crime_summary
    ).fit()
    anova_table = sm.stats.anova_lm(model, typ=3)
    print(anova_table)

    sm.qqplot(model.resid, line='45')
    plt.show()

    sns.histplot(model.resid, kde=True)

    crime_summary["log_incident_rate"] = np.log1p(crime_summary["incident_rate_per_100k"])
    log_model = ols(
        "log_incident_rate ~ C(season) * C(city) + C(year)",
        data=crime_summary
    ).fit()
    log_anova_table = sm.stats.anova_lm(log_model, typ=3)
    print(log_anova_table)

    sm.qqplot(log_model.resid, line='45')
    plt.show()

    sns.histplot(log_model.resid, kde=True)

    print("Original AIC:", model.aic)
    print("Log model AIC:", log_model.aic)
    print("Original BIC:", model.bic)
    print("Log model BIC:", log_model.bic)

    fig, axes = plt.subplots(1, 2, figsize=(12,5))
    sm.qqplot(model.resid, line='45', ax=axes[0])
    axes[0].set_title("Original Model Residuals")
    sm.qqplot(log_model.resid, line='45', ax=axes[1])
    axes[1].set_title("Log Model Residuals")
    plt.tight_layout()
    plt.show()

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    sns.histplot(model.resid, bins=30, kde=True, ax=axes[0])
    axes[0].set_title("Original Model Residuals")
    sns.histplot(log_model.resid, bins=30, kde=True, ax=axes[1])
    axes[1].set_title("Log Model Residuals")
    plt.tight_layout()
    plt.show()
