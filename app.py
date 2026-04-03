import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from calculations import MixDesign
from reference_data import (
    EXPOSURE_TABLE, WATER_CONTENT_TABLE,
    CA_VOLUME_TABLE, SD_TABLE, CEMENT_TYPES
)

st.set_page_config(
    page_title="Concrete Mix Design Calculator",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main-header {
        background: linear-gradient(135deg, #1a3a5c 0%, #2563a8 100%);
        padding: 2rem 2.5rem;
        border-radius: 14px;
        margin-bottom: 2rem;
        color: white;
    }
    .main-header h1 { color: white; font-size: 2rem; font-weight: 700; margin: 0; }
    .main-header p  { color: #b8d4f0; margin: 0.5rem 0 0; font-size: 1rem; }

    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.07);
    }
    .metric-card .label { font-size: 0.75rem; color: #64748b; font-weight: 600;
                          text-transform: uppercase; letter-spacing: 0.05em; }
    .metric-card .value { font-size: 2rem; font-weight: 700; color: #1e3a5f; }
    .metric-card .unit  { font-size: 0.8rem; color: #94a3b8; margin-top: 2px; }

    .step-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #2563a8;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
    }
    .step-number { background: #2563a8; color: white; border-radius: 50%;
                   width: 28px; height: 28px; display: inline-flex;
                   align-items: center; justify-content: center;
                   font-size: 0.8rem; font-weight: 700; margin-right: 8px; }
    .step-title  { font-weight: 600; color: #1e3a5f; font-size: 1rem; }
    .step-formula { background: #f1f5f9; border-radius: 6px; padding: 0.5rem 0.75rem;
                    font-family: monospace; font-size: 0.85rem; margin-top: 0.5rem;
                    color: #334155; }

    .result-highlight {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        margin-bottom: 1rem;
    }
    .result-highlight .ratio { font-size: 1.5rem; font-weight: 700; color: #1d4ed8; }

    .warning-box {
        background: #fffbeb; border: 1px solid #fcd34d;
        border-radius: 8px; padding: 0.75rem 1rem;
        color: #92400e; font-size: 0.9rem; margin-top: 0.5rem;
    }
    .info-box {
        background: #eff6ff; border: 1px solid #bfdbfe;
        border-radius: 8px; padding: 0.75rem 1rem;
        color: #1e40af; font-size: 0.9rem;
    }

    div[data-testid="stSidebar"] { background: #f8fafc; }
    .stButton > button {
        width: 100%;
        background: #2563a8;
        color: white;
        font-weight: 600;
        font-size: 1rem;
        padding: 0.65rem;
        border-radius: 8px;
        border: none;
        margin-top: 1rem;
    }
    .stButton > button:hover { background: #1d4ed8; }
</style>
""", unsafe_allow_html=True)


# ── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🏗️ Concrete Mix Design Calculator</h1>
    <p>IS 10262 : 2019 &nbsp;|&nbsp; Absolute Volume Method &nbsp;|&nbsp; Developed by Gaurav</p>
</div>
""", unsafe_allow_html=True)


# ── Sidebar Inputs ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Design Inputs")
    st.markdown("---")

    st.markdown("**Design Requirements**")
    grade = st.selectbox("Grade of Concrete", [20, 25, 30, 35, 40],
                         index=1, format_func=lambda x: f"M{x}")
    exposure = st.selectbox("Exposure Condition",
                            ["Mild", "Moderate", "Severe", "Very Severe"],
                            index=1)
    structure = st.selectbox("Type of Structure", ["RCC", "PCC"])

    st.markdown("---")
    st.markdown("**Cement Properties**")
    cement_type = st.selectbox("Cement Type",
                               list(CEMENT_TYPES.keys()), index=1)
    sg_cement = st.number_input("Sp. Gravity of Cement", 3.00, 3.20, 3.15, 0.01)

    st.markdown("---")
    st.markdown("**Aggregate Properties**")
    agg_size = st.selectbox("Max. Aggregate Size (mm)", [10, 20, 40], index=1)
    fa_zone  = st.selectbox("Zone of Fine Aggregate",
                            ["Zone I", "Zone II", "Zone III", "Zone IV"], index=1)
    sg_fa = st.number_input("Sp. Gravity of Fine Aggregate", 2.50, 2.90, 2.65, 0.01)
    sg_ca = st.number_input("Sp. Gravity of Coarse Aggregate", 2.50, 2.90, 2.70, 0.01)

    st.markdown("---")
    st.markdown("**Mix Parameters**")
    slump = st.selectbox("Workability (Slump)", [25, 75, 125],
                         index=2, format_func=lambda x: f"{x} mm")
    admixture = st.selectbox("Admixture",
                             ["None", "Plasticizer", "Superplasticizer"], index=2)
    air_content = st.number_input("Entrapped Air (%)", 0.5, 3.0, 1.0, 0.5)
    n_samples   = st.number_input("No. of Test Samples", 15, 60, 30, 1)

    st.markdown("---")
    calculate = st.button("🔢 Calculate Mix Design")


# ── Tabs ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 Results", "📋 Step-by-Step", "📐 Trial Mix", "💰 Cost Estimator", "📚 Reference Tables"]
)

if calculate or "result" in st.session_state:
    md = MixDesign(
        grade=grade,
        exposure=exposure.lower().replace(" ", "_"),
        agg_size=agg_size,
        fa_zone={"Zone I":1,"Zone II":2,"Zone III":3,"Zone IV":4}[fa_zone],
        slump=slump,
        admixture=admixture.lower(),
        sg_cement=sg_cement,
        sg_fa=sg_fa,
        sg_ca=sg_ca,
        air_pct=air_content,
        n_samples=int(n_samples),
    )
    res = md.calculate()
    st.session_state["result"] = res
    st.session_state["md"] = md
else:
    res = st.session_state.get("result", None)
    md  = st.session_state.get("md", None)

# ── Tab 1 : Results ─────────────────────────────────────────────────────────
with tab1:
    if res is None:
        st.info("👈 Fill inputs in the sidebar and click **Calculate Mix Design**.")
    else:
        # Mix ratio highlight
        st.markdown(f"""
        <div class="result-highlight">
            <div style="font-size:0.8rem;color:#1d4ed8;font-weight:600;text-transform:uppercase;
                        letter-spacing:0.05em;">Final Mix Ratio (C : FA : CA)</div>
            <div class="ratio">1 : {res['ratio_fa']} : {res['ratio_ca']}</div>
            <div style="color:#475569;font-size:0.9rem;margin-top:0.25rem;">
                w/c = {res['wc']:.2f} &nbsp;|&nbsp;
                Target f'ck = {res['fck_target']:.1f} MPa &nbsp;|&nbsp;
                Grade M{grade}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Metric cards
        cols = st.columns(4)
        metrics = [
            ("Cement",         res['cement'],  "kg/m³"),
            ("Water",          res['water'],   "liters/m³"),
            ("Fine Aggregate", res['fa'],      "kg/m³"),
            ("Coarse Agg.",    res['ca'],      "kg/m³"),
        ]
        for col, (label, value, unit) in zip(cols, metrics):
            col.markdown(f"""
            <div class="metric-card">
                <div class="label">{label}</div>
                <div class="value">{value}</div>
                <div class="unit">{unit}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("### 📋 Quantity Summary")
            df = pd.DataFrame({
                "Material":  ["Cement", "Water", "Fine Aggregate", "Coarse Aggregate"],
                "Quantity":  [res['cement'], res['water'], res['fa'], res['ca']],
                "Unit":      ["kg/m³", "liters/m³", "kg/m³", "kg/m³"],
                "% by mass": [
                    round(res['cement'] / res['total'] * 100, 1),
                    round(res['water']  / res['total'] * 100, 1),
                    round(res['fa']     / res['total'] * 100, 1),
                    round(res['ca']     / res['total'] * 100, 1),
                ]
            })
            st.dataframe(df, use_container_width=True, hide_index=True)

        with col_b:
            st.markdown("### 🥧 Composition by Volume")
            fig = px.pie(
                names=["Cement", "Water", "Fine Aggregate", "Coarse Aggregate", "Air"],
                values=[
                    res['vol_cement'], res['vol_water'],
                    res['vol_fa'],     res['vol_ca'],
                    res['vol_air']
                ],
                color_discrete_sequence=["#1e3a5f","#3b82f6","#f59e0b","#6b7280","#e2e8f0"],
                hole=0.4
            )
            fig.update_traces(textposition='outside', textinfo='percent+label')
            fig.update_layout(margin=dict(t=20, b=20, l=20, r=20),
                              showlegend=False, height=300)
            st.plotly_chart(fig, use_container_width=True)

        # Bar chart
        st.markdown("### 📊 Material Quantities (kg/m³)")
        fig2 = go.Figure(go.Bar(
            x=["Cement", "Water", "Fine Aggregate", "Coarse Aggregate"],
            y=[res['cement'], res['water'], res['fa'], res['ca']],
            marker_color=["#1e3a5f", "#3b82f6", "#f59e0b", "#6b7280"],
            text=[f"{v} kg" for v in [res['cement'], res['water'], res['fa'], res['ca']]],
            textposition="outside"
        ))
        fig2.update_layout(
            yaxis_title="kg/m³", plot_bgcolor="white",
            yaxis=dict(gridcolor="#f1f5f9"),
            margin=dict(t=30, b=10), height=320
        )
        st.plotly_chart(fig2, use_container_width=True)

        if res.get("cement_adjusted"):
            st.markdown(f"""
            <div class="warning-box">
                ⚠️ Cement content was raised from {res['cement_raw']} kg/m³ to
                {res['cement']} kg/m³ to meet the minimum requirement for
                <b>{exposure}</b> exposure condition (IS 456 Table 5).
            </div>
            """, unsafe_allow_html=True)


# ── Tab 2 : Step-by-Step ────────────────────────────────────────────────────
with tab2:
    if res is None:
        st.info("👈 Calculate first to see the step-by-step solution.")
    else:
        st.markdown("### IS 10262 : 2019 — Step-by-Step Design Procedure")

        steps = md.get_steps(res)
        for i, step in enumerate(steps, 1):
            st.markdown(f"""
            <div class="step-card">
                <span class="step-number">{i}</span>
                <span class="step-title">{step['title']}</span>
                <p style="margin:0.4rem 0 0;color:#475569;font-size:0.9rem;">{step['description']}</p>
                <div class="step-formula">{step['formula']}</div>
                <p style="margin:0.4rem 0 0;color:#1d4ed8;font-weight:600;font-size:0.9rem;">
                    ✔ {step['result']}
                </p>
            </div>
            """, unsafe_allow_html=True)


# ── Tab 3 : Trial Mix ───────────────────────────────────────────────────────
with tab3:
    if res is None:
        st.info("👈 Calculate first to see trial mix quantities.")
    else:
        st.markdown("### 🧪 Trial Mix Calculator")
        st.markdown("Calculate actual quantities for a trial batch.")

        vol = st.number_input("Trial batch volume (liters)", 5.0, 100.0, 30.0, 5.0)
        factor = vol / 1000.0

        trial = {
            "Cement":          round(res['cement'] * factor, 3),
            "Water":           round(res['water']  * factor, 3),
            "Fine Aggregate":  round(res['fa']     * factor, 3),
            "Coarse Aggregate":round(res['ca']     * factor, 3),
        }

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"#### Quantities for {vol:.0f} L batch")
            for mat, qty in trial.items():
                st.metric(mat, f"{qty} kg")
        with col2:
            st.markdown("#### Batching checklist")
            checklist = [
                "Weigh all dry materials separately",
                "Mix CA + FA + Cement dry for 1 min",
                "Add 75% water and mix for 2 min",
                "Add remaining water gradually",
                "Mix for 3–5 minutes total",
                "Check slump immediately",
                "Cast cubes for 3, 7, 28-day testing",
            ]
            for item in checklist:
                st.checkbox(item, key=item)

        st.markdown("---")
        st.markdown("#### 📝 Trial mix corrections (IS 10262 Cl. 9)")
        adjust_water = st.slider("Water adjustment (±%)", -15, 15, 0)
        if adjust_water != 0:
            new_water  = round(res['water'] * (1 + adjust_water/100), 1)
            new_cement = round(new_water / res['wc'], 1)
            st.info(f"Adjusted water: **{new_water} L/m³** → Cement: **{new_cement} kg/m³** (w/c maintained)")


# ── Tab 4 : Cost Estimator ──────────────────────────────────────────────────
with tab4:
    if res is None:
        st.info("👈 Calculate mix design first, then estimate cost here.")
    else:
        st.markdown("### 💰 Cost Estimator")
        st.markdown("Enter current local market rates to calculate cost per m³ of concrete.")

        st.markdown("---")
        st.markdown("#### 📦 Market Rates (enter your local prices)")

        col1, col2 = st.columns(2)
        with col1:
            rate_cement = st.number_input(
                "Cement rate (₹ per 50 kg bag)", 300, 800, 420, 10,
                help="1 bag = 50 kg. Average market rate is ₹380–₹450 per bag."
            )
            rate_fa = st.number_input(
                "Fine aggregate / Sand rate (₹ per tonne)", 500, 5000, 1200, 50,
                help="River sand or M-sand rate per metric tonne."
            )
        with col2:
            rate_ca = st.number_input(
                "Coarse aggregate rate (₹ per tonne)", 500, 5000, 1000, 50,
                help="20mm crushed stone aggregate rate per metric tonne."
            )
            rate_labour = st.number_input(
                "Labour + mixing charges (₹ per m³)", 500, 5000, 1500, 100,
                help="Includes mixing, placing, compacting, and curing labour."
            )
            rate_admix = st.number_input(
                "Admixture cost (₹ per m³)", 0, 2000, 150, 50,
                help="Cost of plasticizer or superplasticizer per m³."
            )

        st.markdown("---")

        # ── Calculations ──
        cement_bags       = res['cement'] / 50
        cost_cement       = round(cement_bags * rate_cement, 2)
        cost_fa           = round((res['fa'] / 1000) * rate_fa, 2)
        cost_ca           = round((res['ca'] / 1000) * rate_ca, 2)
        cost_labour       = rate_labour
        cost_admix        = rate_admix
        cost_misc         = round((cost_cement + cost_fa + cost_ca) * 0.03, 2)  # 3% misc
        total_cost        = round(cost_cement + cost_fa + cost_ca + cost_labour + cost_admix + cost_misc, 2)

        # ── Summary cards ──
        st.markdown("#### 📊 Cost Breakdown per m³")
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"""<div class="metric-card">
            <div class="label">Cement</div>
            <div class="value" style="font-size:1.4rem;">₹{cost_cement:,.0f}</div>
            <div class="unit">{cement_bags:.1f} bags × ₹{rate_cement}</div>
        </div>""", unsafe_allow_html=True)
        c2.markdown(f"""<div class="metric-card">
            <div class="label">Fine Aggregate</div>
            <div class="value" style="font-size:1.4rem;">₹{cost_fa:,.0f}</div>
            <div class="unit">{res['fa']/1000:.3f} T × ₹{rate_fa}</div>
        </div>""", unsafe_allow_html=True)
        c3.markdown(f"""<div class="metric-card">
            <div class="label">Coarse Aggregate</div>
            <div class="value" style="font-size:1.4rem;">₹{cost_ca:,.0f}</div>
            <div class="unit">{res['ca']/1000:.3f} T × ₹{rate_ca}</div>
        </div>""", unsafe_allow_html=True)
        c4.markdown(f"""<div class="metric-card">
            <div class="label">Total Cost / m³</div>
            <div class="value" style="font-size:1.4rem; color:#16a34a;">₹{total_cost:,.0f}</div>
            <div class="unit">all inclusive</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("#### 🧾 Detailed Cost Sheet")
            cost_df = pd.DataFrame({
                "Item": [
                    "Cement",
                    "Fine Aggregate (Sand)",
                    "Coarse Aggregate",
                    "Labour & Mixing",
                    "Admixture",
                    "Misc. (transport, water, etc.)",
                    "TOTAL"
                ],
                "Quantity": [
                    f"{cement_bags:.1f} bags",
                    f"{res['fa']/1000:.3f} tonnes",
                    f"{res['ca']/1000:.3f} tonnes",
                    "per m³",
                    "per m³",
                    "3% of material",
                    ""
                ],
                "Cost (₹)": [
                    f"₹{cost_cement:,.0f}",
                    f"₹{cost_fa:,.0f}",
                    f"₹{cost_ca:,.0f}",
                    f"₹{cost_labour:,.0f}",
                    f"₹{cost_admix:,.0f}",
                    f"₹{cost_misc:,.0f}",
                    f"₹{total_cost:,.0f}"
                ]
            })
            st.dataframe(cost_df, use_container_width=True, hide_index=True)

        with col_right:
            st.markdown("#### 🥧 Cost Distribution")
            fig_cost = px.pie(
                names=["Cement", "Fine Agg.", "Coarse Agg.", "Labour", "Admixture", "Misc."],
                values=[cost_cement, cost_fa, cost_ca, cost_labour, cost_admix, cost_misc],
                color_discrete_sequence=["#1e3a5f","#f59e0b","#6b7280","#3b82f6","#10b981","#e2e8f0"],
                hole=0.4
            )
            fig_cost.update_traces(textposition='outside', textinfo='percent+label')
            fig_cost.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                showlegend=False, height=320
            )
            st.plotly_chart(fig_cost, use_container_width=True)

        st.markdown("---")
        st.markdown("#### 🏗️ Project Volume Calculator")
        st.markdown("Calculate total cost for your actual project volume.")

        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            proj_vol = st.number_input("Total concrete volume (m³)", 1.0, 10000.0, 10.0, 1.0)
        with col_p2:
            wastage  = st.slider("Add wastage (%)", 0, 15, 5)
        with col_p3:
            st.markdown("<br>", unsafe_allow_html=True)
            eff_vol  = round(proj_vol * (1 + wastage/100), 2)
            proj_total = round(total_cost * eff_vol, 0)
            st.metric("Effective Volume", f"{eff_vol} m³")

        st.markdown(f"""
        <div class="result-highlight" style="margin-top:1rem;">
            <div style="font-size:0.8rem;color:#1d4ed8;font-weight:600;text-transform:uppercase;
                        letter-spacing:0.05em;">Estimated Project Cost</div>
            <div class="ratio">₹ {proj_total:,.0f}</div>
            <div style="color:#475569;font-size:0.9rem;margin-top:0.25rem;">
                {eff_vol} m³ × ₹{total_cost:,.0f}/m³ &nbsp;|&nbsp;
                Grade M{grade} concrete &nbsp;|&nbsp;
                {wastage}% wastage included
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="warning-box">
            ⚠️ This is an indicative estimate only. Actual costs vary by location, season,
            and supplier. Always get quotations from local vendors before finalizing.
        </div>
        """, unsafe_allow_html=True)


# ── Tab 5 : Reference Tables ─────────────────────────────────────────────────
with tab5:
    st.markdown("### 📚 IS 10262 : 2019 — Reference Tables")

    st.markdown("#### Table 1 — Standard deviation & target strength")
    st.dataframe(pd.DataFrame({
        "Grade":    ["M20","M25","M30","M35","M40"],
        "fck (MPa)":[20,25,30,35,40],
        "Std. dev s":[4,4,5,5,5],
        "Target f'ck (MPa)":["26.6","31.6","38.25","43.25","48.25"],
    }), use_container_width=True, hide_index=True)

    st.markdown("#### Table 2 — Free water content (liters/m³)")
    st.dataframe(pd.DataFrame({
        "Agg. size (mm)":[10,20,40],
        "Slump 25 mm":   [180,160,140],
        "Slump 50–100 mm":[200,180,160],
        "Slump 100–150 mm":[220,200,180],
    }), use_container_width=True, hide_index=True)

    st.markdown("#### Table 3 — Volume of CA per m³ of concrete")
    st.dataframe(pd.DataFrame({
        "Agg. size (mm)":[10,20,40],
        "Zone I FA": [0.50,0.66,0.75],
        "Zone II FA":[0.48,0.64,0.73],
        "Zone III FA":[0.46,0.62,0.71],
        "Zone IV FA": [0.44,0.60,0.69],
    }), use_container_width=True, hide_index=True)

    st.markdown("#### IS 456 Table 5 — Exposure condition requirements")
    st.dataframe(pd.DataFrame({
        "Exposure":    ["Mild","Moderate","Severe","Very Severe"],
        "Max w/c":     [0.55, 0.50, 0.45, 0.40],
        "Min cement (kg/m³)":[300, 300, 320, 340],
        "Min grade":   ["M20","M25","M30","M35"],
    }), use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#94a3b8;font-size:0.8rem;'>"
    "Concrete Mix Design Calculator · IS 10262 : 2019 · Built with Python & Streamlit"
    "</div>", unsafe_allow_html=True
)