# app.py
import streamlit as st
from retriever import handle_user_query, debug_query

st.title("💼 Invoice Intelligence")

query = st.text_input("Enter your query:")
if query:
    with st.spinner("Processing..."):
        answer = handle_user_query(query)
    st.markdown("### 📌 Answer")
    st.write(answer)

    if st.checkbox("🔍 Show Debug Info"):
        st.markdown("### Debug Info")
        debug_query(query)
