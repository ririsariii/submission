import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# Mengatur gaya visualisasi Seaborn
sns.set(style='whitegrid')


# Fungsi untuk membuat data harian
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    }).reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    
    return daily_orders_df

# Fungsi untuk membuat data jumlah item berdasarkan kategori produk
def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name").size().reset_index(name="quantity")
    return sum_order_items_df.sort_values(by="quantity", ascending=False)

# Fungsi untuk membuat distribusi pembayaran berdasarkan metode pembayaran
def create_payment_distribution_df(df):
    payment_df = df.groupby("payment_type").size().reset_index(name="payment_count")
    return payment_df

# Fungsi untuk membuat data RFM (Recency, Frequency, Monetary)
def create_rfm_df(df):
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",
        "order_id": "nunique",
        "payment_value": "sum"
    })
    rfm_df.columns = ["customer_id", "last_purchase", "frequency", "monetary"]
    rfm_df["last_purchase"] = pd.to_datetime(rfm_df["last_purchase"])
    recent_date = df["order_purchase_timestamp"].max()
    rfm_df["recency"] = (recent_date - rfm_df["last_purchase"]).dt.days
    return rfm_df

# Load data
df = pd.read_csv("/dashboard/all_data.csv")

# Konversi kolom timestamp menjadi datetime
df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

# Mendapatkan rentang tanggal
min_date = df['order_purchase_timestamp'].min()
max_date = df['order_purchase_timestamp'].max()

# Sidebar untuk memilih rentang tanggal
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    start_date, end_date = st.date_input(
        label='Rentang Waktu', 
        min_value=min_date, 
        max_value=max_date, 
        value=[min_date, max_date]
    )

# Filter data berdasarkan tanggal yang dipilih
main_df = df[(df["order_purchase_timestamp"] >= pd.to_datetime(start_date)) & 
             (df["order_purchase_timestamp"] <= pd.to_datetime(end_date))]

# Buat berbagai dataframe yang dibutuhkan
daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
payment_distribution_df = create_payment_distribution_df(main_df)
rfm_df = create_rfm_df(main_df)

# Title
st.title('Dashboard E-Commerce Dicoding')

# Total Orders dan Total Revenue
col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total Orders", value=total_orders)

with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "AUD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)

# Visualisasi data harian
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
)
ax.set_xlabel('Date', fontsize=20)
ax.set_ylabel('Total Orders', fontsize=20)  
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

# Kategori Produk Paling Laris Terjual
st.subheader('Kategori Produk Paling Laris Terjual')

# Visualisasi untuk Kategori Produk Paling Laris
fig1, ax1 = plt.subplots()
sns.barplot(data=sum_order_items_df.head(10), x='quantity', y='product_category_name', ax=ax1)
ax1.set_xlabel('Quantity')
ax1.set_ylabel('Product Category')
st.pyplot(fig1)


# Distribusi Pembayaran Berdasarkan Metode Pembayaran
st.subheader('Distribusi Pembayaran Berdasarkan Metode Pembayaran')

# Visualisasi untuk Distribusi Metode Pembayaran
fig2, ax2 = plt.subplots()
sns.barplot(data=payment_distribution_df, x='payment_type', y='payment_count', ax=ax2)
ax2.set_xlabel('Payment Type')
ax2.set_ylabel('Payment Count')
st.pyplot(fig2)

# Visualisasi Revenue Harian
st.subheader('Pendapatan Harian')
fig3, ax3 = plt.subplots()
sns.lineplot(data=daily_orders_df, x='order_purchase_timestamp', y='revenue', ax=ax3)
ax3.set_xlabel('Date')
ax3.set_ylabel('Revenue')
plt.xticks(rotation=45)
st.pyplot(fig3)

st.subheader('RFM Distribution')

fig4, ax4 = plt.subplots()
sns.histplot(rfm_df['recency'], bins=20, kde=True, ax=ax4)
ax4.set_title('Recency Distribution', fontsize=16)  # Menambahkan judul untuk distribusi recency
ax4.set_xlabel('Recency (days)')
ax4.set_ylabel('Count')
st.pyplot(fig4)


# Mengatur layout dengan container
with st.container():
    # Mengatur layout kolom untuk visualisasi RFM
    col1, col2 = st.columns(2)

    # Visualisasi distribusi frequency
    with col1:
        fig_freq, ax_freq = plt.subplots(figsize=(6, 4))
        sns.histplot(rfm_df['frequency'], bins=30, kde=True, ax=ax_freq)
        ax_freq.set_title('Frequency Distribution', fontsize=16)
        ax_freq.set_xlabel('Purchase Frequency', fontsize=12)
        ax_freq.set_ylabel('Frequency', fontsize=12)
        st.pyplot(fig_freq)

    # Visualisasi distribusi monetary
    with col2:
        fig_mon, ax_mon = plt.subplots(figsize=(6, 4))
        sns.histplot(rfm_df['monetary'], bins=30, kde=True, ax=ax_mon)
        ax_mon.set_xlim(0, 1000) 
        ax_mon.set_title('Monetary Distribution', fontsize=16)
        ax_mon.set_xlabel('Total Money Spent', fontsize=12)
        ax_mon.set_ylabel('Frequency', fontsize=12)
        st.pyplot(fig_mon)
