import streamlit as st
import google.generativeai as genai
from PIL import Image
import traceback
import logging

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)

# --- Configuration and Error Handling ---
try:
    GEMINI_API_KEY = "AIzaSyD9hmqBaXvZqAUxQ3mnejzM_EwPMeZQod4"
    genai.configure(api_key=GEMINI_API_KEY)
except KeyError:
    st.error("API key not found in secrets.toml. Please ensure it is correctly configured.")
    logging.error("API key not found in secrets.toml.")
    st.stop()
except Exception as e:
    error_message = f"Error configuring API: {e}\n{traceback.format_exc()}"
    st.error("Error initializing AI model.")
    logging.error(error_message)
    st.stop()

# --- Firebox AI Class ---
class FireboxAI:
    def __init__(self, model_name="gemini-pro", max_tokens=2048):
        self.model = genai.GenerativeModel(
            model_name, generation_config={"max_output_tokens": max_tokens}
        )

    def ask_gemini(self, prompt):
        try:
            response = self.model.generate_content(prompt)
            if response and response.text:
                return response.text
            else:
                return "Error: No valid response from Firebox AI."
        except Exception as e:
            error_message = f"Gemini API call error: {e}\n{traceback.format_exc()}"
            st.error(error_message)
            logging.error(error_message)
            return "An error occurred while processing the request."

    def refine_response(self, response, refine_prompt=None):
        if not refine_prompt:
            refine_prompt = (
                "Rewrite the following response in a more informative, empathetic, and structured way. "
                "More General and Welcoming, Slightly More Formal. "
                "If the input contains 'your' or 'you're', replace them with: "
                "'Firebox AI, created by Kushagra Srivastava, is a cutting-edge AI assistant designed to provide "
                "smart, insightful, and highly adaptive responses.'\n\n"
                f"Original Response:\n{response}"
            )
        try:
            improved_response = self.model.generate_content(refine_prompt)
            if improved_response and improved_response.text:
                return self.replace_your(improved_response.text)
            else:
                return response
        except Exception as e:
            error_message = f"Response refinement error: {e}\n{traceback.format_exc()}"
            st.error(error_message)
            logging.error(error_message)
            return response

    def replace_your(self, text):
        description = (
            "Firebox AI, created by Kushagra Srivastava, is a cutting-edge AI assistant designed to provide "
            "smart, insightful, and highly adaptive responses."
        )
        return text.replace("your", description).replace("Your", description).replace("you're", description).replace("You're", description)

# --- Image Processing ---
def process_image(uploaded_file):
    try:
        image = Image.open(uploaded_file)
        gray_image = image.convert('L')  # Convert to grayscale
        return "Image processed successfully."
    except Exception as e:
        error_message = f"Image processing error: {e}\n{traceback.format_exc()}"
        st.error(error_message)
        logging.error(error_message)
        return "Failed to process image."

# --- File Upload Handler ---
def handle_file_upload():
    try:
        uploaded_file = st.file_uploader("Upload file", type=["png", "jpg", "jpeg"])
        if uploaded_file:
            file_type = uploaded_file.type
            if "image" in file_type:
                return process_image(uploaded_file)
            else:
                st.warning("Unsupported file type. Please upload an image.")
                return None
        return None
    except Exception as e:
        error_message = f"File upload error: {e}\n{traceback.format_exc()}"
        st.error(error_message)
        logging.error(error_message)
        return "File upload failed."

# --- Streamlit UI Setup ---
st.set_page_config(page_title="Firebox AI", layout="wide")

st.markdown(
    """
    <style>
        #MainMenu, footer, header, .viewerBadge_container__1QSob, .viewerBadge_link__1S1BI, .viewerBadge_button__13la3, .css-1y4p8pa {
            visibility: hidden !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.title("🔥 Firebox AI")
st.title("Firebox AI Assistant")

# Initialize session state for chat messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Checkbox to enable/disable response refinement
refine_response_enabled = st.sidebar.checkbox("Refine Response", value=True)
ai = FireboxAI()

# --- Main Logic ---
try:
    file_result = handle_file_upload()
    query = st.chat_input("Ask Firebox AI...")

    if file_result:
        with st.chat_message("user"):
            st.markdown(file_result)
        with st.spinner("Generating response..."):
            initial_response = ai.ask_gemini(file_result)
            firebox_response = ai.refine_response(initial_response) if refine_response_enabled else initial_response
        with st.chat_message("assistant"):
            st.markdown(firebox_response)
        st.session_state.messages.append({"role": "user", "content": file_result})
        st.session_state.messages.append({"role": "assistant", "content": firebox_response})

    elif query:
        with st.chat_message("user"):
            st.markdown(query)
        with st.spinner("Generating response..."):
            initial_response = ai.ask_gemini(query)
            firebox_response = ai.refine_response(initial_response) if refine_response_enabled else initial_response
        with st.chat_message("assistant"):
            st.markdown(firebox_response)
        st.session_state.messages.append({"role": "user", "content": query})
        st.session_state.messages.append({"role": "assistant", "content": firebox_response})

    # --- Display Messages ---
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

except Exception as e:
    error_message = f"An unexpected error occurred: {e}\n{traceback.format_exc()}"
    st.error(error_message)
    logging.error(error_message)
    st.stop()
