import streamlit as st
from datetime import datetime
import hashlib
import pandas as pd
import json
import os

st.title("🎨 Art Piece Management System")

# ----------- File Management ------------
def load_data():
    """Load art data from JSON file."""
    if os.path.exists("art_pieces.json"):
        with open("art_pieces.json", "r") as f:
            data_dict = json.load(f)
        # Convert to DataFrame for display
        data_list = []
        for key, value in data_dict.items():
            value["id"] = key
            data_list.append(value)
        return pd.DataFrame(data_list), data_dict
    else:
        return pd.DataFrame(), {}

def save_data(data_dict):
    """Save art data to JSON file."""
    with open("art_pieces.json", "w") as f:
        json.dump(data_dict, f, indent=4)

def generate_id(combined):
    """Generate short unique ID."""
    return hashlib.md5(combined.encode()).hexdigest()[:8]

def delete_art(row_id, data_dict):
    """Delete an art record."""
    if row_id in data_dict:
        del data_dict[row_id]
        save_data(data_dict)
        return True
    return False

# ----------- Load Data ------------
df, data_dict = load_data()

# ----------- Sidebar Filter ------------
st.sidebar.header("🔍 Filter")

if not df.empty:
    filter_author = st.sidebar.text_input("Filter by Author")
    filter_name = st.sidebar.text_input("Filter by Art Piece Name")
    filter_category = st.sidebar.text_input("Filter by Category")
    filter_location = st.sidebar.text_input("Filter by Storage Location")
    filter_description = st.sidebar.text_input("Filter by Description")

    # Handle year filter
    if "created_year" in df.columns:
        year_col = pd.to_numeric(df["created_year"], errors="coerce")
        valid_years = year_col[year_col.notna()]
        if len(valid_years) > 0:
            min_year, max_year = max(0, int(valid_years.min())-1), min(int(valid_years.max()),10000)
            year_range = st.sidebar.slider(
                "Created Year Range",
                min_value=min_year,
                max_value=max_year,
                value=(min_year, max_year),
                step=1
            )
            start_year, end_year = year_range
        else:
            start_year, end_year = None, None
            st.sidebar.info("No year data available.")
    else:
        start_year, end_year = None, None

    # Apply filters
    filtered_df = df.copy()
    if filter_author:
        filtered_df = filtered_df[filtered_df["author"].str.contains(filter_author, case=False, na=False)]
    if filter_name:
        filtered_df = filtered_df[filtered_df["name"].str.contains(filter_name, case=False, na=False)]
    if filter_category:
        filtered_df = filtered_df[filtered_df["category"].str.contains(filter_category, case=False, na=False)]
    if filter_location:
        filtered_df = filtered_df[filtered_df["location"].str.contains(filter_location, case=False, na=False)]
    if filter_description:
        filtered_df = filtered_df[filtered_df["description"].str.contains(filter_description, case=False, na=False)]
    if start_year and end_year:
        filtered_df["created_year_num"] = pd.to_numeric(filtered_df["created_year"], errors="coerce")
        filtered_df = filtered_df[
            (filtered_df["created_year_num"] >= start_year)
            & (filtered_df["created_year_num"] <= end_year)
        ]
        filtered_df = filtered_df.drop(columns="created_year_num")

    st.sidebar.write(f"Showing {len(filtered_df)} / {len(df)} records")
    display_df = filtered_df
else:
    display_df = df

# ----------- Display Table ------------
if display_df.empty:
    st.info("No art records found. Add a new one below.")
else:
    st.subheader("🖼️ Existing Art Pieces")

    header_cols = st.columns([2, 2, 2, 1, 2, 4, 1, 1])
    headers = ["Author", "Name", "Category", "Year", "Location", "Description", "✏️ Edit", "🗑️ Delete"]
    for i, header in enumerate(headers):
        header_cols[i].markdown(f"**{header}**")

    for i, row in display_df.iterrows():
        cols = st.columns([2, 2, 2, 1, 2, 3, 1, 1])
        cols[0].write(row["author"])
        cols[1].write(row["name"])
        cols[2].write(row["category"])
        cols[3].write(row.get("created_year", ""))
        cols[4].write(row["location"])
        cols[5].write(row.get("description", ""))

        if cols[6].button("✏️", key=f"edit_{row['id']}"):
            st.session_state.current_edit_id = row["id"]

        if cols[7].button("🗑️", key=f"del_{row['id']}"):
            if delete_art(row["id"], data_dict):
                st.success("Deleted successfully!")
                st.rerun()

# ----------- Edit Form ------------
if "current_edit_id" in st.session_state and st.session_state.current_edit_id in data_dict:
    st.subheader("✏️ Edit Art Piece")
    current_data = data_dict[st.session_state.current_edit_id]

    edit_author = st.text_input("Author", current_data["author"])
    edit_name = st.text_input("Art Piece Name", current_data["name"])
    edit_category = st.text_input("Category", current_data["category"])
    edit_year = st.number_input(
        "Created Year",
        min_value=1000,
        max_value=9999,
        value=int(current_data.get("created_year", datetime.now().year)),
        step=1
    )
    edit_location = st.text_input("Storage Location", current_data["location"])
    edit_description = st.text_area("Description", current_data.get("description", ""))

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Changes"):
            updated = {
                "author": edit_author,
                "name": edit_name,
                "category": edit_category,
                "created_year": int(edit_year),
                "location": edit_location,
                "description": edit_description,
            }
            data_dict[st.session_state.current_edit_id] = updated
            save_data(data_dict)
            st.success("Art piece updated successfully!")
            del st.session_state.current_edit_id
            st.rerun()
    with col2:
        if st.button("❌ Cancel"):
            del st.session_state.current_edit_id
            st.rerun()

# ----------- Add New Art Piece ------------
st.subheader("➕ Add New Art Piece")

new_author = st.text_input("Author", key="new_author")
new_name = st.text_input("Art Piece Name", key="new_name")
new_category = st.text_input("Category", key="new_category")
new_year = st.number_input("Created Year", min_value=1000, max_value=9999, value=datetime.now().year, step=1)
new_location = st.text_input("Storage Location", key="new_location")
new_description = st.text_area("Description", key="new_description")

if st.button("💾 Save New Art Piece"):
    if new_author and new_name and new_category and new_location:
        combined = f"{new_author}-{new_name}-{new_category}-{new_year}-{new_location}-{new_description[:20]}"
        art_id = generate_id(combined)

        if art_id in data_dict:
            st.error("This art piece already exists.")
        else:
            data_dict[art_id] = {
                "author": new_author,
                "name": new_name,
                "category": new_category,
                "created_year": int(new_year),
                "location": new_location,
                "description": new_description,
            }
            save_data(data_dict)
            st.success("New art piece added!")
            st.rerun()
    else:
        st.error("Please fill in all fields before saving.")
