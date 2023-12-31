from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

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
        error_alert = page.locator('div.alert.alert-danger')
        while error_alert.count() > 0:
          page.click("button:text('Order')")
          if error_alert.count() < 1:
              break
      except Exception as e:
         print(f"Clicking ORDER button failed with error: {str(e)}")
      else:
        try:
          page.wait_for_selector("div#receipt", state="visible", timeout=5000)
          screenshot = screenshot_robot(order["Order number"])
          receipt = store_receipt_as_pdf(order["Order number"])
          embed_screenshot_to_receipt(screenshot, receipt)
          page.get_by_role("button", name="Order another robot").click(timeout=10000)
        except Exception as e:
          print(f"Screenshots failed with error: {str(e)}")
      
def close_annoying_modal():
   page = browser.page()
   page.click("button:text('OK')")
   
def submit_orders():
    """Get the orders from the csv."""
    orders = get_orders()
    for order in orders:
          fill_the_form(order)
          close_annoying_modal()
            
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
