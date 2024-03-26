import databutton as db
import streamlit as st
import pandas as pd
import re
import openai
import os
from dotenv import load_dotenv
from openai import OpenAI
from ast import main


# Define the model to use
MODEL_NAME = "gpt-3.5-turbo"


def handle_openai_query(df, column_names):
    """
    Handle the OpenAI query and display the response.

    Parameters:
    - df: DataFrame containing the data
    - column_names: List of column names in the DataFrame
    """

    # Create a text area for user input
    query = st.text_area(
        "Enter your Prompt:",
        placeholder="Prompt tips: Use plotting related keywords such as 'Plots' or 'Charts' or 'Subplots'. Prompts must be concise and clear, example 'Bar plot for the first ten rows.'",
        help="""
            How an ideal prompt should look like? *Feel free to copy the format and adapt to your own dataset.*
            
            ```
            - Subplot 1: Line plot of the whole spectra.
            - Subplot 2: Zoom into the spectra in region 1000 and 1200.
            - Subplot 3: Compare the area of whole spectra and zoom spectra as Bar Plot.
            - Subplot 4: Area curve of the zoom spectra.
            ```
            """,
    )

    # If the "Get Answer" button is clicked
    if st.button("Get Answer"):
        # Ensure the query is not empty
        if query and query.strip() != "":
            # Define the prompt content
            prompt_content = f"""
            The dataset is ALREADY loaded into a DataFrame named 'df'. DO NOT load the data again.
            
            The DataFrame has the following columns: {column_names}
            
            Before plotting, ensure the data is ready:
            1. Check if columns that are supposed to be numeric are recognized as such. If not, attempt to convert them.
            2. Handle NaN values by filling with mean or median.
            
            Use package Pandas and Matplotlib ONLY.
            Provide SINGLE CODE BLOCK with a solution using Pandas and Matplotlib plots in a single figure to address the following query:
            
            {query}

            - USE SINGLE CODE BLOCK with a solution. 
            - Do NOT EXPLAIN the code 
            - DO NOT COMMENT the code. 
            - ALWAYS WRAP UP THE CODE IN A SINGLE CODE BLOCK.
            - The code block must start and end with ```
            
            - Example code format ```code```
        
            - Colors to use for background and axes of the figure : #F0F0F6
            - Try to use the following color palette for coloring the plots : #8f63ee #ced5ce #a27bf6 #3d3b41
            
            """

            # Define the messages for the OpenAI model
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful Data Visualization assistant who gives a single block without explaining or commenting the code to plot. IF ANYTHING NOT ABOUT THE DATA, JUST politely respond that you don't know.",
                },
                {"role": "user", "content": prompt_content},
            ]

            # Call OpenAI and display the response
            with st.status("📟 *Prompting is the new programming*..."):
                with st.chat_message("assistant", avatar="📊"):
                    botmsg = st.empty()
                    response = []
                    for chunk in openai.ChatCompletion.create(
                        model=MODEL_NAME, messages=messages, stream=True
                    ):
                        text = chunk.choices[0].get("delta", {}).get("content")
                        if text:
                            response.append(text)
                            result = "".join(response).strip()
                            botmsg.write(result)
            execute_openai_code(result, df, query)


def extract_code_from_markdown(md_text):
    """
    Extract Python code from markdown text.

    Parameters:
    - md_text: Markdown text containing the code

    Returns:
    - The extracted Python code
    """
    # Extract code between the delimiters
    code_blocks = re.findall(r"```(python)?(.*?)```", md_text, re.DOTALL)

    # Strip leading and trailing whitespace and join the code blocks
    code = "\n".join([block[1].strip() for block in code_blocks])

    return code


def execute_openai_code(response_text: str, df: pd.DataFrame, query):
    """
    Execute the code provided by OpenAI in the app.

    Parameters:
    - response_text: The response text from OpenAI
    - df: DataFrame containing the data
    - query: The user's query
    """

    # Extract code from the response text
    code = extract_code_from_markdown(response_text)

    # If there's code in the response, try to execute it
    if code:
        try:
            exec(code)
            st.pyplot()
        except Exception as e:
            error_message = str(e)
            st.error(
                f"📟 Apologies, failed to execute the code due to the error: {error_message}"
            )
            st.warning(
                """
                📟 Check the error message and the code executed above to investigate further.

                Pro tips:
                - Tweak your prompts to overcome the error 
                - Use the words 'Plot'/ 'Subplot'
                - Use simpler, concise words
                - Remember, I'm specialized in displaying charts not in conveying information about the dataset
            """
            )
    else:
        st.write(response_text)


def get_data():
    """
    Upload data via a file.

    Returns:
    - df: DataFrame containing the uploaded data or None if no data was uploaded
    """
    
    # File uploader for data file
    file_types = ["csv", "xlsx", "xls"]
    data_upload = st.file_uploader("Upload a data file", type=file_types)
    
    if data_upload:
        # Check the type of file uploaded and read accordingly
        if data_upload.name.endswith('.csv'):
            df = pd.read_csv(data_upload)
        elif data_upload.name.endswith('.xlsx') or data_upload.name.endswith('.xls'):
            df = pd.read_excel(data_upload)
        else:
            df = None
        return df
    
    return data_upload

# App UI

# Suppress deprecation warnings related to Pyplot's global use
st.set_option("deprecation.showPyplotGlobalUse", False)


# Cache the header of the app to prevent re-rendering on each load
@st.cache_resource
def display_app_header():
    """Display the header of the Streamlit app."""
    st.image('logo.png')
    st.title("")
    st.markdown("***Upload your data, and see it visualized** ✨")


# Display the header of the app
display_app_header()

with st.expander("App Overview", expanded=False):
    st.markdown(
        """

    You will find each functions either in the library or in the main script. Feel free to modu
    - **App Header:** The function `display_app_header` defines the title and a brief description of the app, setting the context for the user. This function is displayed at the top of the app when called on line 24.
       
    - **API Key Check:** The `key_check` function is invoked to ensure the necessary API keys are present before proceeding. This might be for authentication or to access certain services.
    
    - **Data Upload and Display:** The app provides the user with an option to upload data using the `get_data` function (line 47). Once the data is uploaded, it's optionally displayed in an expandable section for the user to review.
    
    - **OpenAI Query Handling:** If the uploaded data is not empty, the `handle_openai_query` function is called (line 64) to process the user's prompt regarding the data and visualize it accordingly. If the uploaded data is empty, a warning is displayed to the user.  
    
    """
    )

# Check for the necessary API keys
# key_check() # A function to deal with KEY availability
# Alternatively, just using a text-input box

if load_dotenv():
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )
  
  

options = st.radio(
      "Data Usage", options=["Upload file"], horizontal=True
  )
if options == "Upload file":
      # Get data uploaded by the user
      df = get_data()

  
  
  # If data is uploaded successfully
if df is not None:
      # Create an expander to optionally display the uploaded data
      with st.expander("Show data"):
          st.write(df)
  
      # Extract column names for further processing
      column_names = ", ".join(df.columns)
  
      # Check if the uploaded DataFrame is not empty
      if not df.empty:
          # Handle the OpenAI query and display results
          handle_openai_query(df, column_names)
      else:
          # Display a warning if the uploaded data is empty
          st.warning("The given data is empty.")

if __name__ == "__main__":
    main()
