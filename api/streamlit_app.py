import requests
import streamlit as st

# TODO: use aiohttps to request the endpoints

# Base URL for the FastAPI application
base_url = "http://app:80"

# Default value for the input box
default_front = "아버지"

# Set the title of the Streamlit app
st.title("VocRec: Find the Similar FlashCards")


# Add a button to synchronize two dbs
if st.button("Sync the FlashCards"):
    url = base_url + "/sync/"
    response = requests.post(url)
    if response.status_code == 200:
        data = response.json()
        for item in data:
            if "msg" in item.keys():
                st.write(item.get("msg", "Errors"))
            elif "error" in item.keys():
                front_error = item["front"]
                error_msg = item["error"]
                st.write(f"[Sync Error]:{front_error}: {error_msg}")


# Add a text input box with a default value
input_text = st.text_input("Search", value=default_front)

# Button to trigger the search
if st.button("Find Similar FlashCards"):
    # Construct the URL and parameters for the GET request
    url = base_url + "/find_similar/"
    params = {"word": input_text}

    # Make the GET request to the FastAPI endpoint
    response = requests.get(url, params=params)

    # Check the response status code
    if response.status_code == 200:
        st.write("The Similar FlashCards: ")
        data = response.json()
        # Iterate over the recommendations and display each word
        rec_word_list = [item["word"] for item in data["recommendation"]]
        st.write(", ".join(rec_word_list))

    elif response.status_code == 405:
        st.write("No Similar FlashCards found!")
    else:
        st.write("!ERROR!")
