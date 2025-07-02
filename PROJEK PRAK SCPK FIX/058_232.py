# INFO: PROJEK PRAKTIKUM SCPK - WP : PREDIKSI RISIKO CEDERA (IF F)
# - Cindy Nabella S (058)
# - Fara Katty S (232)


# ---- import library ----
import streamlit as st # web app interaktir
import pandas as pd # manipulasi data tabel
import numpy as np # operasi numerik
import matplotlib.pyplot as plt # grafik
from io import BytesIO #excel export
from fpdf import FPDF # pdf export

# ---- CONFIG (set konfigurasi hal streamlit) ----
st.set_page_config(page_title="Injury Risk App", layout="wide")
st.title("\U0001F3E5 Injury Risk Level Assessment")
st.markdown("**Created by:**  \n- **Cindy Nabella S** / 123230058 / IF-F  \n- **Fara Katty** / 123230232 / IF-F")


# ---- LOAD DATA ----
df = pd.read_csv("injury_data.csv")
df.insert(0, "Person", [f"Person {i+1}" for i in range(len(df))])
a = df["Person"].tolist()
criteria_names = list(df.columns[1:])
criteria_labels = [
    "Player Age (years)",         
    "Player Weight (kg)",         
    "Player Height (cm)",         
    "Previous Injuries (count)",  
    "Training Intensity (scale)", 
    "Recovery Time (days)",       
    "Likelihood of Injury"    
]

for i, label in enumerate(criteria_labels):
    df.rename(columns={criteria_names[i]: label}, inplace=True)
criteria_names = np.array(criteria_labels)
x = np.array(df.iloc[:, 1:], dtype=float)
x[x == 0] = 0.0001

# ---- COST/BENEFIT ----
k = [-1, -1, 1, -1, 1, -1, -1]
cb = ["Cost" if val == -1 else "Benefit" for val in k]
criteria_df = pd.DataFrame({"Criteria": criteria_names, "Cost/Benefit": cb})


# ---- MENU (sidebar navigasi utk pilihan halaman) ----
from streamlit_option_menu import option_menu

with st.sidebar:
    selected = option_menu(
        menu_title="Navigation",
        options=["Home", "Dataset Preview", "Set Weights", "Result & Ranking", "Visualization", "Export Result", "About Project"],
        icons=["house", "folder", "gear", "trophy", "bar-chart", "download", "info-circle"],
        default_index=0,
        orientation="vertical"  
    )


# ---- STATE (user input bobot manual di sidebar) ----
if "weights" not in st.session_state:
    st.session_state.weights = [0.0 for _ in range(len(criteria_names))]
# Note:
# - Menyimpan bobot kriteria secara global di session_state agar bobot tidak hilang saat rerun
# - Inisialisasi bobot semua kriteria ke 0


# ================== HALAMAN ==================
# ---- 1. HOME ----
if selected == "Home":
    st.image("risk.jpg", use_container_width=True)
    st.subheader("\U0001F9E0 Injury Risk Prediction")
    st.markdown("""
    Welcome to the Injury Risk Assessment Tool. This application uses the **Weighted Product method** to evaluate the risk level of injury for each player based on multiple criteria.
    """)


# ---- 2. DATASET PREVIEW (Menampilkan data asli yang sudah dimodifikasi (nilai 0 diganti 0.0001) dalam bentuk tabel) ----
elif selected == "Dataset Preview":
    st.subheader("\U0001F4C1 Dataset Preview")
    st.write("This page displays the initial dataset. Zero values have been replaced with 0.0001 to prevent errors during calculations (such as division by zero).")
    st.dataframe(df)
    st.info("Zero values have been replaced with 0.0001.") # mengganti 0 dengan 0.0001
    

