import streamlit as st
import google.generativeai as genai
import pandas as pd
import os
import json
from PIL import Image

# Konfigurasi halaman web Streamlit
st.set_page_config(page_title="Aplikasi Scanner Nota AI", layout="centered")

st.title("🧾 Aplikasi Scanner Nota Otomatis dengan AI")
st.write("Unggah foto nota atau struk belanja Anda di bawah ini, dan AI akan merapikannya ke dalam tabel secara otomatis!")

# Mengambil API Key secara aman dari Streamlit Secrets
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception as e:
    st.error("API Key belum diatur di Streamlit Secrets! Silakan atur terlebih dahulu di menu Settings > Secrets.")
    st.stop()

# Konfigurasi kunci menggunakan library google-generativeai yang stabil
genai.configure(api_key=API_KEY)

def proses_nota_dengan_ai(uploaded_file):
    # Menggunakan model stabil gemini-1.5-flash
    model = genai.GenerativeModel('gemini-1.5-flash')
    image = Image.open(uploaded_file)
    
    prompt = """
    Analisis foto nota/struk belanja ini dan ekstrak informasi berikut ke dalam format JSON dengan kunci (keys):
    - "nama_toko": (Nama toko/perusahaan)
    - "tanggal_jam": (Tanggal dan jam transaksi pada nota)
    - "daftar_barang": (Rincian nama barang, jumlah/qty, dan harga satuan/total dalam satu teks yang rapi)
    - "total_nota": (Total harga keseluruhan belanjaan, ambil angka murninya saja)
    
    Berikan HANYA format JSON murni tanpa teks pengantar atau blok markdown lainnya.
    """
    
    response = model.generate_content([image, prompt])
    teks_res = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(teks_res)

# Tombol Upload Foto di Web
uploaded_file = st.file_uploader("Pilih atau Ambil Foto Nota (JPG/PNG)", type=["jpg", "jpeg", "png"])

nama_file_excel = "hasil_nota_ai.xlsx"

if uploaded_file is not None:
    st.image(uploaded_file, caption="Foto Nota yang Diunggah", use_container_width=True)
    
    if st.button("🚀 Proses Nota Sekarang"):
        with st.spinner("Sedang memproses nota dengan AI... Mohon tunggu..."):
            try:
                # 1. Ekstrak data via AI
                data_dict = proses_nota_dengan_ai(uploaded_file)
                
                # 2. Format total_nota menjadi angka asli (float/int)
                raw_total = str(data_dict.get("total_nota", "0"))
                bersih_angka = ''.join(c for c in raw_total if c.isdigit() or c in ['.', ','])
                bersih_angka = bersih_angka.replace(',', '.')
                try:
                    data_dict["total_nota"] = float(bersih_angka) if '.' in bersih_angka else int(bersih_angka)
                except:
                    data_dict["total_nota"] = 0
                    
                data_dict["waktu_scan_sistem"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 3. Simpan ke file Excel
                df_baru = pd.DataFrame([data_dict])
                if os.path.exists(nama_file_excel):
                    df_existing = pd.read_excel(nama_file_excel)
                    df_combined = pd.concat([df_existing, df_baru], ignore_index=True)
                    df_combined.to_excel(nama_file_excel, index=False)
                else:
                    df_baru.to_excel(nama_file_excel, index=False)
                
                st.success("Data berhasil diekstrak dan disimpan ke Excel!")
                
                st.subheader("Hasil Ekstraksi Terakhir:")
                st.json(data_dict)
                
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")

# Tombol untuk melihat atau mengunduh file Excel hasil rekap
if os.path.exists(nama_file_excel):
    st.markdown("---")
    st.subheader("📊 Riwayat Rekap Excel")
    df_tampil = pd.read_excel(nama_file_excel)
    st.dataframe(df_tampil)
    
    with open(nama_file_excel, "rb") as f:
        st.download_button(
            label="📥 Download File Excel (`hasil_nota_ai.xlsx`)",
            data=f,
            file_name="hasil_nota_ai.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
