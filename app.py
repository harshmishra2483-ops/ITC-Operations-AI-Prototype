
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path

st.set_page_config(
    page_title="Operations Intelligence | FMCG",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- DESIGN ----------
st.markdown("""
<style>
.stApp {
    background-color: #F3F6FA;
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}
[data-testid="stSidebar"] {
    background-color: #14283F;
}
[data-testid="stSidebar"] * {
    color: white !important;
}
.main-title {
    font-size: clamp(24px, 2.5vw, 34px);
    font-weight: 800;
    color: #14283F;
    line-height: 1.25;
    width: 100%;
    white-space: normal;
    overflow-wrap: anywhere;
    display: block;
    padding-bottom: 5px;
}
.section-title {
    color: #14283F;
    font-size: 19px;
    font-weight: 750;
    margin-top: 12px;
}
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E3EAF2;
    padding: 14px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------- SAMPLE DATA ----------
maintenance = pd.DataFrame({
    "Machine": ["M-101", "M-102", "M-103", "M-104", "M-105"],
    "Downtime Hours": [18, 7, 25, 4, 13],
    "Recent Failures": [4, 1, 5, 0, 3],
    "Criticality": [5, 3, 5, 2, 4],
    "Days Since Service": [45, 20, 60, 12, 38]
})

quality = pd.DataFrame({
    "Product": ["Product A", "Product B", "Product C",
                "Product D", "Product E"],
    "Defect Rate (%)": [4.8, 2.1, 6.2, 1.4, 3.7],
    "Repeat Incidents": [5, 2, 7, 1, 4],
    "Severity": [5, 3, 5, 2, 4]
})

inventory = pd.DataFrame({
    "Material": ["Raw Material A", "Packaging B", "Raw Material C",
                 "Packaging D", "Raw Material E"],
    "Available Stock": [1200, 400, 250, 1800, 600],
    "Daily Demand": [100, 80, 100, 120, 50],
    "Lead Time Days": [8, 7, 10, 5, 9]
})

# ---------- RISK CALCULATIONS ----------
maintenance["Risk Score"] = (
    maintenance["Downtime Hours"] / 30 * 35 +
    maintenance["Recent Failures"] / 6 * 30 +
    maintenance["Days Since Service"] / 60 * 15 +
    maintenance["Criticality"] / 5 * 20
).clip(0, 100).round(1)

quality["Risk Score"] = (
    quality["Defect Rate (%)"] / 8 * 35 +
    quality["Repeat Incidents"] / 8 * 25 +
    quality["Severity"] / 5 * 40
).clip(0, 100).round(1)

inventory["Days of Cover"] = (
    inventory["Available Stock"] / inventory["Daily Demand"]
).round(1)

inventory["Risk Score"] = (
    (inventory["Lead Time Days"] /
     inventory["Days of Cover"]).clip(0, 2) * 30 +
    (inventory["Lead Time Days"] /
     inventory["Days of Cover"]).clip(0, 2) * 20 +
    (1 - inventory["Days of Cover"] /
     (inventory["Days of Cover"] + inventory["Lead Time Days"])) * 50
).clip(0, 100).round(1)

def priority(score):
    if score >= 70:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    return "LOW"

maintenance["Priority"] = maintenance["Risk Score"].apply(priority)
quality["Priority"] = quality["Risk Score"].apply(priority)
inventory["Priority"] = inventory["Risk Score"].apply(priority)

# ---------- AI INTELLIGENCE ENGINE ----------

def generate_ai_insight(row, module):

    findings = []
    evidence = []
    recommendation = ""

    if module == "Maintenance":

        if row["Downtime Hours"] >= 15:
            findings.append("Elevated machine downtime detected")
            evidence.append(
                f"Downtime: {row['Downtime Hours']} hours"
            )

        if row["Recent Failures"] >= 3:
            findings.append("Repeated machine failure pattern detected")
            evidence.append(
                f"Recent failures: {row['Recent Failures']}"
            )

        if row["Days Since Service"] >= 30:
            findings.append("Preventive maintenance overdue indicator")
            evidence.append(
                f"Days since service: {row['Days Since Service']}"
            )

        if row["Criticality"] >= 4:
            evidence.append("High operational criticality")

        recommendation = (
            "Prioritise engineering inspection, review failure history "
            "and schedule preventive maintenance if verified."
        )

    elif module == "Quality":

        if row["Defect Rate (%)"] >= 4:
            findings.append("Above-threshold defect rate detected")
            evidence.append(
                f"Defect rate: {row['Defect Rate (%)']}%"
            )

        if row["Repeat Incidents"] >= 3:
            findings.append("Recurring quality incident pattern detected")
            evidence.append(
                f"Repeat incidents: {row['Repeat Incidents']}"
            )

        if row["Severity"] >= 4:
            findings.append("High-severity defect indicator")
            evidence.append(
                f"Severity rating: {row['Severity']}/5"
            )

        recommendation = (
            "Review inspection records, investigate possible root causes "
            "and prepare corrective and preventive action (CAPA)."
        )

    elif module == "Inventory":

        cover = row["Days of Cover"]
        lead = row["Lead Time Days"]

        if cover < lead:
            findings.append(
                "Stock coverage is below supplier lead time"
            )
            evidence.append(
                f"Days of cover: {cover} days; Lead time: {lead} days"
            )

        if cover < lead * 1.2:
            findings.append("Inventory buffer may be insufficient")

        evidence.append(
            f"Available stock: {row['Available Stock']}"
        )
        evidence.append(
            f"Daily demand: {row['Daily Demand']}"
        )

        recommendation = (
            "Verify demand and supplier lead time, then review "
            "replenishment priority with the inventory planner."
        )

    if not findings:
        findings.append(
            "No major risk indicator detected in current rules"
        )
        evidence.append(
            "Current sample indicators are within screening limits"
        )

    return pd.Series({
        "AI Finding": " | ".join(findings),
        "AI Evidence": " | ".join(evidence),
        "AI Recommendation": recommendation
    })


# Generate insights for all three modules

maintenance[
    ["AI Finding", "AI Evidence", "AI Recommendation"]
] = maintenance.apply(
    lambda row: generate_ai_insight(row, "Maintenance"), axis=1
)

quality[
    ["AI Finding", "AI Evidence", "AI Recommendation"]
] = quality.apply(
    lambda row: generate_ai_insight(row, "Quality"), axis=1
)

inventory[
    ["AI Finding", "AI Evidence", "AI Recommendation"]
] = inventory.apply(
    lambda row: generate_ai_insight(row, "Inventory"), axis=1
)


# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("## 🏭 OPERATIONS AI")
    st.caption("FMCG DECISION SUPPORT SYSTEM")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Executive Overview",
            "Predictive Maintenance",
            "Quality Management",
            "Inventory & Supply Chain",
            "Human Approval Centre"
        ]
    )

    st.divider()
    st.caption("PROTOTYPE VERSION 1.0")
    st.caption("Synthetic demonstration data")

# ---------- HEADER ----------
st.markdown(
    '<div class="main-title">Operations Intelligence Control Tower</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="sub-title">MANUFACTURING • QUALITY • INVENTORY • '
    'HUMAN-IN-THE-LOOP DECISION SUPPORT</div>',
    unsafe_allow_html=True
)
st.divider()

# ---------- OVERVIEW ----------
if page == "Executive Overview":

    st.markdown("### Executive Overview")
    st.caption("Illustrative operational indicators from sample datasets")

    high_maintenance = (maintenance["Priority"] == "HIGH").sum()
    high_quality = (quality["Priority"] == "HIGH").sum()
    high_inventory = (inventory["Priority"] == "HIGH").sum()

    k1, k2, k3, k4 = st.columns(4)

    cards = [
        (k1, "MACHINE ALERTS", high_maintenance, "Maintenance"),
        (k2, "QUALITY EXCEPTIONS", high_quality, "Quality"),
        (k3, "INVENTORY ALERTS", high_inventory, "Supply chain"),
        (k4, "TOTAL RECORDS", 15, "Across 3 modules")
    ]

    for col, label, value, note in cards:
        with col:
            st.markdown(f"""
            <div class="kpi">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-note">{note}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Operational Risk Distribution</div>',
                unsafe_allow_html=True)

    risk_data = pd.DataFrame({
        "Module": ["Maintenance", "Quality", "Inventory"],
        "HIGH": [high_maintenance, high_quality, high_inventory],
        "MEDIUM": [
            (maintenance["Priority"] == "MEDIUM").sum(),
            (quality["Priority"] == "MEDIUM").sum(),
            (inventory["Priority"] == "MEDIUM").sum()
        ],
        "LOW": [
            (maintenance["Priority"] == "LOW").sum(),
            (quality["Priority"] == "LOW").sum(),
            (inventory["Priority"] == "LOW").sum()
        ]
    })

    left, right = st.columns([1.5, 1])

    with left:
        chart_data = risk_data.melt(
            id_vars="Module",
            var_name="Priority",
            value_name="Records"
        )
        fig = px.bar(
            chart_data,
            x="Module",
            y="Records",
            color="Priority",
            barmode="stack",
            color_discrete_map={
                "HIGH": "#D9534F",
                "MEDIUM": "#E7A43B",
                "LOW": "#299B78"
            }
        )
        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=10, r=10, t=20, b=10),
            legend_title_text="Risk Level"
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown("#### Priority Attention")
        st.metric("High-risk records", 
                  high_maintenance + high_quality + high_inventory)
        st.info("Review high-risk records first. Recommendations require human approval.")

    # ---------- AI INTELLIGENCE DISPLAY ----------

    st.markdown("### 🧠 AI Intelligence & Operational Insights")

    st.caption(
        "The decision engine analyses operational indicators, "
        "explains detected risks and suggests human-reviewed actions."
    )

    ai_records = pd.concat([
        maintenance.assign(Module="Maintenance").rename(
            columns={"Machine": "Record"}
        ),
        quality.assign(Module="Quality").rename(
            columns={"Product": "Record"}
        ),
        inventory.assign(Module="Inventory").rename(
            columns={"Material": "Record"}
        )
    ], ignore_index=True, sort=False)

    ai_records = ai_records.sort_values(
        "Risk Score", ascending=False
    )

    for _, item in ai_records.head(3).iterrows():

        with st.expander(
            f"{item['Module']} | {item['Record']} | "
            f"Risk: {item['Risk Score']}/100"
        ):

            st.markdown("**1. What did the system detect?**")
            st.write(item["AI Finding"])

            st.markdown("**2. Why did the system detect it?**")
            st.write(item["AI Evidence"])

            st.markdown("**3. What action does it recommend?**")
            st.info(item["AI Recommendation"])

            st.caption(
                "Rule-based decision support. Verify findings "
                "before taking operational action."
            )


    st.markdown('<div class="section-title">Latest Operational Records</div>',
                unsafe_allow_html=True)

    st.dataframe(
        pd.concat([
            maintenance[["Machine", "Risk Score", "Priority"]]
            .rename(columns={"Machine": "Record"}),
            quality[["Product", "Risk Score", "Priority"]]
            .rename(columns={"Product": "Record"}),
            inventory[["Material", "Risk Score", "Priority"]]
            .rename(columns={"Material": "Record"})
        ], ignore_index=True),
        use_container_width=True,
        hide_index=True
    )