# ---- 3. SET WEIGHTS (user input bobot manual di sidebar) ----
elif selected == "Set Weights":
    st.subheader("\u2699\ufe0f Set Weights for Each Criterion")
    st.markdown("""
    - This page allows you to manually assign weights to each criterion using the sidebar on the left.<br>
    - Weights represent the importance level of each criterion and range from 0 to 10.<br>
    - Please adjust the weights according to your preferences or analysis needs. The total weight must not be zero in order to proceed.
    """, unsafe_allow_html=True)

    # Bobot antara 0 - 10
    st.sidebar.subheader("Set Weight (0–10) for:")

    labels = criteria_names.tolist()
    w = []

    for i, label in enumerate(labels):
        weight = st.sidebar.number_input(
            label,
            min_value=0.0,
            max_value=10.0,
            value=st.session_state.weights[i],
            step=1.0,
            key=f"weight_{i}"
        )
        w.append(weight)

    # Update session_state hanya jika ada perubahan supaya tidak overwrite saat rerun
    if w != st.session_state.weights:
        st.session_state.weights = w

    # Tabel Cost/Benefit
    st.markdown("### \U0001F4C4 Cost/Benefit Information")
    st.dataframe(criteria_df)

    # Validasi agar total bobot tidak boleh 0
    # if sum(w) == 0 or all(value !=0 for value in w):
    #     st.error("Total weight is 0. Please input at least one non-zero weight.")
    # else:
    #     st.success("Weights are valid. Continue to **Result & Ranking**.")

    if all(value !=0 for value in w):
        st.success("Weights are valid. Continue to **Result & Ranking**.")
    else:
        st.error("Weights are not fully entered. Please enter the weight for each criterion.")


# ---- 4. RESULT & RANKING ----
elif selected == "Result & Ranking":
    st.subheader("\U0001F4CA Injury Risk Scores & Ranking")
    st.markdown("""
    This page displays the final results of the injury risk assessment using the **Weighted Product** method. The scores are calculated based on the weights you previously assigned to each criterion.

    - The **Score** value represents the injury risk level of each individual.
    - A higher score indicates a higher potential risk of injury.
    - Results are ranked from highest to lowest score.
    
    You can also:
    - View the **Top 3** individuals with the highest injury risk.
    - Use the **slider** to filter the list by a specific risk score threshold.
    """, unsafe_allow_html=True)


    w = st.session_state.weights
    if sum(w) == 0:
        st.warning("Please set the weights first.")
        st.stop()
        
    # Menghitung skor risiko injury dengan Weighted Product method:
    # - Normalisasi bobot
    w_norm = [c / sum(w) for c in w]
    m = len(a)
    
    # Perhitungan skor untuk tiap person i
    s = [1] * m
    for i in range(m):
        for j in range(len(w)):
            s[i] *= x[i][j] ** (k[j] * w_norm[j])
    
    # Perhitungan eigen value
    v = [val / sum(s) for val in s]

    # Menampilkan tabel hasil dengan skor dan ranking
    result_df = pd.DataFrame({"Person": a, "Score": v})
    result_df = result_df.sort_values(by="Score", ascending=False).reset_index(drop=True)
    st.dataframe(result_df)
    
    # Menampilkan top 3 person dengan risiko tertinggi
    st.markdown("### \U0001F3C6 Top 3 Highest Risk")
    st.table(result_df.head(3))

    # Filter Kategori berdasarka skor min
    # st.markdown("### \U0001F50D Filter by Score Category")
    # kategori = st.slider("Show entries with risk score greater than:", 0.0, 1.0, 0.0, 0.01)
    # st.dataframe(result_df[result_df["Score"] > kategori])


