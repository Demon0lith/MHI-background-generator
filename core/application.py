#!/usr/bin/env python3
from core import config
from core.core import ApplicationCore

import streamlit as st
import streamlit_antd_components as sac
import logging

from io import BytesIO
from PIL import Image
import urllib.request 

import requests
from bs4 import BeautifulSoup


logger = logging.getLogger("logger")

class Application(object):
    def __init__(self, core: ApplicationCore):
        super(Application, self).__init__()
        st.session_state.pictures={}
        self.core = core
        st.session_state.color = "#000"

        st.session_state.inscription = ""
        self.session = requests.Session()
        self.session.headers.update(
            {'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'close', 'Te': 'trailers'}
        )

    def setup(self):
        """ Method responsible for generating the general application setup """
        
        # Set page header
        st.set_page_config(
            page_title="Mutant Hound Inscription Background Generator", page_icon=":bar_chart:", layout="wide"
        )
        # Set search bar
        self.text_field(label=":mag:", placeholder = 'Enter inscription number (e.g., 70300943')
        clr = st.color_picker('Select a background color that you would like to add', '#000')

        sac.divider(label='', align='center', key="divider-1")
        st.session_state.color = self.hex_to_rgb(clr)

    def text_field(self, label, columns=None, **input_params):
        with st.form('chat_input_form', clear_on_submit=True):
            # Sets a default key parameter to avoid duplicate key errors
            input_params.setdefault("key", label)
            
            c0, c1, c2 = st.columns(columns or [15, 5, 1])
            with c2:
                c2.markdown("##")
                submitted = st.form_submit_button(label)
            st.write("Inscription number can be extracted from ord.io (for instance, see https://www.ord.io/70300943)")
            st.write("Make sure to enter the number of the inscription WITHOUT commas or #. Like: 70300943")
            
            # Forward text input parameters
            st.session_state.inscription = c0.text_input("", **input_params)
            if len(st.session_state.inscription)>0:
                st.write(f"Inscription # {st.session_state.inscription}")

    def hex_to_rgb(self, value):
        """Return (red, green, blue) for the color given as #rrggbb."""
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

    def fix_image(self, image):
        # image = Image.open(upload)
        self.col1.write("Original Image :camera:")
        self.col1.image(image)

        fixed = image.convert("RGBA")
        new_image = Image.new("RGBA", fixed.size, st.session_state.color)
        new_image.paste(fixed, mask=fixed)
        # fixed = remove(image, bgcolor=[0, 249, 2, 0])#)st.session_state.color)
        self.col2.write("Fixed Image :wrench:")
        self.col2.image(new_image)

    def parse_and_extract(self, r):
        """ Method responsible for parsing the extracted data """
        
        # Parse data 
        soup = BeautifulSoup(r, 'html.parser')

        og_image_meta = soup.find('meta', property='og:image')
        if og_image_meta:
            og_image_content = og_image_meta['content']
            image_id = og_image_content.split('?id=')[1].split('&')[0]
            return image_id
        else:
            print("No meta tag found with property='og:image'")
            return None

    def run(self):
        """ Method responsible for running the application """
        self.setup()
        
        self.col1, self.col2 = st.columns(2)
        base_url = 'https://www.ord.io/'

        # Scrape the page
        if len(st.session_state.inscription) > 0:
            response=self.session.get(f'{base_url}{st.session_state.inscription}', timeout=10)
            if response.status_code != 200:
                raise ValueError(f"scrape returned invalid status code {response.status_code}")
            
            imageid=self.parse_and_extract(r=response.text)
            url = f'https://ordin.s3.amazonaws.com/inscriptions/{imageid}'
            # response=self.session.get(url, timeout=10)
            urllib.request.urlretrieve(url, "mhi.png") 
            image_to_rescale = Image.open("mhi.png")
            
            rescaled_image = image_to_rescale.resize((500, 500), resample=Image.NEAREST)
            self.fix_image(rescaled_image)

                    

            

