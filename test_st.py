import streamlit as st
from googletrans import Translator

# Initialize the translator
translator = Translator()

# Define function to translate text
def translate_text(text, dest_lang):
    translation = translator.translate(text, dest=dest_lang)
    return translation.text

# Store all texts in a dictionary for dynamic updates
texts = {
    "title": "Welcome to the App",
    "greeting": "Hello, how are you?",
    "submit_button": "Submit",
    "description": "This is a sample application demonstrating dynamic translation.",
}

# Allow the user to select a language
languages = {'English': 'en', 'Chinese': 'zh-tw', 'Spanish': 'es'}
selected_language = st.sidebar.selectbox("Select Language", list(languages.keys()))
dest_lang = languages[selected_language]

# Translate all text elements dynamically
translated_texts = {key: translate_text(value, dest_lang) for key, value in texts.items()}

# Use the translated texts in your Streamlit app
st.title(translated_texts["title"])
st.write(translated_texts["greeting"])
st.write(translated_texts["description"])
st.button(translated_texts["submit_button"])