# ---- 5. VISUALIZATION (chart) ----
elif selected == "Visualization":
    st.subheader("\U0001F4C8 Risk Score Visualization")
    st.markdown("""
    In this section, you can **visually explore the injury risk scores** for each individual in the dataset. The bar chart gives a quick comparison of scores across all individuals, making it easy to identify those with higher risk.

    Make sure to set the weights first in the **Set Weights** section to ensure the results and charts reflect your chosen importance levels.
    """)

    # Chart 1: Risiko injury tiap individu.
    w = st.session_state.weights
    if sum(w) == 0:
        st.warning("Please set the weights first.")
        st.stop()

    w_norm = [c / sum(w) for c in w]
    s = [1] * len(a)
    for i in range(len(a)):
        for j in range(len(w)):
            s[i] *= x[i][j] ** (k[j] * w_norm[j])
    v = [val / sum(s) for val in s]

    result_df = pd.DataFrame({"Person": a, "Score": v})
    result_df = result_df.sort_values(by="Score", ascending=False)
    st.bar_chart(data=result_df.set_index("Person")['Score'])
    
    st.info("""
    **Explanation of the chart:**  
    - **Risk Score Visualization:** This bar chart shows the overall risk scores of all individuals, allowing you to quickly identify who has the highest injury risk in the group.  """)
    # - **Individual Criteria Comparison:** This chart displays the contribution of each criterion to the selected person's risk score, helping you understand which factors influence their risk level the most.
    # """)
    

    # Chart 2: Grafik perbandingan nilai kriteria dari person yang dipilih
    # st.markdown("### \U0001F4CA Individual Criteria Comparison")
    # selected_person = st.selectbox("Select a Person", df["Person"])
    # person_data = df[df["Person"] == selected_person].iloc[:, 1:]
    # st.bar_chart(person_data.T)
    # st.info("""
    # **ℹ️ How to read the chart above:**

    # - The **X-axis** shows the names of the **criteria** being evaluated.
    # - The **Y-axis** represents the **input values** of the selected person for each criterion.
    # """)
    
    # a. Grafik 1:
    # - Tujuan: Menampilkan peringkat keseluruhan risiko dari semua individu.
    # - Sumbu X: Nama orang (Person)
    # - Sumbu Y: Nilai skor risiko (Risk Score)
    # - Makna: Semakin tinggi bar, semakin tinggi tingkat risiko orang tersebut dibandingkan yang lain.
    # - Kapan digunakan: Untuk melihat siapa yang berisiko paling tinggi secara keseluruhan.
    
    # b. Grafik 2:
    # - Tujuan: Menampilkan nilai input per kriteria dari satu orang yang dipilih.
    # - Sumbu X: Nama-nama kriteria (misalnya usia, riwayat cedera, latihan, dll)
    # - Sumbu Y: Nilai input untuk tiap kriteria dari orang tersebut
    # - Makna: menunjukkan faktor-faktor apa saja yang berkontribusi pada risiko individu tersebut.
    # - Kapan digunakan: Untuk menganalisis lebih dalam penyebab skor risiko dari satu orang tertentu.


# ---- 6. EXPORT RESULT ----
elif selected == "Export Result":
    st.subheader("\U0001F4BE Export Result")
    st.markdown("""
    ### How to use Export Result
    This section allows you to download the injury risk scores for all individuals in convenient file formats. 
    After the scores are calculated based on the set weights, you can export the results as an Excel spreadsheet or a PDF report.

    - **Excel Export:** Downloads a file containing the full list of individuals and their risk scores, sorted from highest to lowest.
    - **PDF Export:** Downloads a formatted PDF report listing each person and their corresponding risk score.

    This feature helps you save and share the risk assessment results easily for further analysis or record-keeping.
    """)

    w = st.session_state.weights
    if sum(w) == 0:
        st.warning("Please set the weights first.")
        st.stop()

    w_norm = [c / sum(w) for c in w]
    s = [1] * len(a)
    for i in range(len(a)):
        for j in range(len(w)):
            s[i] *= x[i][j] ** (k[j] * w_norm[j])
    v = [val / sum(s) for val in s]
    result_df = pd.DataFrame({"Person": a, "Score": v}).sort_values(by="Score", ascending=False)

    # Export to Excel
    buffer = BytesIO()
    result_df.to_excel(buffer, index=False)
    st.download_button("Download as Excel", buffer.getvalue(), file_name="injury_risk_result.xlsx")

    # Export to PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Injury Risk Report", ln=True, align='C')

    for i, row in result_df.iterrows():
        pdf.cell(200, 10, txt=f"{row['Person']}: {row['Score']:.4f}", ln=True)

    pdf_output = pdf.output(dest='S').encode('latin1')  # Keluarkan sebagai string, lalu encode ke bytes
    st.download_button("Download as PDF", data=pdf_output, file_name="injury_risk_result.pdf", mime="application/pdf")


# ---- 7. ABOUT ----
elif selected == "About Project":
    st.subheader("\U0001F4D8 About This Project")
    st.markdown("""
    - **Title**: Injury Risk Level Assessment
    - **Method**: Weighted Product
    - **Developers**: Cindy Nabella S & Fara Katty
    - **Input**: Player attributes
    - **Output**: Ranked injury risk scores with visualization and export
    
    **Flow**:
    1. Load dataset
    2. Set importance weights
    3. Calculate risk ranking
    4. View results, filter, and export
    """)