from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
import csv
@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=100,
    )
    download_csv_file()
    open_robot_order_website()
    close_annoying_modal()
    submit_orders()

def open_robot_order_website():
    """Navigates to the given URL."""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    # orders = get_orders()

def download_csv_file():
    """Downloads csv file from the given URL."""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def submit_single_order(data):
    """Submit an order on the website."""
    page = browser.page()
    page.select_option("#head", data[1])
    

def close_annoying_modal():
   # browser.wait_until_page_contains_element('element_locator')
   browser.page().click("button:text('OK')")
   
def submit_orders():
    """Get the orders from the csv."""
    with open('orders.csv', 'r') as file:
      reader = csv.reader(file)
      row_count = 0
      for row in reader:
          if row_count > 0:
            submit_single_order(row)
          row_count += 1

def save_pdf_orders():
    """Save each order HTML receipt as a PDF file."""
