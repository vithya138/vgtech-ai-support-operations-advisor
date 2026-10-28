
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="VG Tech AI Support Operations Advisor",
    page_icon="📊",
    layout="wide"
)

st.title("VG Tech | AI Support Operations Advisor")
st.caption("Enterprise Support Operations Intelligence")

st.info("Prototype using synthetic support ticket data.")

# Load the dataset
data_path = Path(__file__).parent / "synthetic_tickets.csv"
tickets = pd.read_csv(data_path)

# Country and priority filters
st.sidebar.header("Dashboard Filters")

selected_countries = st.sidebar.multiselect(
    "Country",
    options=sorted(tickets["country"].dropna().unique()),
    default=sorted(tickets["country"].dropna().unique())
)

selected_priorities = st.sidebar.multiselect(
    "Priority",
    options=sorted(tickets["priority"].dropna().unique()),
    default=sorted(tickets["priority"].dropna().unique())
)

filtered_tickets = tickets[
    tickets["country"].isin(selected_countries)
    & tickets["priority"].isin(selected_priorities)
].copy()

# Calculate KPIs
total_tickets = len(filtered_tickets)

issue_counts = filtered_tickets["issue_signature"].value_counts()
recurrence_threshold = st.sidebar.slider(
    "Minimum occurrences for recurring issues",
    min_value=3,
    max_value=20,
    value=3,
    step=1
)

recurring_groups = int(
    (issue_counts >= recurrence_threshold).sum()
)

def count_yes_values(series):
    return int(
        series.astype(str)
        .str.strip()
        .str.lower()
        .isin(["true", "1", "yes"])
        .sum()
    )

sla_breaches = count_yes_values(filtered_tickets["sla_breached"])
escalations = count_yes_values(filtered_tickets["escalated"])

# Display KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Tickets", total_tickets)

with col2:
    st.metric("Recurring Issue Groups", recurring_groups)

with col3:
    st.metric("SLA Breaches", sla_breaches)

with col4:
    st.metric("Escalations", escalations)

st.divider()


# Step 37 - Operational Performance Scorecard
st.subheader("Operational Performance Scorecard")

scorecard_total = len(filtered_tickets)

if scorecard_total > 0:
    breach_rate = (
        count_yes_values(filtered_tickets["sla_breached"])
        / scorecard_total * 100
    )
    escalation_rate = (
        count_yes_values(filtered_tickets["escalated"])
        / scorecard_total * 100
    )

    completed_tickets = filtered_tickets[
        filtered_tickets["status"].isin(["Resolved", "Closed"])
    ]

    median_hours = pd.to_numeric(
        completed_tickets["resolution_hours"],
        errors="coerce"
    ).median()

    score_col1, score_col2, score_col3 = st.columns(3)

    with score_col1:
        st.metric("SLA Breach Rate", f"{breach_rate:.1f}%")

    with score_col2:
        st.metric("Escalation Rate", f"{escalation_rate:.1f}%")

    with score_col3:
        resolution_display = (
            f"{median_hours:.2f} hrs"
            if pd.notna(median_hours)
            else "N/A"
        )
        st.metric("Median Resolution", resolution_display)

    st.caption(
        f"Based on {scorecard_total} synthetic tickets; "
        f"{len(completed_tickets)} completed. "
        "Resolution time excludes open tickets."
    )
else:
    st.info("No tickets match the selected filters.")

st.divider()

st.header("Support Operations Overview")

st.write(
    "Identify recurring incidents, understand operational "
    "risks, and prioritise service improvements."
)

st.subheader("Recurring Issue Patterns")

recurring_issues = issue_counts[
    issue_counts >= recurrence_threshold
]

if recurring_issues.empty:
    st.warning(
        "No issue groups meet the selected recurrence threshold. "
        "Try lowering the threshold or expanding the filters. "
        "This does not mean there are no repeated incidents."
    )
else:
    st.bar_chart(
        recurring_issues.rename("Ticket Count")
    )

st.caption(
    f"Showing issue signatures with at least "
    f"{recurrence_threshold} tickets."
)


st.divider()

st.header("Ticket-Level Evidence")

st.write(
    "Review the individual synthetic tickets supporting "
    "the selected dashboard metrics."
)

evidence_columns = [
    "ticket_id",
    "created_date",
    "country",
    "issue_signature",
    "priority",
    "status",
    "sla_breached",
    "escalated"
]

st.dataframe(
    filtered_tickets[evidence_columns],
    use_container_width=True,
    hide_index=True
)

