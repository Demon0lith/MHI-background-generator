#!/usr/bin/env python3
from core import config
from core.core import ApplicationCore

import streamlit as st
import streamlit_antd_components as sac
from streamlit_image_select import image_select
import logging

from PIL import Image
import urllib.request 

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("logger")

class Application(object):
    def __init__(self, core: ApplicationCore):
        super(Application, self).__init__()
        self.core = core
        st.session_state.color = "#000"
        st.session_state.selected = ""

        st.session_state.inscription = ""
        self.session = requests.Session()
        self.session.headers.update(
            {'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'close', 'Te': 'trailers'}
        )

    def setup(self):
        """ Method responsible for generating the general application setup """

        # Set page header
        icon = Image.open('core/images/logo.png')
        st.set_page_config(
            page_title="Mutant Hound Inscription Background Generator", layout="wide", page_icon=icon
        )

        # Custom HTML/CSS for the banner
        custom_html = """
        <div class="banner">
            <img src="https://inscriptions.novellabs.xyz/static/media/Logo.23ccec6e35785ba076fa.png" alt="Banner Image">
        </div>
        <style>
            .banner {
                width: 100%;
                overflow: hidden;
            }
            .banner img {
                width: 30%;
                object-fit: cover;
            }
        </style>
        """
        # Display the custom HTML
        st.components.v1.html(custom_html, height = 100)

        # Set copyright
        st.write("Created by @_demonolith. Feel free to reach out via MH Discord if you have any suggestions to improve this app.")
        st.write("**Note that this app will be available up until the moment the official MH tooling is rolled out.**")

        # Set search bar
        self.text_field(label=":mag:", placeholder = 'Enter inscription number (e.g., 70300943)')
        
        col1, col2 = st.columns([5, 20])
        with col1:
            st.session_state.selected = st.radio(
                "**Do you want to pick a background color using the color wheel, or use one of the available templates?**",
                key="visibility",
                options=["Color wheel", "Available templates"],
                index=0,
            )
        with col2:
            if st.session_state.selected == "Color wheel":
                clr = st.color_picker('Select a background color:', '#000')
                st.session_state.color = self.hex_to_rgb(clr)
            if st.session_state.selected == "Available templates":
                st.session_state.img = image_select(
                    label="Select a template (credits go to @HudsonGroupNFT and rubengg.eth):",
                    images=[
                        Image.open("core/images/templates/0.jpeg"),
                        Image.open("core/images/templates/1.jpeg"),
                        Image.open("core/images/templates/2.jpeg"),
                        Image.open("core/images/templates/3.jpeg"),
                        Image.open("core/images/templates/4.png"),
                    ], index=0
                )
        sac.divider(label='', align='center', key="divider-1")
        

    def text_field(self, label, columns=None, **input_params):
        with st.form('chat_input_form', clear_on_submit=True):
            # Sets a default key parameter to avoid duplicate key errors
            input_params.setdefault("key", label)
            
            c0, c1, c2 = st.columns(columns or [15, 5, 1])
            with c2:
                c2.markdown("##")
                submitted = st.form_submit_button(label)
            st.write("Inscription number can be extracted from ord.io (for instance, see https://www.ord.io/70300943)")

            # Forward text input parameters
            input = c0.text_input("", **input_params)
            st.session_state.inscription = input.replace(",", "")
            if len(st.session_state.inscription) > 0:
                st.write(f"**Selected inscription # {st.session_state.inscription}**")
            else:
                st.write("##")

    def hex_to_rgb(self, value):
        """Return (red, green, blue) for the color given as #rrggbb."""
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

    def fix_image(self, image):
        self.col1.image(image)

        fixed = image.convert("RGBA")        
        if st.session_state.selected == "Color wheel":
            new_image = Image.new("RGBA", fixed.size, st.session_state.color)
            new_image.paste(fixed, mask=fixed)
            self.col2.image(new_image)
            new_image.save("processed.png")
        if st.session_state.selected == "Available templates":
            st.session_state.img.paste(fixed, mask=fixed)
            self.col2.image(st.session_state.img)
            st.session_state.img.save("processed.png")
        
        with self.col2:
            st.download_button(label="Download image", data=open('processed.png', 'rb').read(), file_name=f"MHI-inscription-{st.session_state.inscription}.png", mime="image/jpeg")

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
