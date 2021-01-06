from flask import Flask, render_template, request, jsonify, make_response, send_file
import json
from io import BytesIO
from pdfdocument.document import PDFDocument

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload.pdf', methods=['POST']) 
def Upload():
	inputJsonFile = request.files['file']
	data = json.loads(inputJsonFile.read()) # data collected
	# filtering data into different categories
	# data = request.get_json()
	sellerName = data['sold_by']
	deliveryAgent = data['delivered_by']

	returnAddress = ""
	for addr in data['return_address'].values():
		returnAddress += str(addr)
		returnAddress += " "

	itemsToBeDilivered = [["PRODUCT", "DETAILS(opt)", "QTY"]]
	for item in data['line_items']:
		product = []
		for productDetails in item.values():
			product.append(str(productDetails))
		itemsToBeDilivered.append(product)

	orderDate = data['order_date']
	trackingId = data['tracking_id']

	pdfFile = BytesIO()
	pdf = PDFDocument(pdfFile)
	pdf.init_report()
	pdf.generate_style(font_size=12)

	#formatting of pdf begins
	pdf.h1('Rivia.AI')
	pdf.hr()
	pdf.h3("Sold by : " + sellerName)
	pdf.h3("Delivered by : " + deliveryAgent)
	pdf.hr()
	#adding shipping address
	pdf.h2("Shipping Address:")
	for part in data['shipping_address'].values():
		pdf.h2(part)
	pdf.hr()
	pdf.h3("Order Date : " + orderDate)
	pdf.h3("Tracking ID : " + trackingId)
	pdf.hr()
	pdf.table(itemsToBeDilivered, (100, 100, 100), style=pdf.style.table)
	pdf.hr()
	if(data['payment']['mode'] != "COD"):
		data['payment']['amount'] = 'Paid'
	pdf.h2("Invoice Value: " + str(data['payment']['amount']))
	pdf.hr()
	pdf.h3("Return Address: " + returnAddress)
	#formatting of pdf ends

	pdf.generate() #pdf generated

	result = make_response(pdfFile.getvalue())
	result.headers['Content-Type'] = 'application/pdf'
	result.headers['Content-Disposition'] = 'inline; filename=shippingLabel.pdf' # use inline instead of attachment to get the preview
	return result

if __name__ == "__main__":
    app.run(debug = True)