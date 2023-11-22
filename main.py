import streamlit as st
from assistant import assistant
import textwrap

st.title = "YouTube Assistant"

if 'assistant' not in st.session_state:
    st.session_state.assistant = assistant(k=20)

with st.sidebar:
    with st.form(key='my_form'):
        url = st.text_input(label="YouTube URL")
        query = st.text_area(label="Question")
        submitted = st.form_submit_button(label='Submit')

if query and url and submitted:
    response, docs, history, prompt = st.session_state.assistant.get_response_from_query(url, query)

    st.subheader("Answer:")
    st.markdown(response)

    st.markdown("---")

    if prompt:
        with st.expander("Prompt"):            
            st.text(textwrap.fill(prompt.format_prompt(history=history, query=query, docs=docs).to_string(), 80))            

    st.markdown("---")

    if docs is not None:
        with st.expander("Documents"):
            if isinstance(docs, list) and len(docs) > 0:
                for i, doc in enumerate(docs):
                    st.subheader(f'Document {i+1}')
                    st.text(textwrap.fill(doc, 80))
            else:
                st.text(textwrap.fill(docs, 80))