import streamlit as st
import pandas as pd
import requests

# Load the CSV file
@st.cache_data
def load_data():
    file_path = 'CMApprovalGoodBad-CrossTabs-Weighted-ByRows.csv'
    data = pd.read_csv(file_path)
    return data

data = load_data()

# Function to query the Gemini API
def query_gemini_api(prompt):
    api_key = "AIzaSyAVWLvWEzncrWx7rxd72cGnJJkoOOmqB0Y"
    model_name = "gemini-2.5-pro-preview-06-05"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Function to analyze the data
def analyze_data(question, df):
    if "top categories" in question.lower():
        if 'Approval Rating' in df.columns and 'Category' in df.columns:
            top_categories = df.nlargest(5, 'Approval Rating')[['Category', 'Approval Rating']]
            return top_categories

    elif "lowest categories" in question.lower():
        if 'Approval Rating' in df.columns and 'Category' in df.columns:
            lowest_categories = df.nsmallest(5, 'Approval Rating')[['Category', 'Approval Rating']]
            return lowest_categories

    elif "average approval" in question.lower():
        if 'Approval Rating' in df.columns:
            avg = df['Approval Rating'].mean()
            return f"The average approval rating is {avg:.2f}%"

    elif "show data" in question.lower() or "display data" in question.lower():
        return df.head()

    return None

# Streamlit app layout
def main():
    st.title("Approval Ratings Analysis Tool")

    # Display basic data info
    st.sidebar.header("Data Overview")
    st.sidebar.write(f"Total rows: {len(data)}")
    st.sidebar.write("Columns:", ", ".join(data.columns))

    # Show sample data
    if st.sidebar.checkbox("Show sample data"):
        st.sidebar.dataframe(data.head())

    # Create a form for the user input
    with st.form("question_form"):
        user_input = st.text_input("Ask a question about the approval ratings data:")
        submitted = st.form_submit_button("Submit")

    if submitted and user_input:
        data_answer = analyze_data(user_input, data)

        if data_answer is not None:
            st.subheader("Data Analysis Result")
            if isinstance(data_answer, pd.DataFrame):
                st.dataframe(data_answer)
                st.bar_chart(data_answer.set_index(data_answer.columns[0]))
            else:
                st.write(data_answer)
        else:
            st.write("Consulting AI for additional insights...")

            data_context = f"Here's some approval ratings data:\n{data.head().to_string()}\n\n"
            full_prompt = f"{data_context}\n\nQuestion: {user_input}\n\nJust give a clear sentence with the answer from the data. No detailed explanation, just one proper line."

            result = query_gemini_api(full_prompt)

            if "error" in result:
                st.error(f"An error occurred: {result['error']}")
            else:
                try:
                    text_content = result['candidates'][0]['content']['parts'][0]['text']
                    st.write(text_content)
                except KeyError:
                    st.error("Could not extract text from the response.")

if __name__ == "__main__":
    main()