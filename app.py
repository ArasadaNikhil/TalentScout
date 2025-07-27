import streamlit as st
import os
from dotenv import load_dotenv
from chatbot import TalentScoutChatbot

load_dotenv()

st.set_page_config(
    page_title="TalentScout Hiring Assistant",
    page_icon="🧑‍💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("🧑‍💻 TalentScout Hiring Assistant")
    
    if not os.getenv("GROQ_API_KEY"):
        st.error("GROQ_API_KEY not found!")
        st.stop()

    if "conversation_ended" not in st.session_state:
        st.session_state.conversation_ended = False

    if "chatbot" not in st.session_state:
        try:
            st.session_state.chatbot = TalentScoutChatbot()
        except Exception as e:
            st.error(f"Failed to initialize Groq: {e}")
            st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant", 
                "content": "Hello! Welcome to TalentScout. I'm your AI hiring assistant, and I'm excited to learn more about you today. Let's start with the basics - could you please tell me your full name?"
            }
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.session_state.conversation_ended:
        st.success("🎉 **Interview Complete!** Thank you for your time.")
        st.info("💡 **Next Steps:** Our team will review your responses and contact you soon.")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔄 Start New Interview", type="primary"):
                st.session_state.messages = [
                    {
                        "role": "assistant", 
                        "content": "Hello! Welcome to TalentScout. I'm your AI hiring assistant, and I'm excited to learn more about you today. Let's start with the basics - could you please tell me your full name?"
                    }
                ]
                st.session_state.chatbot = TalentScoutChatbot()
                st.session_state.conversation_ended = False
                st.rerun()
        
        st.chat_input("Interview completed. Click 'Start New Interview' to continue.", disabled=True)
    
    else:

        if prompt := st.chat_input("Type your response here... (type 'bye' or 'exit' to end)"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            if st.session_state.chatbot.is_exit_keyword(prompt):
                farewell = st.session_state.chatbot.get_farewell_message()
                with st.chat_message("assistant"):
                    st.markdown(farewell)
                st.session_state.messages.append({"role": "assistant", "content": farewell})
                st.session_state.conversation_ended = True
                st.rerun()
            
            else:
                with st.chat_message("assistant"):
                    with st.spinner("🤔 Thinking..."):
                        response = st.session_state.chatbot.get_response(prompt)
                        st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
    
    # Sidebar
    with st.sidebar:
        st.header("🔍 Interview Status")
        
        if st.session_state.conversation_ended:
            st.success("✅ **Interview Complete**")
        else:
            st.info("🔄 **Interview In Progress**")

if __name__ == "__main__":
    main()