import streamlit as st

def display_eval_results():
    st.title("Evaluation Results")
    
    # Sample data for demonstration
    results = {
        "Metric A": 0.85,
        "Metric B": 0.90,
        "Metric C": 0.75,
    }
    
    # Display results in a table
    st.subheader("Metrics Overview")
    st.table(results)

    # Optionally, you can add visualizations here
    st.subheader("Visualizations")
    st.bar_chart(results)

if __name__ == "__main__":
    display_eval_results()