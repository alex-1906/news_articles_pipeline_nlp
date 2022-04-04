import streamlit as st
import spacy
import time
from collections import Counter
import streamlit_wordcloud
import pandas as pd
from geopy import geocoders

def main():
    menu = ["Home","Places","Persons","Organisations"]

    if "found_places" not in st.session_state:
        st.session_state['found_places'] = []
    if 'found_persons' not in st.session_state:
        st.session_state['found_persons'] = []
    if 'found_org' not in st.session_state:
        st.session_state['found_org'] = []



    st.sidebar.title("News Articles NLP")

    choice = st.sidebar.selectbox("Menu",menu)



    nlp = spacy.load('en_core_web_sm')


    if choice == "Home":
        st.title("News Articles NLP")
        input_menu = ['Example:CNN','File','String']
        input_choice = st.sidebar.selectbox('Choose your type of input',input_menu)
        document = ""
        if input_choice == "Example:CNN":
            #st.image("cnn_logo2.png")
            document = ""
            with open('example_cnn.txt') as f:
                lines = f.read()
                document += lines;
            with st.expander('Example CNN news article:', expanded=False):
                st.write(document)


        if input_choice == 'File':
            uploaded_file = st.file_uploader(label="Choose a file", type='txt')
            if uploaded_file is not None:
                bytes_data = uploaded_file.getvalue()
                raw_text = bytes_data.decode('utf-8')
                with st.expander('Your uploaded document',expanded=False):
                    st.write(raw_text)
                document = raw_text
        elif input_choice == 'String':
            document = st.text_input("Type in your text:")
        elif input_choice == "Examples":
            document = st.text_input("Type in your text:")
        available_nlp_engines = ['spacy','flair (currently maintained)']
        selected_engine =  st.selectbox('Choose your NLP engine',available_nlp_engines)



        if st.button('Click here to process your document') == True:
            with st.spinner('Processing your document, please wait a second.'):
                tic = time.time()
                doc = nlp(document)
                found_persons = []
                found_places = []
                found_org = []
                for ent in doc.ents:
                    if (ent.label_ == "GPE"):
                        found_places.append(ent.text)
                    if (ent.label_ == "PERSON"):
                        found_persons.append(ent.text)
                    if (ent.label_ == "ORG"):
                        found_org.append(ent.text)
                st.session_state['found_persons'] = found_persons
                st.session_state['found_places'] = found_places
                st.session_state['found_org'] = found_org
                html = spacy.displacy.render(doc,style="ent")
                toc = time.time()
                with st.expander(f'Your processed document {toc-tic}s',expanded=True):
                    st.success(f'Processing time: {toc-tic}s')
                    st.markdown(html, unsafe_allow_html=True)
                with st.expander('Explanation'):
                    st.markdown(
                        ''' ## NER Tags
<table>
<tr><th>TYPE</th><th>DESCRIPTION</th><th>EXAMPLE</th></tr>
<tr><td>`PERSON`</td><td>People, including fictional.</td><td>*Fred Flintstone*</td></tr>
<tr><td>`MISC`</td><td>Buildings, airports, highways, bridges, etc.</td><td>*Logan International Airport, The Golden Gate*</td></tr>
<tr><td>`ORG`</td><td>Companies, agencies, institutions, etc.</td><td>*Microsoft, FBI, MIT*</td></tr>
<tr><td>`GPE`</td><td>Countries, cities, states.</td><td>*France, UAR, Chicago, Idaho*</td></tr>
</table>''', unsafe_allow_html=True)






    elif choice == "Places":
        st.title("Found Places:")
        gn = geocoders.GeoNames("cip_geo")
        geocodes = []
        lat = []
        lon = []
        places_list = []
        for place in st.session_state['found_places']:

            geocode = gn.geocode(place)
            geocodes.append(geocode)
            lat.append(geocode.latitude)
            lon.append(geocode.longitude)
            places_list.append((place, geocode.latitude, geocode.longitude))
        places_set = set(places_list)
        df = pd.DataFrame()
        df["lat"] = lat
        df["lon"] = lon
        st.map(df)
        for p in places_set:
            st.write(f"{p[0]} -> {p[1]}, {p[2]}")

    elif choice == "Persons":
        st.title("Found Persons:")
        occurences = Counter(st.session_state['found_persons'])
        word_bank = []
        for key, value in occurences.items():
            word = {
                "text": key,
                "value": value
            }
            word_bank.append(word)

        streamlit_wordcloud.visualize(word_bank)

    elif choice == "Organisations":
        st.title("Found Organisations:")
        occurences = Counter(st.session_state['found_org'])
        word_bank = []
        for key, value in occurences.items():
            word = {
                "text": key,
                "value": value
            }
            word_bank.append(word)

        streamlit_wordcloud.visualize(word_bank)


if __name__=='__main__':
    main()
