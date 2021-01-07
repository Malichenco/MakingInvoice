from flask import Flask, render_template, request, jsonify, make_response, send_file
import json
from io import BytesIO
from pdfdocument.document import PDFDocument
from reportlab.platypus import Table
from fpdf import FPDF



app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload.pdf', methods=['POST']) 
def Upload():
	inputJsonFile = request.files['file']
	if str(inputJsonFile.filename).endswith('.json'): # handling the case if file is not .JSON
		try:
			data = json.loads(inputJsonFile.read()) # data collected
			result = make_response(formatPdf(data).output(dest='S').encode('latin-1'))
			result.headers['Content-Type'] = 'application/pdf'
			result.headers['Content-Disposition'] = 'inline; filename=shippingLabel.pdf' # use inline instead of attachment to get the previe#w
			return result
		except:
			return "Exception occurred"
	else:
		return "Wrong File Uploaded"

def formatPdf(data):
	pdf = FPDF()
	pdf.add_page()
	pdf.set_font('Arial', 'B', 16)
	
	# title of the label 
	pdf.cell(w = 0,h = 15, txt='Rivia.Ai', border=0, ln=1, align = 'C')
	
	# adding seller 
	
	pdf.set_font('Arial', 'B', 12)
	pdf.cell(w = 95, h = 15, txt = "Sold By", border=0, ln = 0, align = 'L')
	pdf.set_font('Arial', '', 12)
	sellerName = ""
	if 'sold_by' in data.keys():
		sellerName = str(data['sold_by'])
	pdf.cell(w = 95, h = 15, txt = sellerName, border=0, ln = 1, align = 'R')
	
	pdf.set_font('Arial', 'B', 12)
	pdf.cell(w = 95, h = 15, txt = "Delivered By", border=0, ln = 0, align = 'L')
	pdf.set_font('Arial', '', 12)
	deliveryAgent = ""
	if 'delivered_by' in data.keys():
		deliveryAgent = str(data['delivered_by'])
	pdf.cell(w = 95, h = 15, txt = deliveryAgent, border=0, ln = 1, align = 'R')
	
	if 'shipping_address' in data.keys():
		pdf.set_font('Arial', 'B', 12)
		address = "Shipping Address:\n"
		for part in data['shipping_address'].values():
			address += part
			address += '\n'
		x = pdf.get_x()
		y = pdf.get_y()
		pdf.multi_cell(w = 95, h = 5, txt = address, border=0, align = 'L')
		p = pdf.get_x()
		q = pdf.get_y()
		x += 95
		pdf.set_xy(x, y)
		pdf.set_font('Arial', 'B', 30)
		if 'payment' in data.keys():
			if 'mode' in data['payment'].keys():
				pdf.cell(w = 95, h = q-y, txt = str(data['payment']['mode']), border=0, ln = 1, align = 'C')
		pdf.set_xy(p, q)

	pdf.cell(w = 95, h = 10, txt = "", border=0, ln = 0, align = 'L')
	pdf.cell(w = 95, h = 10, txt = "", border=0, ln = 1, align = 'R')
	
	pdf.set_font('Arial', 'B', 12)
	pdf.cell(w = 95, h = 5, txt = "Order Date:", border=0, ln = 0, align = 'L')
	pdf.cell(w = 95, h = 5, txt = "Tracking ID:", border=0, ln = 1, align = 'R')
	pdf.set_font('Arial', '', 12)
	order_date = ""
	tracking_id = ""
	if 'order_date' in data.keys():
		order_date = data['order_date']
	if 'tracking_id' in data.keys():
		tracking_id = data['tracking_id']
	pdf.cell(w = 95, h = 5, txt = order_date, border=0, ln = 0, align = 'L')
	pdf.cell(w = 95, h = 5, txt = tracking_id, border=0, ln = 1, align = 'R')
	
	pdf.cell(w = 95, h = 10, txt = "", border=0, ln = 0, align = 'L')
	pdf.cell(w = 95, h = 10, txt = "", border=0, ln = 1, align = 'R')
	
	if 'line_items' in data.keys():
		itemsToBeDilivered = [["PRODUCT", "DETAILS(opt)", "QTY"]]
		for item in data['line_items']:
			product = []
			for productDetails in item.values():
				product.append(str(productDetails))
			itemsToBeDilivered.append(product)
		for r in itemsToBeDilivered:
			for c in range(3):
				if c != 2:
					pdf.cell(w = (190.00 / 3), h = 10, txt = str(r[c]), border=1, ln = 0, align = 'L')
				else:
					pdf.cell(w = (190.00 / 3), h = 10, txt = str(r[c]), border=1, ln = 1, align = 'L')

	pdf.set_font('Arial', 'B', 16)

	pdf.cell(w = 95, h = 20, txt = "Invoice Value ", border=0, ln = 0, align = 'C')
	cost = 0
	if 'payment' in data.keys():
		if 'amount' in data['payment'].keys():
			cost = float(str(data['payment']['amount']))
	pdf.cell(w = 95, h = 20, txt = "INR " + str(cost), border=0, ln = 1, align = 'C')

	returnAddress = ""
	if 'return_address' in data.keys():
		for addr in data['return_address'].values():
			returnAddress += str(addr)
			returnAddress += " "
	pdf.set_font('Arial', 'B', 14)
	pdf.cell(w = 0,h = 15, txt="Return Address:", border=0, ln=1, align = 'C')
	pdf.set_font('Arial', '', 14)
	pdf.cell(w = 0,h = 15, txt=returnAddress, border=0, ln=1, align = 'C')	
	return pdf

if __name__ == "__main__":
    app.run(debug = True)