st.caption(
    f"Showing {len(filtered_tickets)} tickets "
    "based on the selected country and priority filters."
)


# INCIDENT RESPONSE VIEW
st.divider()
st.header("Incident Response")

st.write(
    "Review active P1/P2 incidents and identify "
    "cases requiring urgent attention."
)

active_statuses = ["Open", "In Progress", "Pending"]

active_incidents = filtered_tickets[
    filtered_tickets["status"].isin(active_statuses)
    & filtered_tickets["priority"].isin(["P1", "P2"])
].copy()

priority_rank = {"P1": 1, "P2": 2}

active_incidents["priority_rank"] = (
    active_incidents["priority"].map(priority_rank)
)

active_incidents = active_incidents.sort_values(
    ["priority_rank", "created_date"]
)

st.metric("Active P1/P2 Incidents", len(active_incidents))

if active_incidents.empty:
    st.info(
        "No active P1/P2 incidents match the current filters."
    )
else:
    st.dataframe(
        active_incidents[
            [
                "ticket_id",
                "country",
                "issue_signature",
                "priority",
                "status",
                "escalated"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

st.caption(
    "Active incidents are based on recorded ticket statuses "
    "in the synthetic dataset, not live operational data."
)


st.subheader("Business Impact Assessment")

st.caption(
    "Enter hypothetical business-impact details to test "
    "the recommendation logic. These values are not "
    "present in the source dataset."
)

if active_incidents.empty:
    st.info("Select an active incident to assess its impact.")

else:
    selected_ticket_id = st.selectbox(
        "Select an active incident",
        active_incidents["ticket_id"].tolist()
    )

    selected_incident = active_incidents.loc[
        active_incidents["ticket_id"] == selected_ticket_id
    ].iloc[0]

    affected_customers = st.number_input(
        "Number of affected customers",
        min_value=0,
        value=0,
        step=1
    )

    transactions_blocked = st.checkbox(
        "Business transactions are blocked"
    )

    st.write(
        f"Recorded priority: {selected_incident['priority']}"
    )

    # Fictional approved service criticality
    service_criticality = {
        "Payroll batch timeout": "Critical",
        "Payroll rounding mismatch": "High",
        "SSO token expired": "High",
        "API authentication error": "High",
        "SFTP truncated file": "High",
        "MFA reset failure": "High",
        "Reporting export failed": "Standard",
        "Webhook delivery delayed": "Standard",
        "Dashboard permission denied": "Standard"
    }

    issue_name = selected_incident["issue_signature"]

    approved_criticality = service_criticality.get(
        issue_name, "Unclassified"
    )

    st.write(
        f"Approved service criticality (simulated): "
        f"{approved_criticality}"
    )

    if (
        selected_incident["priority"] == "P2"
        and affected_customers >= 50
        and transactions_blocked
    ):
        st.warning(
            "Urgent P1 reassessment recommended. "
            "Business transactions are blocked and "
            "50 or more customers are affected. "
            "Human approval is required."
        )

    elif (
        selected_incident["priority"] == "P1"
    ):
        st.error(
            "P1 incident: Maintain immediate response "
            "and validate business impact and restoration."
        )

    else:
        st.info(
            "No automatic severity escalation rule triggered. "
            "Validate the business impact and existing priority."
        )

    st.caption(
        "Assessment is a prototype recommendation only. "
        "No ticket priority is changed or saved."
    )


# CRITICALITY GOVERNANCE
st.divider()
st.header("Criticality Governance")

st.write(
    "Demonstrate how approved temporary business-criticality "
    "overrides affect service classification."
)

from datetime import datetime
from zoneinfo import ZoneInfo

sg_timezone = ZoneInfo("Asia/Singapore")

override_start = datetime(
    2026, 10, 20, 8, 0, tzinfo=sg_timezone
)

override_end = datetime(
    2026, 10, 20, 18, 0, tzinfo=sg_timezone
)

simulation_date = st.date_input(
    "Simulation date",
    value=datetime(2026, 10, 20).date()
)

simulation_hour = st.slider(
    "Simulation hour (Singapore time)",
    min_value=0,
    max_value=23,
    value=10
)

simulation_time = datetime(
    simulation_date.year,
    simulation_date.month,
    simulation_date.day,
    simulation_hour,
    0,
    tzinfo=sg_timezone
)

normal_criticality = "High"




# EMERGENCY OVERRIDE SIMULATION
st.subheader("Emergency Override Simulation")

st.caption(
    "Fictional emergency approval scenario. "
    "This demonstration does not activate a real override."
)

emergency_requested = st.checkbox(
    "Simulate an emergency criticality override",
    value=False
)

if emergency_requested:
    st.warning(
        "Emergency scenario: Support Manager requests "
        "temporary Critical classification because the "
        "Business Service Owner is unavailable."
    )

    st.write("**Requested by:** Support Manager (simulated)")
    st.write("**Approval path:** Emergency exception")
    st.write("**Maximum duration:** 2 hours")
    st.write("**Retrospective approval:** Required")
    st.write(
        "**Business justification:** Potential payroll "
        "processing disruption requiring urgent review."
    )

    st.info(
        "Simulation only: a valid emergency exception can "
        "temporarily change effective business criticality "
        "and problem investigation ranking. "
        "No production tickets or real approval records are changed."
    )

    st.write("**Emergency override expiry test**")

    elapsed_minutes = st.slider(
        "Minutes since emergency activation",
        min_value=0,
        max_value=180,
        value=60,
        step=15,
        key="emergency_elapsed_minutes"
    )

    emergency_expired = elapsed_minutes >= 120

    review_status = st.selectbox(
        "Retrospective approval status",
        ["Pending review", "Approved", "Rejected"],
        key="emergency_review_status"
    )

    if review_status == "Rejected":
        st.error(
            "Effective emergency status: REJECTED. "
            "The temporary exception is ended."
        )

    elif emergency_expired:
        if review_status == "Approved":
            st.info(
                "Effective emergency status: EXPIRED. "
                "Retrospective approval recorded, but the "
                "two-hour emergency window has ended."
            )
        else:
            st.error(
                "Effective emergency status: EXPIRED — "
                "REVIEW OVERDUE. Normal criticality applies."
            )

    elif review_status == "Approved":
        st.success(
            "Effective emergency status: ACTIVE — APPROVED. "
            f"{120 - elapsed_minutes} minutes remain."
        )

    else:
        st.warning(
            "Effective emergency status: ACTIVE — "
            "PENDING REVIEW. "
            f"{120 - elapsed_minutes} minutes remain."
        )

st.divider()


# SIMULATED GOVERNANCE AND APPROVAL DETAILS
st.subheader("Governance & Approval Details")

st.caption(
    "Demonstration only: fictional approval records. "
    "No real approval workflow or audit database is connected."
)

st.write("**Affected service:** Payroll")
st.write("**Issue:** Payroll rounding mismatch")
st.write("**Recommended by:** Support Manager (simulated)")
st.write("**Approved by:** Payroll Service Owner (simulated)")
st.write(
    "**Business justification:** Increased payroll accuracy "
    "risk during the scheduled payroll processing window."
)

st.write(
    "**Override window:** "
    f"{override_start:%d %b %Y, %I:%M %p} – "
    f"{override_end:%I:%M %p} (Singapore time)"
)

if override_start <= simulation_time < override_end:
    st.success("Governance status: Approved override active")
elif simulation_time < override_start:
    st.info("Governance status: Approved override not yet active")
else:
    st.info("Governance status: Override expired")

st.divider()

scheduled_active = (
    override_start <= simulation_time < override_end
)

emergency_active = (
    emergency_requested
    and elapsed_minutes < 120
    and review_status != "Rejected"
)

if scheduled_active:
    effective_criticality = "Critical"
    override_status = "Scheduled approved override active"

elif emergency_active:
    effective_criticality = "Critical"
    override_status = "Emergency exception active (simulated)"

else:
    effective_criticality = normal_criticality
    override_status = "Normal approved classification"

col_a, col_b = st.columns(2)

with col_a:
    st.metric("Normal Criticality", normal_criticality)

with col_b:
    st.metric("Effective Criticality", effective_criticality)

st.write("Service: Payroll rounding mismatch")
st.write("Override status:", override_status)

st.caption(
    "Governance simulation only. Scheduled overrides use "
    "fictional Payroll Service Owner approval; emergency "
    "exceptions may be pending retrospective approval. "
    "No real approvals or ticket priorities are modified."
)


# PROBLEM INVESTIGATION QUEUE
st.divider()
st.header("Problem Investigation Queue")

st.write(
    "Identify recurring issues for root-cause investigation "
    "using ticket frequency, SLA breaches, escalations "
    "and simulated business criticality."
)

# Use the currently selected country and priority filters
problem_tickets = filtered_tickets.copy()

# Normalise boolean indicators
for column in ["sla_breached", "escalated"]:
    problem_tickets[column] = (
        problem_tickets[column]
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(["true", "1", "yes"])
    )

problem_summary = (
    problem_tickets.groupby("issue_signature")
    .agg(
        ticket_count=("ticket_id", "count"),
        sla_breaches=("sla_breached", "sum"),
        escalations=("escalated", "sum")
    )
    .reset_index()
)

service_criticality_map = {
    "Payroll batch timeout": "Critical",
    "Payroll rounding mismatch": "High",
    "SSO token expired": "High",
    "API authentication error": "High",
    "SFTP truncated file": "High",
    "MFA reset failure": "High",
    "Reporting export failed": "Standard",
    "Webhook delivery delayed": "Standard",
    "Dashboard permission denied": "Standard"
}

problem_summary["business_criticality"] = (
    problem_summary["issue_signature"]
    .map(service_criticality_map)
    .fillna("Unclassified")
)

criticality_rank = {
    "Critical": 1,
    "High": 2,
    "Standard": 3,
    "Unclassified": 4
}

# Apply the simulated approved temporary override
problem_summary["effective_criticality"] = (
    problem_summary["business_criticality"]
)

# Scheduled override remains independently authorised
scheduled_override_active = (
    override_start <= simulation_time < override_end
)

# Emergency exception is valid only while within
# its two-hour window and not rejected.
emergency_override_active = (
    emergency_requested
    and elapsed_minutes < 120
    and review_status != "Rejected"
)

# Either valid authorisation can elevate criticality.
override_active = (
    scheduled_override_active
    or emergency_override_active
)

if override_active:
    problem_summary.loc[
        problem_summary["issue_signature"]
        == "Payroll rounding mismatch",
        "effective_criticality"
    ] = "Critical"

problem_summary["criticality_rank"] = (
    problem_summary["effective_criticality"]
    .map(criticality_rank)
)

problem_summary = problem_summary[
    problem_summary["ticket_count"] >= recurrence_threshold
].copy()

problem_summary = problem_summary.sort_values(
    [
        "criticality_rank",
        "sla_breaches",
        "escalations",
        "ticket_count"
    ],
    ascending=[True, False, False, False]
)

# Explain the factors used in the investigation ranking
def explain_problem_ranking(row):
    explanation = (
        f"Effective criticality: {row['effective_criticality']}; "
        f"{row['sla_breaches']} SLA breaches; "
        f"{row['escalations']} escalations; "
        f"{row['ticket_count']} recurring tickets."
    )

    if row["effective_criticality"] != row["business_criticality"]:
        explanation += " Temporary criticality override applied."

    return explanation

problem_summary["ranking_explanation"] = (
    problem_summary.apply(explain_problem_ranking, axis=1)
)

if problem_summary.empty:
    st.info(
        "No recurring issue groups meet the current "
        "filters and recurrence threshold."
    )
else:
    st.dataframe(
        problem_summary[
            [
                "issue_signature",
                "business_criticality",
                "effective_criticality",
                "ticket_count",
                "sla_breaches",
                "escalations"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )


    st.subheader("Issue Investigation Details")

    selected_issue = st.selectbox(
        "Select an issue to investigate",
        problem_summary["issue_signature"].tolist(),
        key="investigation_issue"
    )

    selected_problem = problem_summary.loc[
        problem_summary["issue_signature"] == selected_issue
    ].iloc[0]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Recurring Tickets",
                  int(selected_problem["ticket_count"]))

    with col2:
        st.metric("SLA Breaches",
                  int(selected_problem["sla_breaches"]))

    with col3:
        st.metric("Escalations",
                  int(selected_problem["escalations"]))

    st.write(
        "Normal business criticality:",
        selected_problem["business_criticality"]
    )

    st.write(
        "Effective business criticality:",
        selected_problem["effective_criticality"]
    )

    st.info(selected_problem["ranking_explanation"])

    if (
        selected_problem["business_criticality"]
        != selected_problem["effective_criticality"]
    ):
        if scheduled_active:
            st.warning(
                "A fictional scheduled override is active, "
                "with Payroll Service Owner approval."
            )
        elif emergency_active:
            if review_status == "Pending review":
                st.warning(
                    "A simulated emergency override is active. "
                    "Retrospective approval is pending, and "
                    "the exception expires after two hours."
                )
            else:
                st.info(
                    "A simulated emergency override is active "
                    "with retrospective approval recorded. "
                    "The two-hour expiry still applies."
                )

st.caption(
    "Prototype investigation ranking. Business criticality "
    "is simulated; this is not an approved operational queue."
)
