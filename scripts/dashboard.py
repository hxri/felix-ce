import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict

st.set_page_config(page_title="Video Generation Dashboard", layout="wide")

st.title("📊 Video Generation Model Comparison Dashboard")

# ============================================================
# Load metadata from outputs/videos
# ============================================================
VIDEOS_DIR = Path("outputs/videos")

def load_all_metadata():
    """Recursively load all meta_*.json files from videos directory."""
    metadata_list = []
    
    if not VIDEOS_DIR.exists():
        st.error(f"Videos directory not found: {VIDEOS_DIR}")
        return []
    
    for meta_file in VIDEOS_DIR.rglob("meta_*.json"):
        try:
            with open(meta_file, "r") as f:
                data = json.load(f)
                data["metadata_file"] = str(meta_file)
                data["video_dir"] = meta_file.parent.name
                metadata_list.append(data)
        except Exception as e:
            st.warning(f"Failed to load {meta_file}: {e}")
    
    return metadata_list

metadata_list = load_all_metadata()

if not metadata_list:
    st.warning("No metadata files found. Run the pipeline first to generate videos.")
    st.stop()

# ============================================================
# Create DataFrame for analysis
# ============================================================
df_data = []
for meta in metadata_list:
    video_dir = meta.get("video_dir", "unknown")
    latency = meta.get("latency_sec", 0)
    timestamp = meta.get("timestamp", "")
    
    df_data.append({
        "Model": video_dir,  # Use video_dir as the model name
        "Video Directory": video_dir,
        "Latency (s)": latency,
        "Timestamp": timestamp,
        "Full Model": meta.get("model", ""),
        "Reference Image": meta.get("reference_image", ""),
        "Prompt": meta.get("prompt", ""),
    })

df = pd.DataFrame(df_data)

# ============================================================
# SIDEBAR: Filters
# ============================================================
st.sidebar.header("Filters")
selected_models = st.sidebar.multiselect(
    "Select Models to Compare",
    options=df["Model"].unique(),
    default=df["Model"].unique(),
)

df_filtered = df[df["Model"].isin(selected_models)]

# ============================================================
# MAIN CONTENT
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Videos Generated", len(df_filtered))

with col2:
    avg_latency = df_filtered["Latency (s)"].mean()
    st.metric("Avg Latency (s)", f"{avg_latency:.2f}")

with col3:
    models_count = df_filtered["Model"].nunique()
    st.metric("Models Tested", models_count)

st.divider()

# ============================================================
# Latency Comparison Chart
# ============================================================
st.subheader("⚡ Latency Comparison by Model")

latency_by_model = df_filtered.groupby("Model")["Latency (s)"].agg(["mean", "count", "min", "max"]).reset_index()
latency_by_model.columns = ["Model", "Avg Latency", "Count", "Min", "Max"]

fig_latency = px.bar(
    latency_by_model,
    x="Model",
    y="Avg Latency",
    color="Model",
    title="Average Latency by Model",
    labels={"Avg Latency": "Latency (seconds)"},
    text="Avg Latency",
)
fig_latency.update_traces(texttemplate='%{text:.2f}s', textposition='outside')
st.plotly_chart(fig_latency, use_container_width=True)

# ============================================================
# Detailed Statistics Table
# ============================================================
st.subheader("📋 Detailed Model Statistics")

stats_table = latency_by_model.copy()
stats_table["Avg Latency"] = stats_table["Avg Latency"].apply(lambda x: f"{x:.2f}s")
stats_table["Min"] = stats_table["Min"].apply(lambda x: f"{x:.2f}s")
stats_table["Max"] = stats_table["Max"].apply(lambda x: f"{x:.2f}s")

st.dataframe(stats_table, use_container_width=True)

# ============================================================
# Latency Distribution (Box Plot)
# ============================================================
st.subheader("📊 Latency Distribution")

fig_box = px.box(
    df_filtered,
    x="Model",
    y="Latency (s)",
    title="Latency Distribution Across All Generations",
    color="Model",
)
st.plotly_chart(fig_box, use_container_width=True)

# ============================================================
# Timeline: When were videos generated
# ============================================================
st.subheader("⏱️ Generation Timeline")

df_filtered["Timestamp"] = pd.to_datetime(df_filtered["Timestamp"])
df_timeline = df_filtered.sort_values("Timestamp")

fig_timeline = px.scatter(
    df_timeline,
    x="Timestamp",
    y="Latency (s)",
    color="Model",
    title="Video Generation Timeline (Latency over Time)",
    hover_data=["Model", "Latency (s)"],
)
st.plotly_chart(fig_timeline, use_container_width=True)

# ============================================================
# All Videos Table
# ============================================================
st.subheader("🎬 All Generated Videos")

display_df = df_filtered[["Model", "Video Directory", "Latency (s)", "Timestamp"]].copy()
display_df["Latency (s)"] = display_df["Latency (s)"].apply(lambda x: f"{x:.2f}s")
display_df = display_df.sort_values("Timestamp", ascending=False)

st.dataframe(display_df, use_container_width=True)

# ============================================================
# Raw Metadata Inspector
# ============================================================
st.subheader("🔍 Raw Metadata Inspector")

selected_video = st.selectbox(
    "Select a video to view full metadata:",
    options=[f"{row['Model']} - {row['Timestamp']}" for _, row in df_filtered.iterrows()],
)

if selected_video:
    idx = df_filtered.index[
        df_filtered.apply(lambda row: f"{row['Model']} - {row['Timestamp']}" == selected_video, axis=1)
    ][0]
    selected_meta = metadata_list[idx]
    st.json(selected_meta)

# ============================================================
# Download Report
# ============================================================
st.divider()
st.subheader("📥 Download Report")

csv_data = df_filtered[["Model", "Latency (s)", "Timestamp"]].to_csv(index=False)
st.download_button(
    label="Download CSV Report",
    data=csv_data,
    file_name=f"video_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv",
)

# Summary JSON
summary_json = {
    "generated_at": datetime.now().isoformat(),
    "total_videos": len(df_filtered),
    "models_tested": df_filtered["Model"].unique().tolist(),
    "statistics": latency_by_model.to_dict("records"),
}
st.download_button(
    label="Download Summary JSON",
    data=json.dumps(summary_json, indent=2),
    file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
    mime="application/json",
)