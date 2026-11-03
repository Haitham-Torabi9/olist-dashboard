# Olist E-Commerce Analytics Dashboard

An end-to-end analysis of ~96K delivered orders from a Brazilian e-commerce marketplace: what drives sales and customer satisfaction, and where the business can improve.

**[Live dashboard](https://olist-analytics2026.streamlit.app/)**

## Key findings

- **Late delivery costs about 2 review stars.** Late orders average 2.27 vs. 4.29 for on-time orders. Even a 1-3 day delay costs about one star.
- **97% of customers buy only once.** The biggest growth opportunity is repeat purchase, not only acquiring new customers.
- **22,759 high-value customers are inactive.** They spent about R$ 268 each but have not purchased in about a year: the best win-back target.
- **Black Friday 2017** produced 1,147 orders in a single day, about 2.4x the next busiest day.
- **Volume is not value.** `watches_gifts` has an average order value of R$ 213, nearly double `bed_bath_table` (R$ 112), so it ranks 2nd in revenue with far fewer orders.

## What the project covers

1. **Data cleaning and merging:** 9 related tables joined into one analysis table (one row per order), with safety checks against duplicated rows.
2. **Exploratory analysis:** sales trends, categories, delivery time, delays vs. review scores.
3. **Customer segmentation:** RFM scoring with four named segments and a recommended action for each.
4. **Interactive dashboard:** four tabs (Sales, Delivery, Geography, Customers) with year and state filters.

## Tech stack

Python, Pandas, Plotly, Streamlit, Matplotlib, Jupyter.

## Project structure





## Run locally

```bash
pip install -r requirements.txt
streamlit run app/app.py
```

## Data

[Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (Kaggle). Raw files are not included in this repository; download them into a `data/` folder to re-run the notebook.

## Limitations and next steps

- The analysis shows **correlation, not causation**: late delivery and low scores move together, but product quality may also play a role.
- Open question: does a late first order reduce the chance that a customer returns?
- Next: seller-level analysis and a delivery-time prediction model.