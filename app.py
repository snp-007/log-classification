import streamlit as st
import pandas as pd
import plotly.express as px

from streamlit_option_menu import option_menu

from classify import classify_log
from processor_regex import classify_with_regex
from processor_bert import classify_with_bert


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Hybrid Log Classification",
    page_icon="📋",
    layout="wide"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.block-container{
    padding-top:1rem;
}

[data-testid="stSidebar"]{
    background-color: transparent;
}

.stMetric{
    border:1px solid #ddd;
    border-radius:10px;
    padding:10px;
}

h1{
    text-align:center;
}

.prediction-box {
    padding: 15px;
    border-radius: 10px;
    border: 2px solid #28a745;
    margin-top: 10px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# SESSION STATE
# =====================================================

if "history" not in st.session_state:
    st.session_state.history = []

# =====================================================
# HELPERS
# =====================================================

def get_route(source, log_message):

    if source == "LegacyCRM":
        return "LLM"

    regex_result = classify_with_regex(log_message)

    if regex_result:
        return "Regex"

    return "Embedding Model"


# =====================================================
# TITLE
# =====================================================

st.title("📋 Hybrid Log Classification System")

st.markdown(
    "A hybrid AI system combining **Regex**, **Sentence Transformers**, **Machine Learning**, and **LLM Classification**."
)

# =====================================================
# SIDEBAR NAVIGATION
# =====================================================

with st.sidebar:

    page = option_menu(
        menu_title="Navigation",
        options=[
            "Single Log Prediction",
            "Batch CSV Prediction",
            "Analytics Dashboard",
            "Architecture",
            "About Model"
        ],
        icons=[
            "search",
            "file-earmark-spreadsheet",
            "bar-chart",
            "diagram-3",
            "info-circle"
        ],
        menu_icon="list",
        default_index=0
    )

# =====================================================
# SINGLE LOG PREDICTION
# =====================================================

if page == "Single Log Prediction":

    st.header("Single Log Prediction")

    col1, col2 = st.columns([2, 1])

    with col1:

        source = st.selectbox(
            "Source System",
            [
                "ModernCRM",
                "ModernHR",
                "BillingSystem",
                "AnalyticsEngine",
                "ThirdPartyAPI",
                "LegacyCRM"
            ]
        )

        log_message = st.text_area(
            "Log Message",
            height=180
        )

        with st.expander("Sample Logs"):

            st.code("""
IP 192.168.133.114 blocked due to potential attack

Backup completed successfully.

Case escalation for ticket ID 7324 failed because the assigned support agent is no longer active.
            """)

        if st.button("🚀 Classify Log"):

            if log_message.strip():

                route = get_route(
                    source,
                    log_message
                )

                prediction = classify_log(
                    source,
                    log_message
                )

                st.session_state.history.append(
                    {
                        "Source": source,
                        "Prediction": prediction,
                        "Route": route
                    }
                )

                st.success(
                    f"Predicted Category: {prediction}"
                )

                st.info(
                    f"Classification Route: {route}"
                )

                if route == "Embedding Model":

                    _, confidence = classify_with_bert(
                        log_message
                    )

                    st.metric(
                        "Confidence Score",
                        f"{confidence:.2%}"
                    )

    with col2:

        st.subheader("Pipeline")

        st.markdown("""
        **Regex → Embeddings → ML → LLM**

        Routing Logic:

        - LegacyCRM → LLM
        - Regex Match → Return Label
        - Otherwise → Embedding Model
        - Confidence < 0.5 → Unclassified
        """)

    if st.session_state.history:

        st.divider()

        st.subheader("Prediction History")

        history_df = pd.DataFrame(
            st.session_state.history
        )

        st.dataframe(
            history_df,
            use_container_width=True
        )

# =====================================================
# BATCH CSV PREDICTION
# =====================================================

elif page == "Batch CSV Prediction":

    st.header("Batch CSV Prediction")

    st.markdown("""
    Upload a CSV containing:

    ```csv
    source,log_message
    ```
    """)

    uploaded_file = st.file_uploader(
        "Upload CSV",
        type=["csv"]
    )

    if uploaded_file:

        df = pd.read_csv(uploaded_file)

        st.subheader("Preview")

        st.dataframe(
            df.head(),
            use_container_width=True
        )

        if st.button("🚀 Classify CSV"):

            predictions = []

            total_rows = len(df)

            progress_bar = st.progress(0)

            with st.spinner(
                f"Classifying {total_rows} logs..."
            ):

                for idx, (src, msg) in enumerate(
                    zip(
                        df["source"],
                        df["log_message"]
                    )
                ):

                    predictions.append(
                        classify_log(src, msg)
                    )

                    progress_bar.progress(
                        (idx + 1) / total_rows
                    )

            progress_bar.empty()

            df["target_label"] = predictions

            st.success(
                f"Successfully classified {total_rows} logs."
            )

            st.dataframe(
                df,
                use_container_width=True
            )

            csv = df.to_csv(
                index=False
            )

            st.download_button(
                label="📥 Download Results",
                data=csv,
                file_name="classified_logs.csv",
                mime="text/csv"
            )

# =====================================================
# ANALYTICS DASHBOARD
# =====================================================

elif page == "Analytics Dashboard":

    st.header("Analytics Dashboard")

    uploaded_file = st.file_uploader(
        "Upload Classified CSV",
        type=["csv"]
    )

    if uploaded_file:

        df = pd.read_csv(uploaded_file)

        if "target_label" in df.columns:

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Total Logs",
                len(df)
            )

            col2.metric(
                "Unique Categories",
                df["target_label"].nunique()
            )

            col3.metric(
                "Most Common Label",
                df["target_label"].mode()[0]
            )

            counts = (
                df["target_label"]
                .value_counts()
                .reset_index()
            )

            counts.columns = [
                "Category",
                "Count"
            ]

            fig = px.bar(
                counts,
                x="Category",
                y="Count",
                title="Prediction Distribution"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            pie = px.pie(
                counts,
                names="Category",
                values="Count",
                title="Category Share"
            )

            st.plotly_chart(
                pie,
                use_container_width=True
            )

            st.subheader("Category Summary")

            st.dataframe(
                counts,
                use_container_width=True
            )

        else:

            st.error(
                "CSV must contain target_label column."
            )

# =====================================================
# ARCHITECTURE
# =====================================================

elif page == "Architecture":

    st.header("System Architecture")

    st.image(
        "resources/architecture.png",
        use_container_width=True
    )

    st.markdown("""
### Processing Pipeline

**Regex Layer**
- Fast deterministic classification
- Handles User Actions and System Notifications

**Embedding Layer**
- all-MiniLM-L6-v2 Sentence Transformer
- Converts logs into dense vector embeddings

**Classification Layer**
- Logistic Regression classifier
- Predicts operational incident categories

**LLM Layer**
- Groq llama-3.3-70b-versatile
- Handles sparse LegacyCRM categories

**Confidence Threshold**
- Predictions below 0.5 confidence become Unclassified
""")

# =====================================================
# ABOUT MODEL
# =====================================================

elif page == "About Model":

    st.header("About Model")

    st.markdown("""
## Hybrid Log Classification Pipeline

This system combines multiple AI approaches:

### Regex Pattern Matching
High-confidence deterministic classification.

### Sentence Transformer Embeddings
Converts logs into semantic vector representations.

### Logistic Regression
Classifies operational incidents using embeddings.

### Groq LLM Classification
Handles sparse LegacyCRM categories.

---

## Routing Logic

1. LegacyCRM → LLM
2. Regex Match → Return Label
3. Embedding Model → Predict Label
4. Confidence < 0.5 → Unclassified

---

## Models Used

- all-MiniLM-L6-v2
- LogisticRegression(max_iter=1000)
- llama-3.3-70b-versatile

---

## Supported Categories

- HTTP Status
- Security Alert
- Resource Usage
- Error
- Critical Error
- User Action
- System Notification
- Workflow Error
- Deprecation Warning
""")