import os
import streamlit as st
from streamlit_chat import message
from utilities.helper import LLMHelper

def check_variables_in_prompt():
    # Check if "summaries" is present in the string custom_prompt
    if "{summaries}" not in st.session_state.custom_chat_prompt:
        st.warning("""Your custom prompt doesn't contain the variable "{summaries}".  
        This variable is used to add the content of the documents retrieved from the VectorStore to the prompt.  
        Please add it to your custom prompt to use the app.  
        Reverting to default prompt.
        """)
        st.session_state.custom_chat_prompt = ""
    if "{question}" not in st.session_state.custom_chat_prompt:
        st.warning("""Your custom prompt doesn't contain the variable "{question}".  
        This variable is used to add the user's question to the prompt.  
        Please add it to your custom prompt to use the app.  
        Reverting to default prompt.  
        """)
        st.session_state.custom_chat_prompt = ""

def clear_text_input():
    st.session_state['question'] = st.session_state['input']
    st.session_state['input'] = ""

def clear_chat_data():
    st.session_state['question'] = None
    st.session_state['input'] = ""
    st.session_state['chat_history'] = []
    st.session_state['source_documents'] = []
    st.session_state['scores'] = []
    st.session_state['verbose_info'] = ""

# Initialize chat history
if 'custom_chat_prompt' not in st.session_state:
    st.session_state['custom_chat_prompt'] = ""
if 'custom_chat_temperature' not in st.session_state:
    st.session_state['custom_chat_temperature'] = float(os.getenv("OPENAI_TEMPERATURE", 0.7))
if 'custom_chain_type' not in st.session_state:
    st.session_state['custom_chain_type'] = "stuff"
if 'top_k' not in st.session_state:
    st.session_state['top_k'] = 4
if 'question' not in st.session_state:
    st.session_state['question'] = None
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'source_documents' not in st.session_state:
    st.session_state['source_documents'] = []
if 'verbose_info' not in st.session_state:
    st.session_state['verbose_info'] = ""
if 'scores' not in st.session_state:
    st.session_state['scores'] = []

# Setting
custom_chat_prompt_placeholder = """{summaries}
    Please reply to the question using only the information present in the text above.
    Include references to the sources you used to create the answer if those are relevant ("SOURCES").
    If you can't find it, reply politely that the information is not in the knowledge base.
    Question: {question}
    Answer:"""
custom_chat_prompt_help = """You can configure a custom prompt by adding the variables {summaries} and {question} to the prompt.
{summaries} will be replaced with the content of the documents retrieved from the VectorStore.
{question} will be replaced with the user's question.
    """

llm_helper = LLMHelper(custom_prompt=st.session_state.custom_chat_prompt, temperature=st.session_state.custom_chat_temperature)

col1, col3 = st.columns([2,4])
with col3:
    with st.expander("Settings"):
        st.slider("Temperature", min_value=0.0, max_value=1.0, step=0.1, key='custom_chat_temperature')
        st.text_area("Custom Prompt", key='custom_chat_prompt', on_change=check_variables_in_prompt,
                    placeholder=custom_chat_prompt_placeholder,help=custom_chat_prompt_help, height=250)
        # 在使用ChatOpenAI模型时, 目前无法使用stuff以外的功能
        # st.selectbox("QA Chain Type", ("stuff", "map_reduce", "refine", "map_rerank"), key='custom_chain_type')
        st.slider("Top K", min_value=1, max_value=10, step=1, key='top_k')

# Chat 
st.text_input("You: ", placeholder="type your question", key="input", on_change=clear_text_input)
clear_chat = st.button("Clear chat", key="clear_chat", on_click=clear_chat_data)

if st.session_state['question']:
    question, result, _, sources, verbose_info, scores = llm_helper.get_semantic_answer_lang_chain(st.session_state['question'], st.session_state['chat_history'],
                                                                                            top_k=st.session_state['top_k'])
    st.session_state['chat_history'].append((question, result))
    st.session_state['source_documents'].append(sources)
    st.session_state['scores'] = scores
    st.session_state['verbose_info'] = verbose_info

if st.session_state['chat_history']:
    for i in range(len(st.session_state['chat_history'])-1, -1, -1):
        message(st.session_state['chat_history'][i][1], key=str(i))
        st.markdown(f'\n\nSources: {st.session_state["source_documents"][i]}')
        message(st.session_state['chat_history'][i][0], is_user=True, key=str(i) + '_user')

with st.expander("Intermediate"):
    st.markdown('##### embeddings scores')
    st.markdown(st.session_state['scores'])
    st.markdown('##### verbose info')
    st.markdown(st.session_state['verbose_info'])
