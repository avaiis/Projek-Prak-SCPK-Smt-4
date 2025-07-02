import streamlit as st;
import pandas as pd
import numpy as np

st.title("Injury Risk Level")
st.write("Cindy Nabella S/123230058/IF-F n Fara K. S. A")

df = pd.read_csv("injury_data.csv")
st.subheader("Load data file csv")

df.insert(0, "Person", [f"Person {i+1}" for i in range(len(df))])
st.dataframe(df)

# ALTERNATIF
a = df["Person"].tolist()

# KRITERIA
criteria_names = np.array(df.columns[1:])

# MATRIKS KEPUTUSAN
x = np.array(df.iloc[:, 1:], dtype=float)
x[x == 0] = 0.0001

st.info("Zero values in the dataset have been replaced with 0.0001 to allow calculations involving negative weights.")


# COST BENEFIT PER KRITERIA
k = [-1, -1, 1, -1, 1, -1, -1]
cb = []

for i in range(len(k)):
    if k[i] == -1:
        cb.append("Cost")
    else:
        cb.append("Benefit")

st.subheader("Cost and Benefit of Each Criterion")
c = pd.DataFrame({
    "Criteria": criteria_names,
    "Cost/Benefit": cb
})

st.dataframe(c)


# BOBOT [PERKRITERIA]
st.sidebar.header("Input Weight of Each Criterion")

w_PlayerAge = st.sidebar.number_input("Player Age", 0.0, 10.0, 0.0, 1.0)
w_PlayerWeight = st.sidebar.number_input("Player Weight", 0.0, 10.0, 0.0, 1.0)
w_PlayerHeight = st.sidebar.number_input("Player Height", 0.0, 10.0, 0.0, 1.0)
w_PreviousInjuries = st.sidebar.number_input("Previous Injuries", 0.0, 10.0, 0.0, 1.0)
w_TrainingIntensity = st.sidebar.number_input("Training Intensity", 0.0, 10.0, 0.0, 1.0)
w_RecoveryTime = st.sidebar.number_input("Recovery Time", 0.0, 10.0, 0.0, 1.0)
w_LikelihoodofInjury = st.sidebar.number_input("Likelihood of Injury", 0.0, 10.0, 0.0, 1.0)
w = [w_PlayerAge, w_PlayerWeight, w_PlayerHeight, w_PreviousInjuries, w_TrainingIntensity, w_RecoveryTime, w_LikelihoodofInjury]

# NORMALISASI KRITERIA
if sum(w) == 0:
    st.error("Total weight is 0. Please input at least one non-zero weight.")
    st.stop()
else:
    w_norm = [c / sum(w) for c in w]

# HITUNG S(i)
# m = Jumlah alternatif, n = jumlah kriteria
m = len(a)
n = len(w)

s = [1] * m

for i in range(m):
    for j in range(n):
        s[i] = s[i] * (x[i][j] ** (k[j] * w_norm[j]))

# HITUNG V
v = [u / sum(s) for u in s]

# HASIL
result_df = pd.DataFrame({
    "Person": a,
    "Score": v
})

result_df = result_df.sort_values(by="Score", ascending=False).reset_index(drop=True)

st.subheader("Ranking of Players by Injury Risk Level")
st.dataframe(result_df)

st.subheader("Chart")
st.area_chart(data=result_df.set_index("Person")["Score"])