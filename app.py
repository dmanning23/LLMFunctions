import os
import streamlit as st
from openai import OpenAI
#from keys import openAIapikey
from langchain.schema import (SystemMessage, HumanMessage, AIMessage)
import json

def extract_student_info(name, major, school, grades, club):
    #Get the student information
    return f"{name} is majoring in {major} at {school}. He has {grades} GPA and he is an active member of the university's {club}."

def extract_school_info(name, ranking, country, no_of_students):
    #Get the school information
    return f"{name} is located in the {country}. The university is ranked #{ranking} in the world with {no_of_students} students."

def printResponse(response_message):
    if response_message.function_call:
        # Which function call was invoked
        function_called = response_message.function_call.name
        
        # Extracting the arguments
        function_args  = json.loads(response_message.function_call.arguments)
        
        # Function names
        available_functions = {
            "extract_school_info": extract_school_info,
            "extract_student_info": extract_student_info
        }
        
        fuction_to_call = available_functions[function_called]
        response_message = fuction_to_call(*list(function_args.values()))
    else:
        response_message = response_message.content
    #write the response
    st.subheader(response_message)

def main():
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    #os.environ["OPENAI_API_KEY"] = openAIapikey

    st.set_page_config(
        page_title="Use OpenAI Functions",
        page_icon="🤖")
    
    student_1_description = "David Nguyen is a sophomore majoring in computer science at Stanford University. He is Asian American and has a 3.8 GPA. David is known for his programming skills and is an active member of the university's Robotics Club. He hopes to pursue a career in artificial intelligence after graduating."
    student_2_description = "Ravi Patel is a sophomore majoring in computer science at the University of Michigan. He is South Asian Indian American and has a 3.7 GPA. Ravi is an active member of the university's Chess Club and the South Asian Student Association. He hopes to pursue a career in software engineering after graduating."
    school_1_description = "Stanford University is a private research university located in Stanford, California, United States. It was founded in 1885 by Leland Stanford and his wife, Jane Stanford, in memory of their only child, Leland Stanford Jr. The university is ranked #5 in the world by QS World University Rankings. It has over 17,000 students, including about 7,600 undergraduates and 9,500 graduates23. "

    custom_functions = [
    {
        'name': 'extract_student_info',
        'description': 'Get the student information from the body of the input text',
        'parameters': {
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                    'description': 'Name of the person'
                },
                'major': {
                    'type': 'string',
                    'description': 'Major subject.'
                },
                'school': {
                    'type': 'string',
                    'description': 'The university name.'
                },
                'grades': {
                    'type': 'integer',
                    'description': 'GPA of the student.'
                },
                'club': {
                    'type': 'string',
                    'description': 'School club for extracurricular activities. '
                }
            }
        }
    },
    {
        'name': 'extract_school_info',
        'description': 'Get the school information from the body of the input text',
        'parameters': {
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                    'description': 'Name of the school.'
                },
                'ranking': {
                    'type': 'integer',
                    'description': 'QS world ranking of the school.'
                },
                'country': {
                    'type': 'string',
                    'description': 'Country of the school.'
                },
                'no_of_students': {
                    'type': 'integer',
                    'description': 'Number of students enrolled in the school.'
                }
            }
        }
    }
]
    
    container = st.container()
    with container:
        with st.form(key="my form", clear_on_submit=True):
            user_input  = st.text_area(label="Student or school info: ", key="input", height = 100)
            submit_button = st.form_submit_button(label="Ask")

        client = OpenAI()
        if submit_button and user_input:
            #The user entered some text, pass that with our functions
            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model = 'gpt-3.5-turbo',
                    messages = [{'role': 'user', 'content': user_input}],
                    functions = custom_functions,
                    function_call = 'auto')
                printResponse(response.choices[0].message)
            
        elif submit_button:

            descriptions = [
                student_1_description, 
                student_2_description,
                "Who was a Abraham Lincoln?",
                school_1_description]
            with st.spinner("Thinking..."):
                for description in descriptions:
                    response = client.chat.completions.create(
                        model = 'gpt-3.5-turbo',
                        messages = [{'role': 'user', 'content': description}],
                        functions = custom_functions,
                        function_call = 'auto')
                    printResponse(response.choices[0].message)

if __name__ == "__main__":
    main()