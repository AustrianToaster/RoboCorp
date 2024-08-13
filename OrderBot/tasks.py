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
    open_order_site()
    download_order_list()
    fill_form()
    archive_receipts()

def open_order_site():
    """
    Opens the Website to order a new Bot
    """
    browser.configure(slowmo = 1000)
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    close_popup()

def close_popup():
    """Closes the annoying popup of the order site"""
    page = browser.page()
    page.click("text=OK")

def download_order_list():
    """Downloads the order list"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def get_orders():
    """Copies the order from the .csv file into a loopable collection"""
    table = Tables()
    orders = table.read_table_from_csv("orders.csv", columns=["Order number", "Head", "Body", "Legs", "Address"])
    return orders

def fill_form():
    """Fills out the form to build a robot"""
    orders = get_orders()
    page = browser.page()
    
    def get_head():
        if order["Head"] == '1':
            return 'Roll-a-thor head'
        elif order["Head"] == '2':
            return 'Peanut crusher head'
        elif order["Head"] == '3':
            return 'D.A.V.E head'
        elif order["Head"] == '4':
            return 'Andy Roid head'
        elif order["Head"] == '5':
            return 'Spanner mate head'
        elif order["Head"] == '6':
            return 'Drillbit 2000 head'
        
    def get_body():
        if order["Body"] == '1':
            return '#id-body-1'
        elif order["Body"] == '2':
            return '#id-body-1'
        elif order["Body"] == '3':
            return '#id-body-1'
        elif order["Body"] == '4':
            return '#id-body-1'
        elif order["Body"] == '5':
            return '#id-body-1'
        elif order["Body"] == '6':
            return '#id-body-1'
        

    for order in orders:
        page = browser.page()
        page.select_option("#head", get_head())
        page.click(get_body())
        page.fill("input[placeholder='Enter the part number for the legs']", order["Legs"])
        page.fill("#address", order["Address"])
        while 1:
            page.click("#order")
            ordernext_button = page.query_selector("#order-another")
            if ordernext_button:
                pdf = store_receipt_as_pdf(order["Order number"])
                image = screenshot_robot(order["Order number"])
                embed_screenshot_to_receipt(image, order["Order number"])
                page.click("#order-another")
                close_popup()
                break;

def store_receipt_as_pdf(order_number):
    pdf = PDF()
    page = browser.page()
    path = f"output/order/{order_number}.pdf"
    order_html = page.locator("#receipt").inner_html()
    pdf.html_to_pdf(order_html, path)
    return path
    
def screenshot_robot(order_number):
    page = browser.page()
    path = f"output/order/{order_number}.png"
    preview = page.query_selector("#robot-preview-image")
    preview.screenshot(path=path)
    return path

def embed_screenshot_to_receipt(screenshot, order_number):
    pdf = PDF()
    list_of_files = [screenshot]
    pdf.add_files_to_pdf(files=list_of_files, target_document=f"output/{order_number}.pdf", append=True)

def archive_receipts():
    archive = Archive()
    archive.archive_folder_with_zip(f"output/order", "receipts.zip")