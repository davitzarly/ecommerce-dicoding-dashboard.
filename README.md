# E-Commerce Public Dataset Dashboard (Dicoding Submission)

Proyek ini berisi analisis data komprehensif dan dashboard interaktif berbasis **Streamlit** menggunakan **E-Commerce Public Dataset (Olist)**. 

## 🌟 Fitur & Pembaruan Utama

1. **Prinsip Visualisasi Data (Anti-Distract)**
   - Menggunakan warna tunggal/monochromatic (*highlighting* kategori teratas dengan warna utama, kategori lain dengan warna netral) untuk mencegah distraksi visual sesuai prinsip McCandless & Dicoding.
2. **Analisis Lanjutan (Tanpa Machine Learning)**
   - **RFM Analysis**: Mengukur Recency (hari sejak transaksi terakhir), Frequency (jumlah order), dan Monetary (total spending).
   - **Geospatial Analysis**: Menganalisis sebaran pelanggan dan transaksi di provinsi-provinsi (states) Brasil.
   - **Clustering / Binning**: Pengelompokan manual *Spending Tier* (Low, Medium, High Spenders) dan *Delivery Performance*.
3. **Peningkatan Interaktivitas Dashboard**
   - **Multi-filter Sidebar**: Tanggal pembelian (dengan penanganan error `try-except`), status order, provinsi (*customer state*), metode pembayaran (*payment type*), dan kategori produk.
   - **Tab Navigation**: `📊 Main Analysis`, `📈 RFM Analysis`, `🗺️ Geospatial Analysis`, dan `🧩 Customer Binning`.
4. **Tautan Deploy Dashboard**
   - Link aplikasi Streamlit Cloud tersimpan di file `url.txt`.

---

## 📁 Struktur Direktori

```text
E-commerce-public-dataset/
├── dashboard.py                           # Kode aplikasi Streamlit Dashboard
├── Proyek_Analisis_Data.ipynb             # Jupyter Notebook Analisis Data (Lengkap Output)
├── url.txt                                # Tautan deployment Streamlit Cloud
├── README.md                              # Dokumentasi proyek
├── requirements.txt                      # List dependensi Python
├── customers_dataset.csv                 # Data pelanggan
├── geolocation_dataset.csv               # Data lokasi geofrafis
├── order_items_dataset.csv               # Data barang pesanan
├── order_payments_dataset.csv            # Data pembayaran pesanan
├── order_reviews_dataset.csv             # Data ulasan pesanan
├── orders_dataset.csv                    # Data transaksi pesanan
├── product_category_name_translation.csv # Terjemahan kategori produk
├── products_dataset.csv                  # Data produk
└── sellers_dataset.csv                   # Data penjual
```

---

## 🚀 Cara Menjalankan Dashboard

1. **Install Dependensi**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Jalankan Aplikasi Streamlit**:
   ```bash
   streamlit run dashboard.py
   ```

3. Buka browser pada alamat yang muncul (default: `http://localhost:8501`).