# ---------- MAINTENANCE ----------
elif page == "Predictive Maintenance":
    st.markdown("### Predictive Maintenance")
    st.caption("Machine risk screening and maintenance prioritisation")

    st.dataframe(maintenance, use_container_width=True, hide_index=True)

    fig = px.bar(
        maintenance,
        x="Machine",
        y="Risk Score",
        color="Priority",
        color_discrete_map={
            "HIGH": "#D9534F",
            "MEDIUM": "#E7A43B",
            "LOW": "#299B78"
        },
        title="Machine-wise Risk Score"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.warning("Recommendations are screening indicators, not trained failure predictions.")

# ---------- QUALITY ----------
elif page == "Quality Management":
    st.markdown("### Quality Management")
    st.caption("Defect monitoring and recurring incident analysis")

    st.dataframe(quality, use_container_width=True, hide_index=True)

    fig = px.bar(
        quality,
        x="Product",
        y="Defect Rate (%)",
        color="Priority",
        color_discrete_map={
            "HIGH": "#D9534F",
            "MEDIUM": "#E7A43B",
            "LOW": "#299B78"
        },
        title="Product-wise Defect Rate"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.warning("All corrective actions must be reviewed by a quality professional.")

# ---------- INVENTORY ----------
elif page == "Inventory & Supply Chain":
    st.markdown("### Inventory & Supply Chain")
    st.caption("Stock coverage and replenishment risk screening")

    st.dataframe(inventory, use_container_width=True, hide_index=True)

    fig = px.bar(
        inventory,
        x="Material",
        y="Days of Cover",
        color="Priority",
        color_discrete_map={
            "HIGH": "#D9534F",
            "MEDIUM": "#E7A43B",
            "LOW": "#299B78"
        },
        title="Inventory Days of Cover"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.warning("Replenishment recommendations require planner approval.")


# ---------- HUMAN APPROVAL ----------
elif page == "Human Approval Centre":

    st.markdown("### Human Approval Centre")
    st.caption("Review AI-assisted operational recommendations")

    all_records = pd.concat([
        maintenance.assign(Module="Maintenance").rename(
            columns={"Machine": "Record"}
        ),
        quality.assign(Module="Quality").rename(
            columns={"Product": "Record"}
        ),
        inventory.assign(Module="Inventory").rename(
            columns={"Material": "Record"}
        )
    ], ignore_index=True, sort=False)

    record = st.selectbox(
        "Select operational record",
        all_records["Record"].tolist()
    )

    selected = all_records[
        all_records["Record"] == record
    ].iloc[0]

    st.metric(
        "Illustrative Risk Score",
        round(float(selected["Risk Score"]), 1)
    )

    st.write("**Module:**", selected["Module"])
    st.write("**Priority:**", selected["Priority"])

    st.markdown("#### System Analysis")

    st.write(
        "**AI Finding:**",
        selected.get("AI Finding", "Not available")
    )

    st.write(
        "**Supporting Evidence:**",
        selected.get("AI Evidence", "Not available")
    )

    recommendation = selected.get(
        "AI Recommendation",
        "Review the record and verify supporting evidence."
    )

    st.info("Suggested action: " + str(recommendation))

    decision = st.radio(
        "Human decision",
        ["Pending Review", "Approve", "Modify", "Reject"],
        horizontal=True
    )

    comments = st.text_area("Reviewer comments")

    if st.button("Submit Review"):

        if decision == "Pending Review":
            st.warning("Please select Approve, Modify or Reject.")

        else:
            log_dir = Path("outputs/review_logs")
            log_dir.mkdir(parents=True, exist_ok=True)

            log_file = log_dir / "approval_history.csv"

            new_record = pd.DataFrame([{
                "Date & Time": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "Module": selected["Module"],
                "Record ID": selected["Record"],
                "Risk Score": round(
                    float(selected["Risk Score"]), 1
                ),
                "Priority": selected["Priority"],
                "Recommendation": str(recommendation),
                "Decision": decision,
                "Reviewer Comments": comments
            }])

            if log_file.exists():
                old_records = pd.read_csv(log_file)

                updated_records = pd.concat(
                    [old_records, new_record],
                    ignore_index=True
                )
            else:
                updated_records = new_record

            updated_records.to_csv(log_file, index=False)

            st.success(
                "Decision successfully saved to permanent review history."
            )

            st.write("**Record:**", selected["Record"])
            st.write("**Decision:**", decision)

    # Display saved review history
    log_file = Path("outputs/review_logs/approval_history.csv")

    st.divider()
    st.markdown("#### Saved Approval History")

    if log_file.exists():
        history = pd.read_csv(log_file)
        st.dataframe(
            history,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No review decisions recorded yet.")

# ---------- FOOTER ----------
st.divider()
st.caption(
    "Academic prototype | Synthetic data | "
    "No live ITC integration | Human approval required"
)
