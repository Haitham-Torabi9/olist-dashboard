# ---------- Imports ----------
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ---------- Page setup ----------
st.set_page_config(page_title="Olist | Commerce Analytics", page_icon="📊", layout="wide")

# ---------- One color palette for the whole app ----------
PRIMARY = "#6366F1"   # indigo
TEAL = "#14B8A6"
AMBER = "#F59E0B"
ORANGE = "#F97316"
RED = "#EF4444"
GREEN = "#22C55E"
SLATE = "#64748B"

# ---------- Custom CSS ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    #MainMenu, footer { visibility: hidden; }
    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1400px; }

    .hero {
        background: linear-gradient(135deg, #312E81 0%, #4F46E5 55%, #0EA5E9 100%);
        padding: 28px 32px; border-radius: 18px; margin-bottom: 22px;
    }
    .hero .title { color: #fff; font-size: 2rem; font-weight: 800; letter-spacing: -0.5px; }
    .hero .sub { color: rgba(255,255,255,.85); margin-top: 6px; font-size: 1rem; }

    div[data-testid="stMetric"] {
        background: #111827; border: 1px solid #1F2937;
        padding: 16px 18px; border-radius: 14px;
    }
    div[data-testid="stMetricLabel"] p { color: #9CA3AF; font-size: .85rem; font-weight: 500; }
    div[data-testid="stMetricValue"] { font-weight: 700; }

    .finding {
        background: #111827; border: 1px solid #1F2937;
        border-top: 4px solid var(--c); border-radius: 14px; padding: 18px 20px;
    }
    .finding .tag { font-size: .7rem; letter-spacing: 1.2px; font-weight: 700; color: var(--c); }
    .finding .head { font-size: 1.25rem; font-weight: 700; color: #F9FAFB; margin: 6px 0; }
    .finding .body { font-size: .92rem; color: #9CA3AF; line-height: 1.55; }

    .callout {
        background: rgba(99,102,241,.08); border-left: 4px solid var(--c);
        padding: 14px 18px; border-radius: 8px; color: #E5E7EB;
        font-size: .95rem; line-height: 1.55; margin-top: 6px;
    }
    .section-title { font-size: 1.15rem; font-weight: 700; color: #F9FAFB; margin: 4px 0 2px 0; }

    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] { padding: 10px 18px; font-weight: 600; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- Helper functions ----------
def finding(tag, head, body, color=PRIMARY):
    """A summary card with a colored top border."""
    st.markdown(
        f'<div class="finding" style="--c:{color}">'
        f'<div class="tag">{tag}</div><div class="head">{head}</div>'
        f'<div class="body">{body}</div></div>',
        unsafe_allow_html=True,
    )


def callout(text, color=PRIMARY):
    """A short takeaway under a chart."""
    st.markdown(f'<div class="callout" style="--c:{color}">{text}</div>', unsafe_allow_html=True)


def section(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def style(fig, height=380):
    """Apply the same clean look to every chart."""
    fig.update_layout(
        template="plotly_dark",
        height=height,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=13),
        showlegend=False,
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgba(148,163,184,0.15)")
    return fig


def pct_change(new, old):
    return (new - old) / old * 100 if old else None


# ---------- Load data ----------
APP_DIR = Path(__file__).parent   # the folder that contains app.py


@st.cache_data
def load_orders():
    return pd.read_csv(APP_DIR / "orders_clean.csv", parse_dates=["order_purchase_timestamp"])


@st.cache_data
def load_rfm():
    return pd.read_csv(APP_DIR / "rfm.csv")


orders = load_orders()
rfm = load_rfm()
orders["year"] = orders["order_purchase_timestamp"].dt.year
orders["month"] = orders["order_purchase_timestamp"].dt.month

# ---------- Sidebar filters ----------
st.sidebar.markdown("### Filters")
years = [y for y in sorted(orders["year"].unique()) if y >= 2017]
selected_year = st.sidebar.selectbox("Year", years, index=len(years) - 1)
all_states = sorted(orders["customer_state"].dropna().unique())
selected_states = st.sidebar.multiselect("Customer state (empty = all)", all_states)
st.sidebar.caption("2016 is excluded: it contains only a few hundred orders.")

base = orders[orders["customer_state"].isin(selected_states)] if selected_states else orders
cur = base[base["year"] == selected_year]

if cur.empty:
    st.warning("No orders for this selection. Try another filter.")
    st.stop()

# Previous period = the SAME months of the previous year (fair comparison)
prev = base[(base["year"] == selected_year - 1) & (base["month"].isin(cur["month"].unique()))]
has_prev = selected_year - 1 >= 2017 and len(prev) > 0

# ---------- Header ----------
scope = ", ".join(selected_states) if selected_states else "all states"
st.markdown(
    f'<div class="hero"><div class="title">Olist E-Commerce Performance</div>'
    f'<div class="sub">Sales, delivery and customer insights &nbsp;|&nbsp; {selected_year} &nbsp;|&nbsp; {scope}</div></div>',
    unsafe_allow_html=True,
)

# ---------- KPI cards ----------
revenue = cur["total_price"].sum()
aov = cur["total_price"].mean()
review = cur["review_score"].mean()
late_pct = cur["is_late"].mean() * 100

d_orders = d_rev = d_aov = d_review = d_late = None
if has_prev:
    d_orders = f"{pct_change(len(cur), len(prev)):+.1f}%"
    d_rev = f"{pct_change(revenue, prev['total_price'].sum()):+.1f}%"
    d_aov = f"{pct_change(aov, prev['total_price'].mean()):+.1f}%"
    d_review = f"{review - prev['review_score'].mean():+.2f}"
    d_late = f"{late_pct - prev['is_late'].mean() * 100:+.1f} pp"

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Orders", f"{len(cur):,}", d_orders)
k2.metric("Revenue", f"R$ {revenue / 1e6:.2f}M", d_rev)
k3.metric("Avg. order value", f"R$ {aov:,.0f}", d_aov)
k4.metric("Avg. review score", f"{review:.2f} / 5", d_review)
k5.metric("Late deliveries", f"{late_pct:.1f}%", d_late, delta_color="inverse")
if has_prev:
    st.caption(f"Changes compare with the same months of {selected_year - 1}.")

st.write("")

# ---------- Key findings (numbers update with the filters) ----------
reviewed = cur.dropna(subset=["review_score"])
on_time_score = reviewed.loc[~reviewed["is_late"], "review_score"].mean()
late_score = reviewed.loc[reviewed["is_late"], "review_score"].mean()

one_time = (rfm["frequency"] == 1).mean() * 100
risk = rfm[rfm["segment"] == "Big spenders at risk"]

f1, f2, f3 = st.columns(3)
with f1:
    if pd.notna(on_time_score) and pd.notna(late_score):
        finding(
            "FINDING 01 | DELIVERY",
            f"Late delivery costs {on_time_score - late_score:.1f} stars",
            f"Late orders average {late_score:.2f} versus {on_time_score:.2f} for on-time orders. "
            f"Only {late_pct:.1f}% of orders arrive late, so the problem is narrow and fixable.",
            RED,
        )
    else:
        finding("FINDING 01 | DELIVERY", "Not enough late orders", "This selection has too few late orders to compare.", RED)
with f2:
    finding(
        "FINDING 02 | RETENTION",
        f"{one_time:.0f}% of customers never come back",
        "Almost every customer buys once. The biggest growth lever is repeat purchase, not only new acquisition.",
        AMBER,
    )
with f3:
    finding(
        "FINDING 03 | OPPORTUNITY",
        f"{len(risk):,} high-value customers are inactive",
        f"They spent about R$ {risk['monetary'].mean():,.0f} each but have not purchased for roughly a year. "
        "This is the best win-back target.",
        TEAL,
    )

st.write("")

# ---------- Tabs ----------
tab1, tab2, tab3, tab4 = st.tabs(["Sales", "Delivery & Satisfaction", "Geography", "Customers"])

# ===== Tab 1: Sales =====
with tab1:
    monthly = (
        cur.groupby("purchase_month")
        .agg(revenue=("total_price", "sum"), orders=("order_id", "count"))
        .reset_index()
    )
    peak = monthly.loc[monthly["revenue"].idxmax()]

    left, right = st.columns([2, 1])

    with left:
        section("Monthly revenue")
        fig = go.Figure(
            go.Scatter(
                x=monthly["purchase_month"], y=monthly["revenue"],
                mode="lines+markers", fill="tozeroy",
                line=dict(color=PRIMARY, width=3), marker=dict(size=7),
                fillcolor="rgba(99,102,241,0.15)",
                customdata=monthly["orders"],
                hovertemplate="%{x}<br>Revenue: R$ %{y:,.0f}<br>Orders: %{customdata:,}<extra></extra>",
            )
        )
        fig.add_annotation(
            x=peak["purchase_month"], y=peak["revenue"],
            text=f"Peak: {peak['purchase_month']}",
            showarrow=True, arrowhead=2, ay=-40,
            font=dict(color=AMBER, size=13), arrowcolor=AMBER,
        )
        fig.update_xaxes(type="category")
        st.plotly_chart(style(fig, 400), use_container_width=True)

    with right:
        section("Top categories by revenue")
        cat = (
            cur.groupby("category")
            .agg(revenue=("total_price", "sum"))
            .nlargest(8, "revenue")
            .reset_index()
            .sort_values("revenue")
        )
        cat["category"] = cat["category"].str.replace("_", " ").str.title()
        fig_cat = px.bar(cat, x="revenue", y="category", orientation="h",
                         labels={"revenue": "Revenue (R$)", "category": ""})
        fig_cat.update_traces(marker_color=TEAL)
        st.plotly_chart(style(fig_cat, 400), use_container_width=True)

    msg = f"Revenue peaked in <b>{peak['purchase_month']}</b> at R$ {peak['revenue']:,.0f}."
    if peak["purchase_month"] == "2017-11":
        msg += " Black Friday (Nov 24) alone brought 1,147 orders, about 2.4x the next busiest day."
    callout(msg, PRIMARY)

# ===== Tab 2: Delivery & Satisfaction =====
with tab2:
    reviewed = cur.dropna(subset=["review_score"]).copy()
    bins = [-1000, 0, 3, 7, 1000]
    labels = ["On time or early", "1-3 days late", "4-7 days late", "7+ days late"]
    reviewed["delay_group"] = pd.cut(reviewed["delay_days"], bins=bins, labels=labels)

    delay = (
        reviewed.groupby("delay_group", observed=True)["review_score"]
        .agg(avg_score="mean", orders="count")
        .reset_index()
    )
    delay["delay_group"] = delay["delay_group"].astype(str)
    color_map = {"On time or early": GREEN, "1-3 days late": AMBER, "4-7 days late": ORANGE, "7+ days late": RED}

    left, right = st.columns([3, 2])

    with left:
        section("Review score by delivery delay")
        fig2 = go.Figure(
            go.Bar(
                x=delay["delay_group"], y=delay["avg_score"],
                marker_color=[color_map[g] for g in delay["delay_group"]],
                text=delay["avg_score"].round(2), textposition="outside",
                customdata=delay["orders"],
                hovertemplate="%{x}<br>Avg score: %{y:.2f}<br>Orders: %{customdata:,}<extra></extra>",
            )
        )
        fig2.update_yaxes(range=[0, 5.5], title="Average review score")
        st.plotly_chart(style(fig2, 400), use_container_width=True)

    with right:
        section("Share of orders by delay")
        fig_pie = px.pie(
            delay, names="delay_group", values="orders", hole=0.6,
            color="delay_group", color_discrete_map=color_map,
        )
        fig_pie.update_traces(textinfo="percent", sort=False)
        st.plotly_chart(style(fig_pie, 400), use_container_width=True)

    if pd.notna(on_time_score) and pd.notna(late_score):
        callout(
            f"Customers rate late orders <b>{late_score:.2f}</b> versus <b>{on_time_score:.2f}</b> for on-time orders. "
            "The score falls at every stage of delay, and even a 1-3 day delay costs about one star. "
            "Priority: orders that slip beyond 7 days.",
            RED,
        )

# ===== Tab 3: Geography =====
with tab3:
    state = (
        cur.groupby("customer_state")
        .agg(revenue=("total_price", "sum"),
             orders=("order_id", "count"),
             late_pct=("is_late", lambda s: s.mean() * 100),
             avg_days=("delivery_days", "mean"))
        .reset_index()
    )

    left, right = st.columns(2)

    with left:
        section("Top 10 states by revenue")
        top = state.nlargest(10, "revenue").sort_values("revenue")
        fig_s = px.bar(top, x="revenue", y="customer_state", orientation="h",
                       labels={"revenue": "Revenue (R$)", "customer_state": ""})
        fig_s.update_traces(marker_color=PRIMARY)
        st.plotly_chart(style(fig_s, 420), use_container_width=True)

    with right:
        section("Highest late-delivery rate (states with 300+ orders)")
        big = state[state["orders"] >= 300].nlargest(10, "late_pct").sort_values("late_pct")
        if len(big) > 0:
            fig_l = px.bar(big, x="late_pct", y="customer_state", orientation="h",
                           labels={"late_pct": "Late deliveries (%)", "customer_state": ""})
            fig_l.update_traces(marker_color=RED)
            st.plotly_chart(style(fig_l, 420), use_container_width=True)
        else:
            st.info("Not enough orders per state for this selection.")

    top1 = state.nlargest(1, "revenue").iloc[0]
    share = top1["revenue"] / state["revenue"].sum() * 100
    msg = f"<b>{top1['customer_state']}</b> generates {share:.0f}% of revenue. "
    if len(big) > 0:
        worst = big.iloc[-1]
        msg += (f"<b>{worst['customer_state']}</b> has the highest late rate at {worst['late_pct']:.1f}% "
                f"(overall: {late_pct:.1f}%), the first place to look for delivery improvements.")
    callout(msg, ORANGE)
    st.caption("States use Brazilian two-letter codes (SP = Sao Paulo).")

# ===== Tab 4: Customers =====
with tab4:
    seg = (
        rfm.groupby("segment")
        .agg(customers=("customer_unique_id", "count"),
             avg_spend=("monetary", "mean"),
             avg_recency=("recency", "mean"))
        .reset_index()
    )
    seg_colors = {"Champions": TEAL, "Big spenders at risk": AMBER, "Promising": PRIMARY, "Low value": SLATE}
    actions = {
        "Champions": "Reward and retain: loyalty perks, early access",
        "Big spenders at risk": "Win back: personalized offer, free shipping",
        "Promising": "Grow: cross-sell and second-purchase incentive",
        "Low value": "Low priority: automated, low-cost campaigns",
    }

    left, right = st.columns([3, 2])

    with left:
        section("Customer map: recency vs. spend")
        fig_b = px.scatter(
            seg, x="avg_recency", y="avg_spend", size="customers", color="segment",
            color_discrete_map=seg_colors, text="segment", size_max=55,
            labels={"avg_recency": "Days since last order (average)", "avg_spend": "Average spend (R$)"},
        )
        fig_b.update_traces(textposition="top center")
        fig_b.update_xaxes(showgrid=True, gridcolor="rgba(148,163,184,0.15)")
        st.plotly_chart(style(fig_b, 420), use_container_width=True)

    with right:
        section("Segment playbook")
        table = seg.copy()
        table["Recommended action"] = table["segment"].map(actions)
        table = table.rename(columns={"segment": "Segment", "customers": "Customers",
                                      "avg_spend": "Avg spend (R$)", "avg_recency": "Avg days inactive"})
        st.dataframe(
            table.sort_values("Avg spend (R$)", ascending=False),
            hide_index=True, use_container_width=True,
            column_config={
                "Customers": st.column_config.NumberColumn(format="%d"),
                "Avg spend (R$)": st.column_config.NumberColumn(format="%.0f"),
                "Avg days inactive": st.column_config.NumberColumn(format="%.0f"),
            },
        )

    callout(
        f"<b>Big spenders at risk</b>: {len(risk):,} customers who previously spent "
        f"R$ {risk['monetary'].sum() / 1e6:.1f}M in total and have been inactive for about a year. "
        "They are the highest-return audience for a win-back campaign.",
        AMBER,
    )
    st.caption("Segments are calculated on all customers and do not change with the year or state filters.")

# ---------- Footer ----------
st.divider()
st.caption("Data: Olist Brazilian E-Commerce public dataset (Kaggle), delivered orders 2016-2018. "
           "Revenue = product price, excluding freight.")