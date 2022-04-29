import streamlit as st
import pandas as pd
import os
import openai
import urllib.request
import re
import ast
from streamlit_player import st_player

#Load API key only once, the first time the page is loaded
if "api_key" not in st.session_state:
  st.session_state.api_key = True
  openai.api_key = os.getenv("OPENAI_API_KEY")

st.markdown(
  """
  <style>
.css-qrbaxs {
    font-size: 20px;
}
.css-16huue1 {
    font-size: 20px;
}
  </style>
  """,
  unsafe_allow_html = True
)

user_input = st.text_area(label = 'Please describe the specific workout you are interested in today',
value = 'I am outdoors in a park and have no gym equipment. I want to exercise my legs. I have 60 minutes available. Please create a warm up, generate three leg exercises, and then a warm down.',
help = '''Analysis is completed using the GPT3 Davinci model.''')

# Progress bar for workout generation function
def workout_progess(func):
  def wrapper(user_input):
    with st.spinner('Generating workout...'):
      return func(user_input)
  return wrapper

# Progress bar for exercise extraction function
def extract_progess(func):
  def wrapper(response_text):
    with st.spinner('Extracting instructional videos...'):
      return func(response_text)
  return wrapper

@workout_progess
def generate_workout(user_input):
  prompt = '{}. Generate a workout plan according to the preceding criteria.'.format(user_input)
  response = openai.Completion.create(engine="text-davinci-002", prompt=prompt, temperature=0, max_tokens=2000)
  response_text = response.choices[0].text
  st.header('Your tailored workout:')
  st.info(response_text)
  return response_text

def find_url(query_string):
    query_string = query_string.replace(" ", "+")
    query_string = query_string + "+correct+technique"
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query={}".format(query_string))
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    return "https://www.youtube.com/watch?v=" + video_ids[0]

@extract_progess
def extract_exercises(response_text):
  prompt = "{}. Please create a python list containing all of the exercises described in the preceding text. ['".format(response_text)
  response = openai.Completion.create(engine="text-davinci-002", prompt=prompt, temperature=0, max_tokens=2000)
  final_response = ast.literal_eval("['" + response.choices[0].text)
  final_response = list(dict.fromkeys(final_response))
  st.header("Instructional videos for your exercises: ")
  for i, exercise in enumerate(final_response):
    with st.container():
      col1, col2 = st.columns([1,3])
      with col1:
        st.subheader(exercise)
      with col2:
        st_player(find_url(exercise), key=i)



generate_button = st.button('Generate tailored workout', on_click=None)

if generate_button == True:
  response_text = generate_workout(user_input)
  extract_exercises(response_text)
