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

def open_robot_order_website():
    """Navigates to the given URL."""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    # orders = get_orders() 1698078155622

def get_orders():
    """Downloads csv file from the given URL."""
    lib = Tables()
    HTTP().download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    orders = lib.read_table_from_csv(
      "orders.csv", columns=["Order number", "Head", "Body", "Legs", "Address"]
    )
    return orders


def submit_single_order(order):
      """Submit an order on the website."""
      try:
        page = browser.page()
        page.select_option("#head", order["Head"])
        page.click("#id-body-" + order["Body"])
        page.get_by_placeholder("Enter the part number for the legs").fill(order["Legs"])
        page.fill("#address", order["Address"])
        page.click("button:text('Preview')")
        page.click("button:text('Order')")
        embed_screenshot_to_receipt(screenshot_robot(order["Order number"]), store_receipt_as_pdf(order["Order number"]))
      except Exception as e:
         print(f"Attempt for order {order['Order number']} failed with error: {str(e)}")
         return False
      return True

def close_annoying_modal():
   browser.page().click("button:text('OK')")
   
def submit_orders():
    """Get the orders from the csv."""
    orders = get_orders()
    for order in orders:
      if not submit_single_order(order):
         submit_single_order(order)

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
    p = PDF()
    p.add_files_to_pdf(
       files=[screenshot],
       target_document=pdf_file,
       append=True
    )

def archive_receipts():
   Archive().archive_folder_with_zip('output/receipts', 'receipts.zip')

