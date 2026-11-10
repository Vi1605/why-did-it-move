import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import duckdb
import plotly.express as px
import streamlit as st

from src.anomaly import detect_anomalies
from src.rca import narrate, run_rca

st.set_page_config(page_title="Why Did It Move?", layout="wide")

DB = Path("data/renewals.duckdb")
if not DB.exists():  # lets the app also work when deployed online
    from src.generate_data import main as generate
    from src.load_db import main as load
    generate()
    load()


@st.cache_data
def load_data():
    con = duckdb.connect(str(DB), read_only=True)
    monthly = con.sql(Path("sql/monthly_kpi.sql").read_text()).df()
    detail = con.sql("SELECT * FROM renewals").df()
    con.close()
    return monthly, detail


monthly, detail = load_data()
monthly = detect_anomalies(monthly)

st.title("Why Did It Move?")
st.caption("KPI anomaly detection and automated root-cause analysis. "
           "Synthetic UK motor-insurance renewal data.")

fig = px.line(monthly, x="renewal_month", y="renewal_rate", markers=True,
              labels={"renewal_month": "Month", "renewal_rate": "Renewal rate"})
flagged = monthly[monthly["is_anomaly"]]
fig.add_scatter(x=flagged["renewal_month"], y=flagged["renewal_rate"],
                mode="markers", marker=dict(size=14, color="red"), name="Anomaly")
st.plotly_chart(fig, use_container_width=True)

months = monthly["renewal_month"].tolist()
default_cur = months.index(monthly.loc[monthly["robust_z"].abs().idxmax(), "renewal_month"])
fmt = lambda m: m.strftime("%b %Y")

cur = st.sidebar.selectbox("Month to explain", months, index=default_cur, format_func=fmt)
base_options = [m for m in months if m < cur]
if not base_options:
    st.info("Pick a later month: we need an earlier month to compare against.")
    st.stop()
base = st.sidebar.selectbox("Compare against", base_options,
                            index=len(base_options) - 1, format_func=fmt)

st.subheader("Explanation")
st.markdown(narrate(detail, base, cur))

res = run_rca(detail, base, cur)
top = res.head(10).copy()
top["label"] = top["dimension"] + " = " + top["segment"].astype(str)
long = top.melt(id_vars="label", value_vars=["rate_effect", "mix_effect"],
                var_name="effect", value_name="pts")
long["pts"] *= 100
fig2 = px.bar(long, x="pts", y="label", color="effect", orientation="h",
              labels={"pts": "Contribution (percentage points)", "label": ""})
fig2.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig2, use_container_width=True)

with st.expander("Full table"):
    st.dataframe(res.drop(columns="abs_contribution"), use_container_width=True)

    