from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
import time

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
    open_robot_order_website()
    close_annoying_modal()
    submit_orders()
    archive_receipts()

def order_url():
    return "https://robotsparebinindustries.com/#/robot-order"

def open_robot_order_website():
    """Navigates to the given URL."""
    browser.goto(order_url())

def get_orders():
    """Downloads csv file from the given URL."""
    lib = Tables()
    HTTP().download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    orders = lib.read_table_from_csv(
      "orders.csv", columns=["Order number", "Head", "Body", "Legs", "Address"]
    )
    return orders


def fill_the_form(order):
      """Submit an order on the website."""
      page = browser.page()
      page.select_option("#head", order["Head"])
      page.click("#id-body-" + order["Body"])
      page.get_by_placeholder("Enter the part number for the legs").fill(order["Legs"])
      page.fill("#address", order["Address"])
      page.click("button:text('Preview')")
      page.click("button:text('Order')")
      try:
        while page.get_by_role("alert").count() > 0:
          page.click("button:text('Order')")
          if page.get_by_role("alert").count() < 1:
              break
      except Exception as e:
         print(f"Clicking ORDER button failed with error: {str(e)}")
      else:
        screenshot = screenshot_robot(order["Order number"])
        receipt = store_receipt_as_pdf(order["Order number"])
        embed_screenshot_to_receipt(screenshot, receipt)
         

      # page.get_by_text("Receipt").wait_for()
      # Hint: in debug mode you can actually use browser.page().pause() in the debug console (when paused in a breakpoint)
      # page.pause()
      # time.sleep(5)
      page.get_by_role("button", name="Order another robot").click(timeout=10000) # click("button:text('Order another robot')")
      

def close_annoying_modal():
   page = browser.page()
   # page.wait_for_selector(page.get_by_role("dialog"))
   # page.get_by_role("dialog").wait_for()
   # while page.get_by_role("dialog") < 1:
   #while page.get_by_role("dialog").locator("div").nth(2).count() > 0:
   page.click("button:text('OK')")
#    while True:
#       page.get_by_role("button", name="OK").click()
#       if not page.get_by_role("dialog").locator("div").nth(2).count() > 0:
#         break

   # page.get_by_role("button", name="OK").click()
   
def submit_orders():
    """Get the orders from the csv."""
    orders = get_orders()
    page = browser.page()
    for order in orders:
          fill_the_form(order)
          # page.pause()
          close_annoying_modal()
          # page.get_by_role("button", name="OK").click()
            
def store_receipt_as_pdf(order_number):
    """Save each order HTML receipt as a PDF file."""
    filepath = "output/receipts/pdf/robot-order-" + order_number + ".pdf"
    try:
      PDF().html_to_pdf(browser.page().locator("#receipt").inner_html(), filepath)
    except Exception as e:
      print(f"Storing receipt PDF for order {order_number} failed with error: {str(e)}")
    return filepath

def screenshot_robot(order_number):
    """Take a screenshot of the robot order."""
    filepath = "output/receipts/screenshot/robot-order-" + order_number + "-screenshot.png"
    try:
      browser.page().screenshot(path=filepath)
    except Exception as e:
      print(f"Storing screenshot for order {order_number} failed with error: {str(e)}")
    return filepath

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Embed the screenshot in the receipt file."""
    try:
      p = PDF()
      p.add_files_to_pdf(
        files=[screenshot],
        target_document=pdf_file,
        append=True
      )
    except Exception as e:
        print(f"Embedding PDF for file {pdf_file} failed with error: {str(e)}")

def archive_receipts():
   Archive().archive_folder_with_zip('output/receipts', 'output/receipts.zip', recursive=True)
