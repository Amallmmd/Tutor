from distutils import debug
import mysql.connector
import streamlit as st

# Establish a connection to MySQL Server
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Amal@123",
    database="newdb"
)
mycursor=mydb.cursor()
print("Connection Established")

# Fetch prompts from the database
def fetch_prompts():
    mycursor.execute("SELECT id, algebra_prompt, tutor_prompt, personality_prompt FROM prompt")
    return mycursor.fetchall()

if 'selected_algebra' not in st.session_state:
    st.session_state.selected_algebra = ""
if 'selected_tutor' not in st.session_state:
    st.session_state.selected_tutor = ""
if 'selected_personality' not in st.session_state:
    st.session_state.selected_personality = ""

def select_prompt():
    prompts = fetch_prompts()

    algebra_options = [row[1] for row in prompts if row[1] is not None]
    tutor_options = [row[2] for row in prompts if row[2] is not None]
    personality_options = [row[3] for row in prompts if row[3] is not None]
    # col1, col2, col3 = st.columns(3)
# with col1:
    selected_algebra = st.selectbox("Select Algebra Prompt", options=[""] + algebra_options, index=0)
    if st.button("OK", key="algebra_ok"):
        st.session_state.selected_algebra = selected_algebra

# with col2:
    selected_tutor = st.selectbox("Select Tutor Prompt", options=[""] + tutor_options, index=0)
    if st.button("OK", key="tutor_ok"):
        st.session_state.selected_tutor = selected_tutor

# with col3:
    selected_personality = st.selectbox("Select Personality Prompt", options=[""] + personality_options, index=0)
    if st.button("OK", key="personality_ok"):
        st.session_state.selected_personality = selected_personality

    st.write("Selected Algebra Prompt:", st.session_state.selected_algebra)
    st.write("Selected Tutor Prompt:", st.session_state.selected_tutor)
    st.write("Selected Personality Prompt:", st.session_state.selected_personality)
    # prompts = fetch_prompts()
    # prompt_options = {row[1]: row[0] for row in prompts}
    # selected_prompt = st.selectbox(f"Select the {prompt_type} Prompt", options=prompt_options.keys())
    # if selected_prompt:
    #     st.write(f"You selected: {selected_prompt}")
    #     selected_id = prompt_options[selected_prompt]
    
def add_prompt():
    def insert_or_update_prompt(column, prompt):
        # Check if there's an existing row that can be updated
        mycursor.execute(f"SELECT id FROM prompt WHERE {column} IS NULL LIMIT 1")
        result = mycursor.fetchone()

        if result:
            # Update existing row
            prompt_id = result[0]
            sql = f"UPDATE prompt SET {column} = %s WHERE id = %s"
            val = (prompt, prompt_id)
        else:
            # Insert new row
            sql = f"INSERT INTO prompt ({column}) VALUES (%s)"
            val = (prompt,)
        
        mycursor.execute(sql, val)
        mydb.commit()

    st.subheader("Add the Prompt")
    types_of_prompts = st.selectbox("Select a Prompt",["Algebra","Tutor","Personality"])
    prompt_text=st.text_input("Write your prompt here.")
    # email=st.text_input("Enter Email")
    if st.button("Add Prompt"):
        if types_of_prompts == "Algebra":
            insert_or_update_prompt("algebra_prompt", prompt_text)
            # sql= "insert into prompt(algebra_prompt) values(%s)"
            # val= (prompts,)
            # mycursor.execute(sql,val)
            # mydb.commit()
            # st.success("Record Created Successfully!!!")
        elif types_of_prompts == "Tutor":
            insert_or_update_prompt("tutor_prompt", prompt_text)
        elif types_of_prompts == "Personality":
            insert_or_update_prompt("personality_prompt", prompt_text)
        st.success(f"{types_of_prompts} Prompt Added Successfully!")


# Create Streamlit App
def main():

    # Display Options for CRUD Operations
    option=st.sidebar.selectbox("Select an Operation",["Select prompt","Create new prompt","Delete"])
    # Perform Selected CRUD Operations
    if option=="Create new prompt":
        add_prompt()

    elif option == "Select prompt":
        st.subheader("Read Prompts")
        select_prompt()
            
    elif option=="Delete":
        st.subheader("Delete a Record")
        id=st.number_input("Enter ID",min_value=1)
        if st.button("Delete"):
            sql="delete from prompt where id =%s"
            val=(id,)
            mycursor.execute(sql,val)
            mydb.commit()
            st.success("Record Deleted Successfully!!!")

if __name__ == "__main__":
    main()








