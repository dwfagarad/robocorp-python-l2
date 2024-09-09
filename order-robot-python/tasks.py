from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    browser.configure(slowmo = 500)
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    download_csv_file()
    open_robot_order_website()
    fill_form_with_csv_data()
    archive_receipts()

def open_robot_order_website():
    """Open robot order website by navigating to the URL"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    
    
def download_csv_file():
    """Downloads csv file from the given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv",overwrite=True)
def get_orders():
    """Reads orders from csv file"""
    csv_file=Tables()
    csv_orders = csv_file.read_table_from_csv("orders.csv")
    return csv_orders

def fill_form_with_csv_data():
    """Read data from csv and fill in the robot order form"""
    orders = get_orders()
    for row in orders:
        fill_in_and_submit(row)

def fill_in_and_submit(row):
    """Fills in the robot order details and clicks the 'Order' button"""
    close_annoying_modal()
    page = browser.page()
    model_names = {
        "1" : "Roll-a-thor",
        "2" : "Peanut crusher",
        "3" : "D.A.V.E",
        "4" : "Andy Roid",
        "5" : "Spanner mate",
        "6" : "Drillbit 2000"
    }
    head_number = row["Head"]
    body_number = row["Body"]
    legs_number = row["Legs"]
    legs_selector = "xpath=//input[@placeholder='Enter the part number for the legs']"
    address = row["Address"]
    page.select_option("#head",head_number)
    body_input = model_names.get(body_number) + " body"
    page.click("text="+body_input)
    page.fill(legs_selector,legs_number)
    page.fill("#address",address)
    
    while page.query_selector("#order"):
        page.click("#order")
        
    screenshots_path = store_receipt_as_pdf(row["Order number"])
    receipts_path = screenshot_robot(row["Order number"])
    embed_screenshot_to_receipt(receipts_path,screenshots_path)

    page.click("#order-another")

def close_annoying_modal():
    """Clicks OK button on the pop-up"""
    page = browser.page()
    page.click("text=OK")

def store_receipt_as_pdf(order_number):
    """Export the data to a pdf file"""
    page = browser.page()
    receipts_html = page.locator("#receipt").inner_html()
    receipts_output_path = "output/receipts/receipt_" + order_number + ".pdf"
    pdf = PDF()
    pdf.html_to_pdf(receipts_html, receipts_output_path)
    return receipts_output_path

def screenshot_robot(order_number):
    """Takes screenshot of the ordered bot image"""
    screenshots_output_path = "output/screenshots/preview_" + order_number + ".png"
    page = browser.page()
    page.locator("#robot-preview-image").screenshot(path=screenshots_output_path)
    return screenshots_output_path

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Embeds the screenshot to the bot receipt"""
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(
        image_path = screenshot,
        source_path = pdf_file,
        output_path = pdf_file
    )
def archive_receipts():
    """Archives all the receipt pdfs into a single zip archive"""
    lib = Archive()
    lib.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")
    
