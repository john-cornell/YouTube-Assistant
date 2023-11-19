import streamlit as st
import assistant
import textwrap

st.title = "YouTube Assistant"
with st.sidebar:
    with st.form(key='my_form'):
        url = st.text_input(label="YouTube URL")
        query = st.text_area(label="Question")
        submitted = st.form_submit_button(label='Submit')


if  query and url and submitted:
    response, docs, prompt = assistant.get_response_from_query(url, query)

    type(prompt)

    st.subheader("Answer:")
    st.markdown(response)

    st.markdown("---")

    if prompt:
        with st.expander("Prompt"):
            st.text(textwrap.fill(prompt.format_prompt(query=query, docs=docs).to_string(), 80))

    st.markdown("---")

    if docs or docs.__len__() > 0:
        with st.expander("Documents"):
            for i, doc in enumerate(docs):

                st.subheader(f'Document {i+1}')
                st.text(textwrap.fill(doc.page_content, 80))

                if doc.metadata:
                    st.json(doc.metadata)