import streamlit as st
import requests
import os

API_URL = os.environ.get("API_URL", "http://localhost:8000/api/v1")

st.set_page_config(page_title="Dietary Guidance Chatbot", page_icon="🥗")

st.title("🥗 Dietary Guidance Chatbot")
st.write("Ask questions about nutrition, food safety, and healthy eating based on official guidelines.")

if "messages" not in st.session_state:
    st.session_state.messages = []

def fetch_documents():
    try:
        response = requests.get(f"{API_URL}/documents")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

docs = fetch_documents()
doc_options = {"All Documents": None}
for doc in docs:
    doc_options[doc["title"]] = doc["doc_id"]

st.sidebar.header("Filter by Document")
selected_doc = st.sidebar.selectbox("Select a document", list(doc_options.keys()))

st.sidebar.header("Corpus Documents")
for doc in docs:
    st.sidebar.markdown(f"**{doc['title']}** ({doc['publisher']}, {doc['year']})")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "citations" in msg and msg["citations"]:
            st.markdown("**Citations:**")
            for cit in msg["citations"]:
                st.markdown(f"- [{cit['document_name']}, {cit['publisher']}, {cit['year']}]({cit['source_url']})")
        if "refusal_type" in msg and msg["refusal_type"]:
            st.error(f"Refusal: {msg['refusal_type']}")

if prompt := st.chat_input("Ask a question (e.g. What does WHO recommend for daily salt intake?)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching and generating..."):
            filter_doc = doc_options[selected_doc]
            payload = {"query": prompt}
            if filter_doc:
                payload["filter_document"] = filter_doc
            
            try:
                response = requests.post(f"{API_URL}/chat", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer")
                    citations = data.get("citations", [])
                    refusal_type = data.get("refusal_type")
                    
                    st.markdown(answer)
                    if citations:
                        st.markdown("**Citations:**")
                        for cit in citations:
                            st.markdown(f"- [{cit['document_name']}, {cit['publisher']}, {cit['year']}]({cit['source_url']})")
                    if refusal_type:
                        st.error(f"Refusal: {refusal_type}")
                        
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "citations": citations,
                        "refusal_type": refusal_type
                    })
                else:
                    st.error(f"Error connecting to the API. Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                st.error(f"Failed to fetch response: {e}")
