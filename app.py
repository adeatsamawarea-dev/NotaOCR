import streamlit as st
import google.generativeai as genai
import pandas as pd
import os
import json
from PIL import Image

st.set_page_config(page_title="Aplikasi Scanner Nota AI", layout="centered")

st.title("🧾 Aplikasi Scanner Nota Otomatis dengan AI")
st.write("Unggah foto nota atau struk belanja Anda di bawah ini, dan AI akan merapikannya ke dalam tabel secara otomatis!")

# Mengambil API Key secara aman dari Streamlit Secrets
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)

def proses_nota_dengan_ai(uploaded_file):
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

# (Sisa kode ke bawah dibiarkan sama seperti sebelumnya...)
