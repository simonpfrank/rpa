from robocorp.tasks import task
from robocorp.tasks import get_output_dir
from robocorp import log
from RPA.HTTP import HTTP
from RPA.Excel.Files import Files
# import overriden Selenium with OPEN AI locator fixer
from LocatorFixer import SeleniumLocatorFixer

import os
import sys
import traceback

OUTPUT_DIR = get_output_dir()
    
@task    
def rpa_challenge():
    try:
        # Use Class which inherits Selenium and adds element not found fixer
        robot = SeleniumLocatorFixer()
        # Get Web site from env.json
        robot.open_available_browser(os.environ.get('WEBSITE'))
        
        # Get the download link. THIS WILL FAIL as it is spelt wrong
        download_link = robot.get_element_attribute('Download Exel','href')
        # Download the file
        file_path = os.path.join(OUTPUT_DIR,download_link.split('/')[-1])
        HTTP().download(download_link,target_file=file_path,overwrite=True)
        
        # Read the spreadsheet
        excel = Files()
        excel.open_workbook(file_path)
        people = excel.read_worksheet_as_table(header=True)
        excel.close_workbook()

        # Start the challenge
        robot.click_button("Start")
        for person in people:
            for column, value in person.items():
                locator = f'//div[label[text()="{column}"]]/input'
                robot.input_text(locator,value)
            robot.click_button('Submit')
        
        robot.screenshot(None,os.path.join(OUTPUT_DIR,'page.png'))
    except Exception as e:
        robot.screenshot(None,os.path.join(OUTPUT_DIR,'error.png'))
        stripped_message = str(e).split('\n')[0]
        log.critical(f"{traceback.format_exc()}\n{sys.exc_info()[2]}\n{stripped_message}")
        raise


# if executed outside of Robocorp
if __name__ == '__main__':
    rpa_challenge()