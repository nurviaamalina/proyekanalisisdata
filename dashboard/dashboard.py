import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Olist Dashboard", layout="wide")

sns.set(style="whitegrid")

# -------------------------
# Load Data
# -------------------------
@st.cache_data
def load_data():
    orders = pd.read_csv("data/olist_orders_dataset.csv",
                         parse_dates=['order_purchase_timestamp'])
    items = pd.read_csv("data/olist_order_items_dataset.csv")
    products = pd.read_csv("data/olist_products_dataset.csv")

    df = items.merge(orders, on='order_id')
    df = df.merge(products, on='product_id')

    return df

df = load_data()

# -------------------------
# CLEANING 
# -------------------------
df = df.dropna(subset=['product_category_name'])
df['year'] = df['order_purchase_timestamp'].dt.year
df['month'] = df['order_purchase_timestamp'].dt.to_period('M').astype(str)

# -------------------------
# SIDEBAR FILTER
# -------------------------
st.sidebar.header("Filter")

year = st.sidebar.multiselect(
    "Tahun",
    options=sorted(df['year'].unique()),
    default=sorted(df['year'].unique())
)

category = st.sidebar.multiselect(
    "Kategori",
    options=sorted(df['product_category_name'].unique()),
    default=sorted(df['product_category_name'].unique())
)

status = st.sidebar.multiselect(
    "Status",
    options=df['order_status'].unique(),
    default=df['order_status'].unique()
)

filtered_df = df[
    (df['year'].isin(year)) &
    (df['product_category_name'].isin(category)) &
    (df['order_status'].isin(status))
]

# -------------------------
# TITLE
# -------------------------
st.title("📊 Olist E-Commerce Dashboard")


# -------------------------
# KPI (BIAR KEREN)
# -------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Total Order", filtered_df['order_id'].nunique())
col2.metric("Total Produk Terjual", filtered_df.shape[0])
col3.metric("Jumlah Kategori", filtered_df['product_category_name'].nunique())

# -------------------------
# CHART 1: Top Kategori
# -------------------------
st.subheader("🏆 Top 10 Kategori Produk")

top_cat = (filtered_df.groupby('product_category_name')
           .size()
           .sort_values(ascending=False)
           .head(10))

fig1, ax1 = plt.subplots(figsize=(8,5))
sns.barplot(x=top_cat.values, y=top_cat.index, ax=ax1)
ax1.set_xlabel("Jumlah Terjual")
ax1.set_ylabel("Kategori")

st.pyplot(fig1)

# -------------------------
# CHART 2: Tren Penjualan
# -------------------------
st.subheader("📈 Tren Penjualan per Bulan")

trend = filtered_df.groupby('month').size()

fig2, ax2 = plt.subplots(figsize=(10,5))
trend.plot(ax=ax2)
ax2.set_xlabel("Bulan")
ax2.set_ylabel("Jumlah Order")
plt.xticks(rotation=45)

st.pyplot(fig2)

# -------------------------
# CHART 3: Status Pesanan
# -------------------------
st.subheader("📦 Distribusi Status Pesanan")

status_count = filtered_df['order_status'].value_counts().sort_values(ascending=True)

fig3, ax3 = plt.subplots(figsize=(8,5))

sns.barplot(
    x=status_count.values,
    y=status_count.index,
    ax=ax3
)

ax3.set_xlabel("Jumlah Order")
ax3.set_ylabel("Status")

st.pyplot(fig3)
# -------------------------
# DATA TABLE
# -------------------------
st.subheader("📋 Data Detail")
st.dataframe(filtered_df.head(100))
