
from robocorp.tasks import task
from robocorp.tasks import get_output_dir
from RPA.Robocorp.Vault import Vault
from robocorp import log
from RPA.Browser.Selenium import Selenium
from RPA.HTTP import HTTP
from RPA.Excel.Files import Files
from RPA.OpenAI import OpenAI
from SeleniumLibrary.errors import ElementNotFound
from bs4 import BeautifulSoup as soup
import lxml
import tiktoken

import os
import sys
import traceback

OUTPUT_DIR = get_output_dir()

gpt = OpenAI()
vault = Vault()

class SeleniumLocatorFixer(Selenium):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.locator_fixer(*args,**kwargs)
        
    def locator_fixer(self):
        # base element finder appears to be _element_finder.find
        original_function = self._element_finder.find
        # define new function which uses original
        def finder(*args,**kwargs):
            try:
                result = original_function(*args,**kwargs)
                return result
            except ElementNotFound as el:
                log.info(f'Element not found:{args[0]}. Attempting to fix')
                new_locator = self.fix_locator(args[0])
                log.info(f'Returned locator is:{new_locator}')
                new_args = list(args)
                new_args[0] = new_locator
                log.info('Attempting new locator')
                result = original_function(*new_args)
                # continue as before or exception will occur if not
                return result
        # replace original element finder
        self._element_finder.find = finder

    def get_page_source(self):
        # Get the current page to pass to Open AI
        source = self.get_source()
        file_path = os.path.join(OUTPUT_DIR,'page.html')
        # Save oringal page for diagnosis
        with open(file_path,'w') as f:
            f.writelines(source)
        
        # Strip out irrelevant tags
        page = soup(source,'html.parser')
        for tag in ['style', 'script','meta','head','path','svg']:
            [el.extract() for el in page.find_all(tag)]
        # Save new page for comparison
        with open(os.path.join(OUTPUT_DIR,'new_page.html'),'w') as f:
            f.write(str(page))
        return str(page)

    def count_tokens(self,prompt):
        # Count tokens in prompt
        encoding = tiktoken.get_encoding(os.environ.get("TOKEN_ENCODING"))
        num_tokens = len(encoding.encode(prompt))
        return num_tokens
    
    def fix_locator(self,locator):
        # Get the page source
        html = str(self.get_page_source())
        # Create prompt
        prompt = f"""You are an expert in HTML,rpaframework and xpath.
        The rpaframework locator {locator} has failed. Using your knowledge find the appropriate 
        locator in the html below. Avoid using html ids or names if the id or name do not resemble 
        words and in that case use xpath. Do not use class attributes in the xpath. When using xpath use the shortest possible relative xpath that 
        guarantees to make the locator work. Do not explain do not put any values in front (e.g. //xpath:) of the response just return the xpath.
        The html is as follows:
        {html}"""
        # Check prompt size
        token_count = self.count_tokens(prompt)
        if token_count > 4050:
            raise Exception('HTML source is too long for Chat GPT cannot fix locator')
        log.info('Querying OpenAI')
        _openai = vault.get_secret('openai')
        gpt.authorize_to_openai(_openai['key'])
        result = gpt.completion_create(prompt,temperature=int(os.environ.get('OPENAI_TEMP')))
        return result