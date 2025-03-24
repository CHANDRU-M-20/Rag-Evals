import streamlit as st
import json
import time
from datetime import datetime
from pathlib import Path

BASE_FOLDER = "data"  # Update this with your actual base path

if "add_file_key" not in st.session_state:
    st.session_state.add_file_key = 0

# Step 1: Get all subfolders dynamically (HDR, FTSA, etc.)
subfolders = [f.name for f in Path(BASE_FOLDER).iterdir() if f.is_dir()]

st.title("JSONL File Appender")

# Step 2: Select a Subfolder (HDR, FTSA, etc.)
selected_subfolder = st.selectbox("Select a subfolder", subfolders)

# Step 3: Get JSONL files in selected subfolder
folder_path = Path(BASE_FOLDER) / selected_subfolder
jsonl_files = [f.name for f in folder_path.glob("*.jsonl")]

if not jsonl_files:
    st.warning(f"No JSONL files found in {selected_subfolder}.")
else:
    selected_file = st.selectbox("Select a JSONL file", jsonl_files)

    file_path = folder_path / selected_file

    # Step 4: Choose an option (Upload a file OR enter JSONL manually)
    option = st.radio("Choose an option", ["Upload JSONL File", "Enter JSONL Data Manually"])

    if option == "Upload JSONL File":
        uploaded_file = st.file_uploader("Upload a JSONL file", type=["jsonl"], key=f"upload_file_{st.session_state.add_file_key}")

        if uploaded_file and st.button("Append File"):
            # Progress bar
            progress_bar = st.progress(0)

            with st.spinner("Appending file..."):
                for percent_complete in range(1, 101):
                    time.sleep(0.01)  # Simulate upload time
                    progress_bar.progress(percent_complete)

                try:
                    with open(file_path, "ab") as f:  # Append mode
                        f.write(uploaded_file.getbuffer())

                    st.success(f"✅ {uploaded_file.name} appended to {selected_file} successfully!")
                except Exception as e:
                    st.error(f"❌ Error appending file: {e}")

            # Reset file uploader
            st.session_state.add_file_key += 1
            st.rerun()

    elif option == "Enter JSONL Data Manually":
        user_input = st.text_area("Enter JSONL data (one JSON per line)")

        if st.button("Append JSONL Data"):
            if user_input.strip():
                try:
                    jsonl_lines = user_input.strip().split("\n")
                    with open(file_path, "a") as f:  # Append mode
                        for line in jsonl_lines:
                            json.loads(line)  # Validate JSON format
                            f.write(line + "\n")

                    st.success("✅ JSONL data appended successfully!")
                except json.JSONDecodeError:
                    st.error("❌ Invalid JSON format. Ensure each line is a valid JSON.")
            else:
                st.warning("⚠️ No JSONL data provided.")


# import streamlit as st
# import json
# import time
# from datetime import datetime
# from pathlib import Path

# BASE_FOLDER = "data_set/INPUTS"  # Update this with your actual base path

# if "add_file_key" not in st.session_state:
#     st.session_state.add_file_key = 0

# # Step 1: Get all subfolders dynamically
# subfolders = [f.name for f in Path(BASE_FOLDER).iterdir() if f.is_dir()]

# st.title("JSONL File Appender with Validation")

# # Step 2: Select a Subfolder (HDR, FTSA, etc.)
# selected_subfolder = st.selectbox("Select a subfolder", subfolders)

# # Step 3: Get JSONL files in selected subfolder
# folder_path = Path(BASE_FOLDER) / selected_subfolder
# jsonl_files = [f.name for f in folder_path.glob("*.jsonl")]

# if not jsonl_files:
#     st.warning(f"No JSONL files found in {selected_subfolder}.")
# else:
#     selected_file = st.selectbox("Select a JSONL file", jsonl_files)

#     file_path = folder_path / selected_file

#     # Step 4: Choose an option (Upload a file OR enter JSONL manually)
#     option = st.radio("Choose an option", ["Upload JSONL File", "Enter JSONL Data Manually"])

#     if option == "Upload JSONL File":
#         uploaded_file = st.file_uploader("Upload a JSONL file", type=["jsonl"], key=f"upload_file_{st.session_state.add_file_key}")

#         if uploaded_file and st.button("Append File"):
#             try:
#                 jsonl_lines = uploaded_file.getvalue().decode("utf-8").strip().split("\n")

#                 # Validate JSONL format
#                 for line in jsonl_lines:
#                     json.loads(line)  # This ensures each line is valid JSON

#                 # Progress bar
#                 progress_bar = st.progress(0)
#                 with st.spinner("Appending file..."):
#                     for percent_complete in range(1, 101):
#                         time.sleep(0.01)  # Simulate upload time
#                         progress_bar.progress(percent_complete)

#                     with open(file_path, "a") as f:  # Append mode
#                         f.write("\n".join(jsonl_lines) + "\n")

#                 st.success(f"✅ {uploaded_file.name} appended to {selected_file} successfully!")

#             except json.JSONDecodeError:
#                 st.error("❌ Invalid JSONL file! Each line must be a valid JSON object.")

#             except Exception as e:
#                 st.error(f"❌ Error processing file: {e}")

#             # Reset file uploader
#             st.session_state.add_file_key += 1
#             st.rerun()

#     elif option == "Enter JSONL Data Manually":
#         user_input = st.text_area("Enter JSONL data (one JSON per line)")

#         if st.button("Append JSONL Data"):
#             if user_input.strip():
#                 try:
#                     jsonl_lines = user_input.strip().split("\n")

#                     # Validate JSONL format
#                     for line in jsonl_lines:
#                         json.loads(line)  # Ensures each line is a valid JSON

#                     with open(file_path, "a") as f:  # Append mode
#                         f.write("\n".join(jsonl_lines) + "\n")

#                     st.success("✅ JSONL data appended successfully!")

#                 except json.JSONDecodeError:
#                     st.error("❌ Invalid JSON format! Ensure each line is a valid JSON object.")

#             else:
#                 st.warning("⚠️ No JSONL data provided.")
