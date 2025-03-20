import streamlit as st

def chat_page():
    st.title("Chat Page")
    
    # Input field for user messages
    user_input = st.text_input("Type your message:")
    
    # Display area for chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if st.button("Send"):
        if user_input:
            st.session_state.chat_history.append(user_input)
            st.text_input("Type your message:", value="", key="new_input")  # Clear input field

    # Display chat history
    st.subheader("Chat History")
    for message in st.session_state.chat_history:
        st.write(message)

if __name__ == "__main__":
    chat_page()