import streamlit as st
import requests
import json
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="AI Content Generator",
    page_icon="🧠",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .stTextArea [data-baseweb=textarea] {
        min-height: 150px;
    }
    .reportview-container .main .block-container {
        max-width: 900px;
    }
    h1 {
        color: #2e86c1;
    }
</style>
""", unsafe_allow_html=True)

# Constants
API_ENDPOINT = "https://d9lskv83ek.execute-api.us-east-1.amazonaws.com/dev/agentbedrock"

# Session state
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = None

# --- UI Components ---
def show_header():
    st.title("📝 AI Content Generator")
    st.markdown("Create blog posts powered by AWS Bedrock")
    st.divider()

def input_section():
    topic = st.text_area(
        "**Content Topic**",
        value="",
        help="Enter the topic you want to generate content about",
        key="input_topic"
    )
    
    expertise = st.selectbox(
        "**Expertise Level**",
        options=["Beginner", "Intermediate", "Advanced"],
        index=0,
        key="input_expertise"
    )
    
    context = st.text_area(
        "**Additional Context (Optional)**",
        value="",
        help="Provide any specific requirements or audience details",
        key="input_context"
    )
    
    return topic.strip(), expertise, context.strip()

# --- Core Functions ---
def call_lambda_backend(topic: str, expertise: str, context: str):
    """Call the AWS Lambda endpoint"""
    payload = {
        "blogTopic": topic,
        "level": expertise,
        "context": context
    }
    
    try:
        response = requests.post(
            API_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            content = response.json()
            if "blog" in content:
                return content["blog"]
            return None
        else:
            st.error(f"API returned status code: {response.status_code}")
            return None
    
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None

# --- Main App Flow ---
def main():
    show_header()
    
    topic, expertise, context = input_section()
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🚀 Generate Content", use_container_width=True):
            with st.spinner("Generating content..."):
                content = call_lambda_backend(topic, expertise, context)
                
                if content:
                    st.session_state.generated_content = content
                    st.success("Content generated successfully!")
                else:
                    st.error("Failed to generate content. Please try again.")
    
    with col2:
        if st.button("🔄 Clear", use_container_width=True):
            st.session_state.generated_content = None
    
    if st.session_state.generated_content:
        blog = st.session_state.generated_content
        
        st.subheader("Generated Content")
        st.write(blog)
        
        st.download_button(
            label="📥 Download Content",
            data=blog,
            file_name=f"content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

if __name__ == "__main__":
    main()