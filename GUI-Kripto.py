import streamlit as st
import pandas as pd
from io import BytesIO
import numpy as np

# Customizing the Page Layout
st.set_page_config(page_title="S-Box Testing Tool", page_icon="\\U0001F3AE", layout="wide")

# Header Section
st.title("\U0001F4CA S-Box Testing Tool")
st.markdown(
    """
    #### Alat Analisis S-Box dari Kelompok 3
    Unggah file S-Box dan analisis dengan berbagai parameter kriptografi.\n
    Dibuat dengan cinta oleh:
    1. Hadid Ramadhan (4611422083)
    2. Nathandia Athallah Sugiharto	(4611422102)
    3. Syifa Maulida (4611422121)
    """
)

# Utility Functions
def hamming_weight(n):
    return bin(n).count('1')

def hamming_distance(a, b):
    return bin(a ^ b).count('1')

def calculate_nonlinearity(sbox):
    N = len(sbox)
    max_correlation = 0
    for a in range(1, N):
        for b in range(N):
            correlation = 0
            for x in range(N):
                wx = hamming_weight(x & a) % 2
                fx = hamming_weight(sbox[x % len(sbox)] & b) % 2
                correlation += (-1) ** (wx ^ fx)
            max_correlation = max(max_correlation, abs(correlation))
    return 128 - max_correlation // 2

def calculate_sac(sbox):
    total_changes = 0
    N = len(sbox)
    for x in range(N):
        for bit in range(8):
            flipped_input = x ^ (1 << bit)
            total_changes += hamming_distance(sbox[x], sbox[flipped_input])
    return total_changes / (N * 8 * 8)

def calculate_bic_sac(sbox):
    n = len(sbox)
    bit_length = 8
    total_pairs = 0
    total_independence = 0
    for i in range(bit_length):
        for j in range(i + 1, bit_length):
            independence_sum = 0
            for x in range(n):
                for bit_to_flip in range(bit_length):
                    flipped_x = x ^ (1 << bit_to_flip)
                    y1 = sbox[x]
                    y2 = sbox[flipped_x]
                    b1_i = (y1 >> i) & 1
                    b1_j = (y1 >> j) & 1
                    b2_i = (y2 >> i) & 1
                    b2_j = (y2 >> j) & 1
                    independence_sum += ((b1_i ^ b2_i) ^ (b1_j ^ b2_j))
            total_independence += independence_sum / (n * bit_length)
            total_pairs += 1
    return round(total_independence / total_pairs, 5) 

def calculate_lap(sbox):
    max_bias = 0
    N = len(sbox)
    for a in range(1, N):
        for b in range(1, N):
            bias = sum(1 for x in range(N) if (hamming_weight(x & a) % 2) == (hamming_weight(sbox[x] & b) % 2))
            max_bias = max(max_bias, abs(bias - N // 2))
    return max_bias / N

def calculate_dap(sbox):
    max_prob = 0
    N = len(sbox)
    for dx in range(1, N):
        counts = [0] * N
        for x in range(N):
            dy = sbox[x] ^ sbox[x ^ dx]
            counts[dy] += 1
        max_prob = max(max_prob, max(counts) / N)
    return max_prob

def calculate_bic_nl(sbox):
    N = len(sbox)
    max_correlation = 0
    for a in range(1, N):
        for b in range(N):
            correlation = 0
            for x in range(N):
                wx = hamming_weight(x & a) % 2
                fx = hamming_weight(sbox[x % len(sbox)] & b) % 2
                correlation += (-1) ** (wx ^ fx)
            max_correlation = max(max_correlation, abs(correlation))
    return max(0, 128 - max_correlation // 2)

# File Upload Section
st.sidebar.header("\U0001F4BE Upload File")
uploaded_file = st.sidebar.file_uploader("Unggah file S-Box (Excel)", type=["xls", "xlsx"])

if uploaded_file:
    try:
        # Displaying Uploaded Data
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        st.write("### Data yang Diunggah")
        st.dataframe(df)

        # Column Selection
        column = st.selectbox("Pilih Kolom untuk Analisis:", df.columns)
        sbox = df[column].dropna().astype(int).values 

        # Analysis Selection
        st.sidebar.header("\U0001F4D0 Pilih Operasi Analisis")
        operation = st.sidebar.selectbox("Operasi:", ["NL", "SAC", "LAP", "DAP", "BIC-SAC", "BIC-NL"])

        # Display Results
        st.write("### Hasil Analisis")
        with st.spinner("Sedang menghitung... Mohon tunggu sebentar"):
            if operation == "NL":
                result = calculate_nonlinearity(sbox)
            elif operation == "SAC":
                result = calculate_sac(sbox)
            elif operation == "LAP":
                result = calculate_lap(sbox)
            elif operation == "DAP":
                result = calculate_dap(sbox)
            elif operation == "BIC-SAC":
                result = calculate_bic_sac(sbox)
            elif operation == "BIC-NL":
                result = calculate_bic_nl(sbox)
            else:
                result = "Operasi belum didukung."

        st.success(f"Hasil ({operation}): {result}")

        # Export Results
        st.write("### Ekspor Hasil")
        output = BytesIO()
        result_df = pd.DataFrame({operation: [result]})
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            result_df.to_excel(writer, sheet_name="Hasil", index=False)
        data = output.getvalue()

        st.download_button(
            label="\U0001F4E5 Download Hasil sebagai Excel",
            data=data,
            file_name="hasil_operasi_sbox.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    except Exception as e:
        st.error(f"\U0001F6AB Gagal membaca file: {str(e)}")
else:
    st.info("\U0001F4DD Silakan unggah file untuk memulai analisis.")
