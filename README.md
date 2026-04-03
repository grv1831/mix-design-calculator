# 🏗️ Concrete Mix Design Calculator

> A web app for designing concrete mixes as per **IS 10262 : 2019** (Absolute Volume Method), built with Python and Streamlit.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

---

## 📸 Features

- ✅ Full IS 10262 : 2019 mix design (Absolute Volume Method)
- ✅ IS 456 : 2000 exposure condition checks
- ✅ Step-by-step solution with formulas
- ✅ Trial mix batch calculator
- ✅ Pie & bar charts for composition
- ✅ Admixture water reduction (Plasticizer / Superplasticizer)
- ✅ Built-in reference tables (IS 10262 & IS 456)
- ✅ Grades M20 to M40
- ✅ Aggregate sizes 10, 20, 40 mm
- ✅ FA zones I to IV

---

## 🧮 Design Parameters

| Parameter          | Options                                      |
|--------------------|----------------------------------------------|
| Grade of concrete  | M20, M25, M30, M35, M40                      |
| Exposure condition | Mild, Moderate, Severe, Very Severe          |
| Cement type        | OPC 43, OPC 53, PPC, PSC, SRC               |
| Aggregate size     | 10 mm, 20 mm, 40 mm                          |
| FA zone            | Zone I, II, III, IV                          |
| Slump              | 25 mm, 75 mm, 125 mm                         |
| Admixture          | None, Plasticizer, Superplasticizer          |

---

## 🚀 How to Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/grv1831/mix-design-calculator.git
cd mix-design-calculator
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## ☁️ Deploy on Streamlit Cloud (Free)

1. Push this repo to your GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click **New app** → select this repo → set `app.py` as main file
5. Click **Deploy** — your app goes live in ~2 minutes! 🎉

---

## 📁 Project Structure

```
mix-design-calculator/
│
├── app.py              # Main Streamlit UI
├── calculations.py     # IS 10262 calculation engine
├── reference_data.py   # IS standard reference tables
├── requirements.txt    # Python dependencies
├── .streamlit/
│   └── config.toml     # App theme & server config
└── README.md
```

---

## 📐 IS Standards Referenced

| Standard          | Description                                      |
|-------------------|--------------------------------------------------|
| IS 10262 : 2019   | Guidelines for concrete mix design              |
| IS 456 : 2000     | Plain and reinforced concrete — Code of practice|
| IS 383 : 2016     | Coarse and fine aggregate specification         |

---

## 🔢 Method Overview

1. **Target strength** → f'ck = fck + 1.65 × s
2. **w/c ratio** → from IS 456 Table 5 (exposure based)
3. **Water content** → from IS 10262 Table 2 (agg. size + slump)
4. **Cement content** → Water / w/c (checked against minimum)
5. **CA content** → Volume fraction from IS 10262 Table 3
6. **FA content** → Absolute volume method (remaining volume)
7. **Mix ratio** → C : FA : CA expressed relative to cement

---

## 👨‍💻 Author

**Gaurav** — B.Tech Civil Engineering student  
GitHub: [@grv1831](https://github.com/grv1831)

---

## 📄 License

MIT License — free to use, modify, and share.
