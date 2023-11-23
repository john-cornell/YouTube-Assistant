import streamlit as st
import asyncio

st.session_state.from_main = "HERE"

async def async_task():
    st.write("Ctx Async task started")
    await asyncio.sleep(5)  # Simulate a long-running async task
    st.write("Ctx Async task finished")

    x = st.session_state.from_main
    st.text(f"From main: {x}")
    st.session_state.from_thread = "THREAD"

async def run_async_task():
    await async_task()
    st.text(st.session_state.from_thread)

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

def main():
    if st.button("Start Async Task"):
        with setup_event_loop() as loop:
            loop.run_until_complete(run_async_task())

st.title("Async Task Demo")
main()