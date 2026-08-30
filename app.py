import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="FIRELINE - Kalimantan Wildfire Monitoring",
    layout="wide"
)

st.title("FIRELINE: Wildfire Monitoring & Population Impact Kalimantan")
st.caption("Monitoring Titik Panas NASA FIRMS VIIRS dan Analisis Kepadatan Populasi")

# 1. Load Data
try:
    df_firms = pd.read_csv("firms_kalimantan.csv")
    df_firms["acq_date"] = pd.to_datetime(df_firms["acq_date"])

    df_pop = pd.DataFrame({
        "Provinsi": ["KALIMANTAN BARAT", "KALIMANTAN SELATAN", "KALIMANTAN TIMUR", "KALIMANTAN TENGAH"],
        "Jumlah Penduduk": [4395983, 3626616, 3553143, 2212089],
        "Luas (km2)": [148338.72, 37362.52, 196837.11, 154496.71],
        "Kepadatan (jiwa/km2)": [29.63, 97.07, 18.05, 14.32]
    })
except Exception as e:
    st.error(f"Error pembacaan data: {e}")
    st.stop()

# 2. Sidebar Filter
st.sidebar.header("Pengaturan Filter")

min_date = df_firms["acq_date"].min().date()
max_date = df_firms["acq_date"].max().date()

date_range = st.sidebar.date_input(
    "Rentang Waktu Perekaman:",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Filter Confidence dengan label deskriptif
conf_labels = {"h": "High (Tinggi)", "n": "Nominal", "l": "Low (Rendah)"}
conf_options = sorted(list(df_firms["confidence"].dropna().unique()))
selected_conf = st.sidebar.multiselect(
    "Tingkat Kepercayaan (Confidence):",
    conf_options,
    default=conf_options,
    format_func=lambda x: conf_labels.get(x, x)
)

# Filter Waktu Lintasan dengan label deskriptif
daynight_labels = {"D": "Siang (Day)", "N": "Malam (Night)"}
daynight_options = sorted(list(df_firms["daynight"].dropna().unique()))
selected_daynight = st.sidebar.multiselect(
    "Waktu Lintasan Satelit:",
    daynight_options,
    default=daynight_options,
    format_func=lambda x: daynight_labels.get(x, x)
)

# Eksekusi Filter
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
    df_filtered = df_firms[
        (df_firms["acq_date"].dt.date >= start_date) &
        (df_firms["acq_date"].dt.date <= end_date) &
        (df_firms["confidence"].isin(selected_conf)) &
        (df_firms["daynight"].isin(selected_daynight))
    ]
else:
    df_filtered = df_firms

# 3. Baris 1: Ringkasan Metrik KPI
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
total_hotspot = len(df_filtered)
kritis_count = len(df_filtered[df_filtered["frp"] > 50]) if "frp" in df_filtered.columns else 0
avg_frp_val = df_filtered["frp"].mean() if ("frp" in df_filtered.columns and total_hotspot > 0) else 0
siang_pct = (len(df_filtered[df_filtered["daynight"] == "D"]) / total_hotspot * 100) if total_hotspot > 0 else 0

kpi1.metric("Total Titik Panas", f"{total_hotspot:,} Titik")
kpi2.metric("Hotspot Kritis (FRP > 50)", f"{kritis_count:,} Titik")
kpi3.metric("Rata-rata FRP", f"{avg_frp_val:.2f} MW")
kpi4.metric("Proporsi Siang Hari", f"{siang_pct:.1f}%")

st.markdown("---")

# 4. Baris 2: Visualisasi Spasial & Tren Waktu
col_peta, col_tren = st.columns([6, 4])

with col_peta:
    st.subheader("Peta Sebaran Titik Panas")
    if not df_filtered.empty and "latitude" in df_filtered.columns and "longitude" in df_filtered.columns:
        df_map_sample = df_filtered.sample(min(5000, len(df_filtered)), random_state=42)
        
        if hasattr(px, "scatter_map"):
            fig_map = px.scatter_map(
                df_map_sample,
                lat="latitude",
                lon="longitude",
                color="frp" if "frp" in df_map_sample.columns else None,
                size="frp" if "frp" in df_map_sample.columns else None,
                color_continuous_scale="Reds",
                size_max=12,
                zoom=4.5,
                center={"lat": -0.5, "lon": 114.5},
                map_style="carto-positron"
            )
        else:
            fig_map = px.scatter_mapbox(
                df_map_sample,
                lat="latitude",
                lon="longitude",
                color="frp" if "frp" in df_map_sample.columns else None,
                size="frp" if "frp" in df_map_sample.columns else None,
                color_continuous_scale="Reds",
                size_max=12,
                zoom=4.5,
                center={"lat": -0.5, "lon": 114.5},
                mapbox_style="carto-positron"
            )
            
        fig_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("Tidak ada titik panas pada filter yang dipilih.")

with col_tren:
    st.subheader("Tren Kemunculan Titik Panas")
    if not df_filtered.empty:
        df_daily = df_filtered.groupby("acq_date").size().reset_index(name="jumlah_titik")
        fig_trend = px.line(
            df_daily,
            x="acq_date",
            y="jumlah_titik",
            labels={"acq_date": "Tanggal", "jumlah_titik": "Jumlah Titik"},
            title="Frekuensi Titik Panas Harian"
        )
        st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")

# 5. Baris 3: Keterpaparan Populasi
st.subheader("Profil Kepadatan Populasi Wilayah (BPS)")
fig_pop_bar = px.bar(
    df_pop.sort_values(by="Kepadatan (jiwa/km2)", ascending=False),
    x="Provinsi",
    y="Kepadatan (jiwa/km2)",
    color="Kepadatan (jiwa/km2)",
    color_continuous_scale="Teal",
    text="Kepadatan (jiwa/km2)",
    title="Tingkat Kepadatan Penduduk per Wilayah"
)
fig_pop_bar.update_traces(textposition="outside")
st.plotly_chart(fig_pop_bar, use_container_width=True)

# 6. Baris 4: Tabel Operasional Prioritas Verifikasi
st.markdown("---")
st.subheader("Daftar Prioritas Titik Panas Berenergi Tinggi (FRP > 50 MW)")
if not df_filtered.empty and "frp" in df_filtered.columns:
    cols_to_show = [c for c in ["acq_date", "acq_time", "latitude", "longitude", "frp", "confidence", "daynight"] if c in df_filtered.columns]
    df_prioritas = df_filtered[df_filtered["frp"] > 50][cols_to_show].sort_values(by="frp", ascending=False)
    st.dataframe(df_prioritas.head(50), use_container_width=True)
else:
    st.write("Tidak ada data prioritas.")