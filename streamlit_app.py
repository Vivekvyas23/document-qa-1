import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import io

st.set_page_config(page_title="Waveform Viewer", layout="wide")

st.title("📈 Waveform Viewer (WFM / CSV)")

uploaded_file = st.file_uploader("Upload your WFM or CSV file", type=["wfm", "csv"])

if uploaded_file is not None:
    filename = uploaded_file.name.lower()

    # --- CASE 1: CSV ---
    if filename.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        st.success(f"Loaded {len(df)} rows from CSV file.")
        st.write(df.head())

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df.iloc[:, 0], df.iloc[:, 1], color="blue", linewidth=1)
        ax.set_xlabel(df.columns[0])
        ax.set_ylabel(df.columns[1])
        ax.set_title("Waveform Visualization")
        ax.grid(True)
        st.pyplot(fig)

    # --- CASE 2: WFM ---
    elif filename.endswith(".wfm"):
        st.info("Reading WFM file...")

        data = uploaded_file.read()

        # Skip text header
        ascii_part = re.match(b'[\x20-\x7E\r\n\t]+', data)
        header_end = len(ascii_part.group(0)) if ascii_part else 512
        payload = data[header_end:]

        dtype = np.float32
        size = len(payload) // np.dtype(dtype).itemsize
        usable = payload[: size * np.dtype(dtype).itemsize]
        values = np.frombuffer(usable, dtype=dtype)

        if len(values) % 2 != 0:
            values = values[:-1]

        pairs = values.reshape(-1, 2)
        time = pairs[:, 0]
        amplitude = pairs[:, 1]
        df = pd.DataFrame({"Time (s)": time, "Amplitude (V)": amplitude})

        st.success(f"Decoded {len(df)} waveform samples from WFM file.")
        st.write(df.head())

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(time, amplitude, color="blue", linewidth=1)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude (V)")
        ax.set_title("Waveform Visualization")
        ax.grid(True)
        st.pyplot(fig)

        # Option to download as CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="💾 Download as CSV",
            data=csv_buffer.getvalue(),
            file_name="waveform_converted.csv",
            mime="text/csv",
        )

else:
    st.warning("Please upload a .wfm or .csv file to visualize.")
