import streamlit as st
from assistant import assistant
import textwrap
import asyncio

if 'assistant' not in st.session_state:
    st.session_state.assistant = assistant(k=20)

st.title("SHIPIT")

with st.sidebar:
    with st.form(key='my_form'):
        url = st.text_input(label="YouTube URL")
        query = st.text_area(label="Question")
        submitted = st.form_submit_button(label='Submit')

async def get_response_async():
    response, docs, history, prompt = await st.session_state.assistant.get_response_from_query(url, query)

    st.subheader("Answer:")
    st.markdown(response)

    st.markdown("---")

    if prompt:
        with st.expander("Prompt"):            
            st.text(textwrap.fill(prompt.format_prompt(history=history, query=query, docs=docs).to_string(), 80))            

    st.markdown("---")

    if docs is not None:
        with st.expander("Documents"):
            if isinstance(docs, list):
                if len(docs) > 0:
                    for i, doc in enumerate(docs):
                        st.subheader(f'Document {i+1}')
                        st.text(textwrap.fill(doc, 80))
                else:
                    st.text("No documents available")                    
            else:
                print(type(docs))
                st.text(textwrap.fill(docs, 80))

# Create a context manager to run an event loop
from contextlib import contextmanager

@contextmanager
def setup_event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        yield loop
    finally:
        loop.close()
        asyncio.set_event_loop(None)

if query and url and submitted:
    with setup_event_loop() as loop:
        loop.run_until_complete(get_response_async())

