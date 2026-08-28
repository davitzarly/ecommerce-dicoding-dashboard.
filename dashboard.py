import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from pathlib import Path

# Streamlit Page Config
st.set_page_config(
    page_title='E-Commerce Public Dataset Analysis',
    page_icon='🛍️',
    layout='wide'
)

# Custom Styling / CSS for Clean UI
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-box {
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 12px;
        border: 1px solid #E2E8F0;
    }
    </style>
""", unsafe_allow_html=True)

# Seaborn Theme
sns.set_theme(style='whitegrid')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#CBD5E1'
plt.rcParams['axes.linewidth'] = 0.8

@st.cache_data
def load_data():
    base_path = Path(__file__).resolve().parent

    orders = pd.read_csv(
        base_path / 'orders_dataset.csv',
        parse_dates=[
            'order_purchase_timestamp',
            'order_approved_at',
            'order_delivered_carrier_date',
            'order_delivered_customer_date',
            'order_estimated_delivery_date',
        ],
    )
    order_items = pd.read_csv(base_path / 'order_items_dataset.csv')
    products = pd.read_csv(base_path / 'products_dataset.csv')
    category_trans = pd.read_csv(base_path / 'product_category_name_translation.csv')
    reviews = pd.read_csv(base_path / 'order_reviews_dataset.csv')
    customers = pd.read_csv(base_path / 'customers_dataset.csv')
    payments = pd.read_csv(base_path / 'order_payments_dataset.csv')

    # Merge items with product categories
    items = order_items.merge(products, on='product_id', how='left')
    items = items.merge(category_trans, on='product_category_name', how='left')
    items['category'] = (
        items['product_category_name_english']
        .fillna(items['product_category_name'])
        .fillna('unknown')
    )

    # Merge orders with customers and payments
    orders_df = orders.merge(customers, on='customer_id', how='left')
    
    # Primary payment type per order
    payments_primary = payments.groupby('order_id').agg({
        'payment_type': lambda x: x.iloc[0],
        'payment_value': 'sum'
    }).reset_index()

    orders_df = orders_df.merge(payments_primary, on='order_id', how='left')
    orders_df['payment_type'] = orders_df['payment_type'].fillna('unknown')

    return orders_df, items, reviews

# Load datasets
orders, items, reviews = load_data()

# Page Title & Header
st.markdown('<div class="main-header">🛍️ E-Commerce Public Dataset Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Analisis Performa Penjualan, Kepuasan Pelanggan, RFM & Geospatial (Olist E-Commerce)</div>', unsafe_allow_html=True)

# Date Range Helpers
min_date = orders['order_purchase_timestamp'].min().date()
max_date = orders['order_purchase_timestamp'].max().date()

# SIDEBAR FILTERS
with st.sidebar:
    st.header('🔍 Filter Data')
    
    # Try-Except Block for Robust Date Input Handling
    try:
        date_input_res = st.date_input(
            'Rentang Tanggal Pembelian',
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
        if isinstance(date_input_res, (list, tuple)) and len(date_input_res) == 2:
            start_date, end_date = date_input_res
        elif isinstance(date_input_res, (list, tuple)) and len(date_input_res) == 1:
            start_date = end_date = date_input_res[0]
        else:
            start_date, end_date = min_date, max_date
    except Exception as e:
        start_date, end_date = min_date, max_date

    # Status Order Filter
    status_options = sorted(orders['order_status'].dropna().unique())
    selected_status = st.multiselect(
        'Status Order',
        options=status_options,
        default=['delivered'] if 'delivered' in status_options else status_options,
    )

    # State (Provinsi) Filter
    state_options = ['Semua Provinsi'] + sorted(orders['customer_state'].dropna().unique().tolist())
    selected_states = st.multiselect(
        'Provinsi (State)',
        options=state_options,
        default=['Semua Provinsi']
    )

    # Payment Method Filter
    payment_options = ['Semua Metode'] + sorted(orders['payment_type'].dropna().unique().tolist())
    selected_payments = st.multiselect(
        'Metode Pembayaran',
        options=payment_options,
        default=['Semua Metode']
    )

    # Category Filter
    all_categories = ['Semua Kategori'] + sorted(items['category'].dropna().unique().tolist())
    selected_categories = st.multiselect(
        'Kategori Produk',
        options=all_categories,
        default=['Semua Kategori']
    )

# APPLY FILTERS TO ORDERS
filtered_orders = orders[
    (orders['order_purchase_timestamp'].dt.date >= start_date) &
    (orders['order_purchase_timestamp'].dt.date <= end_date)
]

if selected_status:
    filtered_orders = filtered_orders[filtered_orders['order_status'].isin(selected_status)]

if selected_states and 'Semua Provinsi' not in selected_states:
    filtered_orders = filtered_orders[filtered_orders['customer_state'].isin(selected_states)]

if selected_payments and 'Semua Metode' not in selected_payments:
    filtered_orders = filtered_orders[filtered_orders['payment_type'].isin(selected_payments)]

# Filter items based on filtered orders
items_filtered = items[items['order_id'].isin(filtered_orders['order_id'])]

if selected_categories and 'Semua Kategori' not in selected_categories:
    items_filtered = items_filtered[items_filtered['category'].isin(selected_categories)]
    filtered_orders = filtered_orders[filtered_orders['order_id'].isin(items_filtered['order_id'])]

# METRICS OVERVIEW
col1, col2, col3, col4, col5 = st.columns(5)

total_orders_cnt = len(filtered_orders)
total_revenue = items_filtered['price'].sum() if not items_filtered.empty else 0.0
avg_order_val = total_revenue / total_orders_cnt if total_orders_cnt > 0 else 0.0

orders_reviews = filtered_orders.merge(reviews[['order_id', 'review_score']], on='order_id', how='left')
delivered_df = orders_reviews[orders_reviews['order_status'] == 'delivered'].copy()
delivered_df = delivered_df.dropna(subset=['order_delivered_customer_date', 'order_estimated_delivery_date'])

if not delivered_df.empty:
    delivered_df['delay_days'] = (
        delivered_df['order_delivered_customer_date'] - delivered_df['order_estimated_delivery_date']
    ).dt.days
    delivered_df['is_delayed'] = delivered_df['delay_days'] > 0
    delay_rate = delivered_df['is_delayed'].mean() * 100
    avg_review = delivered_df['review_score'].mean()
else:
    delay_rate = 0.0
    avg_review = float('nan')

col1.metric('📦 Total Order', f"{total_orders_cnt:,}")
col2.metric('💰 Total Revenue', f"R$ {total_revenue:,.2f}")
col3.metric('🛒 Avg Order Value', f"R$ {avg_order_val:,.2f}")
col4.metric('⚠️ Delay Rate', f"{delay_rate:.2f}%")
col5.metric('⭐ Avg Review Score', f"{avg_review:.2f}" if pd.notna(avg_review) else '-')

st.markdown("---")

# DASHBOARD TABS
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Main Analysis", 
    "📈 RFM Analysis", 
    "🗺️ Geospatial Analysis", 
    "🧩 Customer Binning"
])

# TAB 1: MAIN BUSINESS QUESTIONS
with tab1:
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Top 10 Kategori Produk Berdasarkan Revenue")
        st.caption("Penerapan Prinsip Anti-Distract: Warna tunggal/monochromatic untuk kejernihan informasi.")
        
        if items_filtered.empty:
            st.warning("Tidak ada data transaksi pada filter yang dipilih.")
        else:
            rev_cat = (
                items_filtered.groupby('category')['price']
                .sum()
                .sort_values(ascending=False)
                .head(10)
                .reset_index()
            )

            fig1, ax1 = plt.subplots(figsize=(7, 4.5))
            # Single monochromatic color palette to prevent visual distraction
            colors = ['#1f77b4' if i == 0 else '#8cb8d8' for i in range(len(rev_cat))]
            
            bars = ax1.barh(rev_cat['category'][::-1], rev_cat['price'][::-1] / 1e3, color=colors[::-1])
            ax1.set_xlabel("Total Revenue (R$ Ribu)", fontsize=10)
            ax1.set_ylabel("Kategori Produk", fontsize=10)

            for bar in bars:
                w = bar.get_width()
                ax1.text(w + 1, bar.get_y() + bar.get_height()/2, f'R$ {w:.1f}k', va='center', fontsize=8, color='#333333')

            ax1.set_xlim(0, max(rev_cat['price'] / 1e3) * 1.15)
            st.pyplot(fig1, clear_figure=True)

    with col_chart2:
        st.subheader("Skor Ulasan vs Status Pengiriman")
        st.caption("Membandingkan distribusi skor ulasan antara pesanan tepat waktu vs terlambat.")
        
        if delivered_df.empty:
            st.warning("Tidak ada data pesanan delivered pada filter yang dipilih.")
        else:
            delivered_df['status_pengiriman'] = np.where(
                delivered_df['delay_days'] > 0,
                'Terlambat',
                'Tepat Waktu / Lebih Cepat'
            )

            fig2, ax2 = plt.subplots(figsize=(6, 4.5))
            palette_status = {'Tepat Waktu / Lebih Cepat': '#2e7d32', 'Terlambat': '#c62828'}
            
            sns.boxplot(
                data=delivered_df,
                x='status_pengiriman',
                y='review_score',
                palette=palette_status,
                width=0.4,
                ax=ax2
            )
            ax2.set_xlabel("Status Pengiriman", fontsize=10)
            ax2.set_ylabel("Skor Ulasan (1 - 5)", fontsize=10)
            st.pyplot(fig2, clear_figure=True)

# TAB 2: RFM ANALYSIS
with tab2:
    st.subheader("📈 Analisis RFM (Recency, Frequency, Monetary)")
    st.markdown("""
        Analisis RFM mengelompokkan pelanggan berdasarkan 3 faktor utama:
        - **Recency**: Hari sejak transaksi terakhir.
        - **Frequency**: Jumlah transaksi.
        - **Monetary**: Total pengeluaran (R$).
    """)

    if filtered_orders.empty or items_filtered.empty:
        st.warning("Data tidak cukup untuk melakukan analisis RFM.")
    else:
        # RFM Computation
        rfm_orders = filtered_orders[filtered_orders['order_status'] == 'delivered'].merge(
            items_filtered[['order_id', 'price']], on='order_id', how='left'
        )
        
        if rfm_orders.empty:
            st.warning("Tidak ada order berstatus delivered untuk Analisis RFM.")
        else:
            max_date_rfm = rfm_orders['order_purchase_timestamp'].max()
            
            rfm_df = rfm_orders.groupby('customer_unique_id').agg({
                'order_purchase_timestamp': lambda x: (max_date_rfm - x.max()).days,
                'order_id': 'nunique',
                'price': 'sum'
            }).reset_index()
            rfm_df.columns = ['customer_unique_id', 'Recency', 'Frequency', 'Monetary']

            rfm_col1, rfm_col2, rfm_col3 = st.columns(3)
            rfm_col1.metric("Rata-Rata Recency", f"{rfm_df['Recency'].mean():.1f} Hari")
            rfm_col2.metric("Rata-Rata Frequency", f"{rfm_df['Frequency'].mean():.2f} Transaksi")
            rfm_col3.metric("Rata-Rata Monetary", f"R$ {rfm_df['Monetary'].mean():,.2f}")

            # Plot RFM Distributions
            fig_rfm, ax_rfm = plt.subplots(1, 3, figsize=(15, 4))
            
            ax_rfm[0].hist(rfm_df['Recency'], bins=25, color='#1f77b4', edgecolor='white')
            ax_rfm[0].set_title('Distribusi Recency (Hari)', fontweight='bold')
            ax_rfm[0].set_xlabel('Hari')

            ax_rfm[1].hist(rfm_df[rfm_df['Frequency'] <= 5]['Frequency'], bins=5, color='#1f77b4', edgecolor='white')
            ax_rfm[1].set_title('Distribusi Frequency (<= 5)', fontweight='bold')
            ax_rfm[1].set_xlabel('Transaksi')

            ax_rfm[2].hist(rfm_df[rfm_df['Monetary'] <= 1000]['Monetary'], bins=25, color='#1f77b4', edgecolor='white')
            ax_rfm[2].set_title('Distribusi Monetary (<= R$ 1000)', fontweight='bold')
            ax_rfm[2].set_xlabel('Total Spend (R$)')

            plt.tight_layout()
            st.pyplot(fig_rfm, clear_figure=True)

            st.markdown("### Top 10 Pelanggan Berdasarkan Monetary")
            top_monetary = rfm_df.sort_values('Monetary', ascending=False).head(10)
            st.dataframe(top_monetary, use_container_width=True)

# TAB 3: GEOSPATIAL ANALYSIS
with tab3:
    st.subheader("🗺️ Geospatial Analysis (Distribusi Pelanggan per Provinsi)")
    st.markdown("Menganalisis sebaran wilayah basis pelanggan berdasarkan provinsi (state) di Brasil.")

    if filtered_orders.empty:
        st.warning("Tidak ada data untuk analisis geografis.")
    else:
        state_summary = filtered_orders.groupby('customer_state').agg(
            Jumlah_Pelanggan=('customer_unique_id', 'nunique'),
            Total_Orders=('order_id', 'nunique')
        ).reset_index().sort_values('Jumlah_Pelanggan', ascending=False)

        col_geo1, col_geo2 = st.columns([3, 2])

        with col_geo1:
            fig_geo, ax_geo = plt.subplots(figsize=(8, 4.5))
            top_states = state_summary.head(10)
            colors_geo = ['#1f77b4' if i == 0 else '#8cb8d8' for i in range(len(top_states))]

            bars_geo = ax_geo.bar(top_states['customer_state'], top_states['Jumlah_Pelanggan'], color=colors_geo)
            ax_geo.set_title('Top 10 Provinsi (State) Berdasarkan Jumlah Pelanggan', fontweight='bold')
            ax_geo.set_xlabel('Provinsi (State)')
            ax_geo.set_ylabel('Jumlah Pelanggan')

            for bar in bars_geo:
                h = bar.get_height()
                ax_geo.text(bar.get_x() + bar.get_width()/2, h + 100, f'{h:,}', ha='center', fontsize=8)

            st.pyplot(fig_geo, clear_figure=True)

        with col_geo2:
            st.markdown("### Ringkasan Data Provinsi")
            st.dataframe(state_summary, height=300, use_container_width=True)

# TAB 4: CUSTOMER BINNING & SEGMENTATION
with tab4:
    st.subheader("🧩 Customer Binning & Segmentation (Manual Grouping)")
    st.markdown("Mengelompokkan data ke dalam kategori bisnis tanpa algoritma Machine Learning.")

    if not delivered_df.empty and 'rfm_df' in locals() and not rfm_df.empty:
        col_bin1, col_bin2 = st.columns(2)

        with col_bin1:
            st.markdown("### 1. Spending Tier Binning")
            bins_spend = [0, 100, 500, np.inf]
            labels_spend = ['Low Spender (< R$100)', 'Medium Spender (R$100-500)', 'High Spender (> R$500)']
            
            rfm_df['Spending_Tier'] = pd.cut(rfm_df['Monetary'], bins=bins_spend, labels=labels_spend)
            spend_counts = rfm_df['Spending_Tier'].value_counts().reset_index()
            spend_counts.columns = ['Spending_Tier', 'Jumlah']

            fig_b1, ax_b1 = plt.subplots(figsize=(6, 4))
            bars_b1 = ax_b1.bar(spend_counts['Spending_Tier'], spend_counts['Jumlah'], color='#1f77b4')
            ax_b1.set_title('Segmen Pengeluaran Pelanggan', fontweight='bold')
            ax_b1.tick_params(axis='x', rotation=15)
            
            for bar in bars_b1:
                ax_b1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50, f'{bar.get_height():,}', ha='center', fontsize=8)

            st.pyplot(fig_b1, clear_figure=True)

        with col_bin2:
            st.markdown("### 2. Delivery Performance Binning")
            bins_del = [-np.inf, 0, 7, np.inf]
            labels_del = ['Tepat Waktu', 'Terlambat Ringan (1-7 hr)', 'Terlambat Parah (>7 hr)']
            
            delivered_df['Delay_Category'] = pd.cut(delivered_df['delay_days'], bins=bins_del, labels=labels_del)
            del_counts = delivered_df['Delay_Category'].value_counts().reset_index()
            del_counts.columns = ['Delay_Category', 'Jumlah']

            fig_b2, ax_b2 = plt.subplots(figsize=(6, 4))
            bars_b2 = ax_b2.bar(del_counts['Delay_Category'], del_counts['Jumlah'], color='#1f77b4')
            ax_b2.set_title('Kategori Performa Pengiriman', fontweight='bold')
            ax_b2.tick_params(axis='x', rotation=15)

            for bar in bars_b2:
                ax_b2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50, f'{bar.get_height():,}', ha='center', fontsize=8)

            st.pyplot(fig_b2, clear_figure=True)
    else:
        st.warning("Data tidak mencukupi untuk menampilkan binning.")

st.caption("Dashboard dikembangkan untuk submission Dicoding Analisis Data E-Commerce Public Dataset.")
