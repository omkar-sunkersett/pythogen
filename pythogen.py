import ast
import bibtexparser
import email
import fpdf
import json
import requests
import scholarly
import smtplib
import time


class GScholar():
	def __init__(self, user_query, n_records):
		self.user_query = user_query
		self.search_handle = scholarly.search_pubs_query(self.user_query)
		self.gscholar_resultset = []
		self.count_resultset = 0
		self.retrieval = ""
		self.retrieval_no = 0
		self.n_records = n_records

	def retrieve_resultset(self):
		while True:
			print "\nSearching for retrieval " + str(self.count_resultset + 1) + " ... "
			record = next(self.search_handle)
			record = str(record)
			self.retrieval = ast.literal_eval(record)
			citation = self.retrieve_citation(self.retrieval)
			self.retrieval.update(citation)
			self.gscholar_resultset.append(self.retrieval)
			self.count_resultset = self.count_resultset + 1
			if self.count_resultset % self.n_records == 0:
				break

	def retrieve_citation(self, retrieval):
		url = retrieval['url_scholarbib']
		try:
			response = requests.get(url)
			bibtex = response.text
			citation = bibtexparser.loads(bibtex).entries[0]
			return citation
		except:
			return { 'ENTRYTYPE': "Access denied", 'journal': "Access denied", 'volume': "Access denied", 'number': "Access denied", 'pages': "Access denied", 'year': "Access denied", 'publisher': "Access denied"}

	def __str__(self):
		print "\nRetrieval " + str(self.retrieval_no + 1) +":"

		if 'title' not in self.gscholar_resultset[self.retrieval_no]['bib'].keys():
			self.gscholar_resultset[self.retrieval_no]['bib']['title'] = "Not available"
		print "Title: " + self.gscholar_resultset[self.retrieval_no]['bib']['title']

		if 'abstract' not in self.gscholar_resultset[self.retrieval_no]['bib'].keys():
			self.gscholar_resultset[self.retrieval_no]['bib']['abstract'] = "Not available"
		print "Abstract:\n" + self.gscholar_resultset[self.retrieval_no]['bib']['abstract']

		if 'author' not in self.gscholar_resultset[self.retrieval_no]['bib'].keys():
			self.gscholar_resultset[self.retrieval_no]['bib']['author'] = "Not available"
		print "Author: " + self.gscholar_resultset[self.retrieval_no]['bib']['author']

		if 'url' not in self.gscholar_resultset[self.retrieval_no]['bib'].keys():
			self.gscholar_resultset[self.retrieval_no]['bib']['url'] = "Not available"
		print "Web URL: " + self.gscholar_resultset[self.retrieval_no]['bib']['url']

		if 'eprint' not in self.gscholar_resultset[self.retrieval_no]['bib'].keys():
			self.gscholar_resultset[self.retrieval_no]['bib']['eprint'] = "Not available"
		print "E-Print: " + self.gscholar_resultset[self.retrieval_no]['bib']['eprint']

		if 'id_scholarcitedby' not in self.gscholar_resultset[self.retrieval_no].keys():
			self.gscholar_resultset[self.retrieval_no]['id_scholarcitedby'] = "Not available"
		print "Clustered Results: " + "https://scholar.google.com/scholar?cluster=" + str(self.gscholar_resultset[self.retrieval_no]['id_scholarcitedby'])

		if 'ENTRYTYPE' not in self.gscholar_resultset[self.retrieval_no].keys():
			self.gscholar_resultset[self.retrieval_no]['ENTRYTYPE'] = "Not available"
		print "Entry Type: " + self.gscholar_resultset[self.retrieval_no]['ENTRYTYPE'].capitalize()

		if 'journal' not in self.gscholar_resultset[self.retrieval_no].keys():
			self.gscholar_resultset[self.retrieval_no]['journal'] = "Not available"
		print "Journal: " + self.gscholar_resultset[self.retrieval_no]['journal']

		if 'volume' not in self.gscholar_resultset[self.retrieval_no].keys():
			self.gscholar_resultset[self.retrieval_no]['volume'] = "Not available"
		print "Volume: " + self.gscholar_resultset[self.retrieval_no]['volume']

		if 'number' not in self.gscholar_resultset[self.retrieval_no].keys():
			self.gscholar_resultset[self.retrieval_no]['number'] = "Not available"
		print "Number: " + self.gscholar_resultset[self.retrieval_no]['number']

		if 'pages' not in self.gscholar_resultset[self.retrieval_no].keys():
			self.gscholar_resultset[self.retrieval_no]['pages'] = "Not available"
		print "Pages: " + self.gscholar_resultset[self.retrieval_no]['pages']

		if 'year' not in self.gscholar_resultset[self.retrieval_no].keys():
			self.gscholar_resultset[self.retrieval_no]['year'] = "Not available"
		print "Year: " + self.gscholar_resultset[self.retrieval_no]['year']

		if 'publisher' not in self.gscholar_resultset[self.retrieval_no].keys():
			self.gscholar_resultset[self.retrieval_no]['publisher'] = "Not available"
		print "Publisher: " + self.gscholar_resultset[self.retrieval_no]['publisher']

		if 'citedby' not in self.gscholar_resultset[self.retrieval_no].keys():
			self.gscholar_resultset[self.retrieval_no]['citedby'] = "Not available"
		print "Cited By: " + str(self.gscholar_resultset[self.retrieval_no]['citedby'])

		self.retrieval_no = self.retrieval_no + 1
		return "\n"


class Report(fpdf.FPDF, GScholar):
	def __init__(self, user_query, n_records):
		GScholar.__init__(self, user_query, n_records)
		self.final_selection = []
		self.pdf = fpdf.FPDF('P', 'mm', 'Letter')
		self.pdf.set_margins(25.4, 25.4, 25.4)
		self.pdf.alias_nb_pages()
		self.pdf.add_page()

	def __str__(self):
		return GScholar.__str__(self)

	def title_page(self):
		self.heading = "PythoGen v1.0"
		self.pdf.ln(65) # 139.7
		self.pdf.image("gs_logo.png", x = 55, link = "https://scholar.google.com")
		self.pdf.set_font('Times', 'B', 16)
		self.pdf.multi_cell(0, 16, self.heading, align = 'C')
		self.pdf.set_font('Times', 'B', 14)
		self.pdf.multi_cell(0, 14, "Date: " + time.strftime("%m/%d/%Y  %H:%M:%S"), align = 'C')

	def outline_page(self):
		self.read_cache()
		self.pdf.add_page()
		self.pdf.set_font('Times', 'B', 12)
		self.pdf.multi_cell(0, 12, "Contents: ", align = 'L')
		self.pdf.set_font('Times', size = 12)
		self.pdf.multi_cell(0, 12, "I. Online Search Query")
		self.pdf.multi_cell(0, 12, "II. Number of Selected Retrievals")
		self.pdf.multi_cell(0, 12, "III. List of Selected Retrievals")
		self.pdf.multi_cell(0, 12, "IV. Bibliography (APA 6th Ed.)")
		self.pdf.ln(10)
		self.pdf.ln(10)
		self.pdf.set_font('Times', 'B', 12)
		self.pdf.multi_cell(0, 12, "Online Search Query: ", align = 'L')
		self.pdf.set_font('Times', size = 12)
		self.pdf.multi_cell(0, 12, '"' + self.user_query + '"', align = 'L')
		self.pdf.ln(10)
		self.pdf.set_font('Times', 'B', 12)
		self.pdf.multi_cell(0, 12, "Number of selected retrievals: " + str(len(self.final_selection)), align = 'L')

	def read_cache(self):
		try:
			cache_handle = open("result-cache.txt", 'r')
			for selection in cache_handle:
				selection = json.loads(selection)
				self.final_selection.append(selection)
			cache_handle.close()
		except Exception, e:
			print "Error while reading cached retrievals!"
			print str(e)

	def contents_page(self):
		self.pdf.set_font('Times', size = 12)
		retrieval_count = 0
		for surrogate in self.final_selection:
			self.pdf.add_page()
			retrieval_count += 1
			self.pdf.multi_cell(0, 10, "Retrieval " + str(retrieval_count).encode('utf-8') + " of " + str(len(self.final_selection)).encode('utf-8'), align = 'L')
			self.pdf.set_font('Times', 'B', size = 12)
			self.pdf.multi_cell(0, 10, "Title: " + surrogate['bib']['title'].encode('utf-8'), align = 'L')
			self.pdf.multi_cell(0, 10, "Abstract: \n" + surrogate['bib']['abstract'].encode('utf-8'), border = 1, align = 'L')
			self.pdf.set_font('Times', size = 12)
			self.pdf.multi_cell(0, 10, "Author: " + surrogate['bib']['author'].encode('utf-8'), align = 'L')
			self.pdf.multi_cell(0, 10, "Web URL: " + surrogate['bib']['url'].encode('utf-8'), align = 'L')
			self.pdf.multi_cell(0, 10, "E-Print: " + surrogate['bib']['eprint'].encode('utf-8'), align = 'L')
			self.pdf.multi_cell(0, 10, "Clustered Results: " + "https://scholar.google.com/scholar?cluster=" + str(surrogate['id_scholarcitedby']).encode('utf-8'), align = 'L')
			self.pdf.multi_cell(0, 10, "Entry Type: " + surrogate['ENTRYTYPE'].encode('utf-8').capitalize(), align = 'L')
			self.pdf.multi_cell(0, 10, "Journal: " + surrogate['journal'].encode('utf-8'), align = 'L')
			self.pdf.multi_cell(0, 10, "Volume: " + surrogate['volume'].encode('utf-8'), align = 'L')
			self.pdf.multi_cell(0, 10, "Number: " + surrogate['number'].encode('utf-8'), align = 'L')
			self.pdf.multi_cell(0, 10, "Pages: " + surrogate['pages'].encode('utf-8'), align = 'L')
			self.pdf.multi_cell(0, 10, "Year: " + surrogate['year'].encode('utf-8'), align = 'L')
			self.pdf.multi_cell(0, 10, "Publisher: " + surrogate['publisher'].encode('utf-8'), align = 'L')
			self.pdf.multi_cell(0, 10, "Cited By: " + str(surrogate['citedby']).encode('utf-8'), align = 'L')

	def bibliography_page(self):
		self.pdf.add_page()
		self.pdf.set_font('Times', 'BU', 12)
		self.pdf.multi_cell(0, 12, "Bibliography", align = 'C')
		self.pdf.set_font('Times', size = 10)
		self.pdf.multi_cell(0, 10, "Citation Style: American Psychological Association (APA), 6th Edition", align = 'C')
		self.pdf.set_font('Times', size = 12)
		retrieval_count = 0
		for surrogate in self.final_selection:
			retrieval_count += 1
			try:
				author = ", ".join(map(lambda x : str(x[1]) + " " + str(x[0]) + ".", map(lambda x : x.split(), map(lambda x : x.strip(), surrogate['bib']['author'].encode('utf-8').split('and')))))
			except Exception, e:
				author = "Unknown."
			year = surrogate['year'].encode('utf-8')
			entry_title = surrogate['bib']['title'].encode('utf-8')
			periodical = surrogate['journal'].encode('utf-8')
			volume = surrogate['volume'].encode('utf-8')
			issue = surrogate['number'].encode('utf-8')
			pp_pp = surrogate['pages'].encode('utf-8')
			url = surrogate['bib']['url'].encode('utf-8')
			if surrogate['ENTRYTYPE'].encode('utf-8').lower() == 'article':
				self.pdf.multi_cell(0, 10, "(" + str(retrieval_count) + ") " + author + " (" + year + "). " + entry_title + ". " + periodical + ", " + volume + "(" + issue + "), " + pp_pp + ". Retrieved from journal " + url, align = 'L')
			else:
				self.pdf.multi_cell(0, 10, "(" + str(retrieval_count) + ") " + author + " (" + year + "). " + entry_title + ". Retrieved from " + url, align = 'L')

	def generate(self):
		self.title_page()
		self.outline_page()
		self.contents_page()
		self.bibliography_page()
		self.pdf.output("PythogenReport_" + time.strftime("%m%d%Y") + ".pdf", 'F')

class PrepareEmail():
	def __init__(self, name, toaddr):
		self.fromaddr = "sunkersetto.sa@gmail.com"
		self.toaddr = toaddr
		self.msg = email.MIMEMultipart.MIMEMultipart()
		self.msg['From'] = self.fromaddr
		self.msg['To'] = self.toaddr
		self.msg['Subject'] = "Google Scholar Search Selection Report (Powered by PythoGen)"
		self.body = "Hello " + name + ":\n\n" + "Kindly find the attached PDF of the Search Selection Report from Google Scholar.\n\n\n" + "Regards,\nPythoGen for Google Scholar\n\n"
		self.msg.attach(email.MIMEText.MIMEText(self.body, 'plain'))

	def attach_file(self):
		try:
			self.filename = "PythogenReport_" + time.strftime("%m%d%Y") + ".pdf"
			self.attachment = open(self.filename, "rb")
			self.part = email.MIMEBase.MIMEBase('application', 'octet-stream')
			self.part.set_payload((self.attachment).read())
			email.encoders.encode_base64(self.part)
			self.part.add_header('Content-Disposition', "attachment; filename= %s" % self.filename)
			self.msg.attach(self.part)
		except Exception, e:
			print "File I/O error while trying to send email!"
			print str(e)

	def send_message(self):
		try:
			self.server = smtplib.SMTP('smtp.gmail.com', 587)
			self.server.starttls()
			self.server.login(self.fromaddr, "SI665_srt")
			self.text = self.msg.as_string()
			self.server.sendmail(self.fromaddr, self.toaddr, self.text)
			self.server.quit()
			print "\nThe report has been sent successfully to " + self.toaddr + "\n"
		except Exception, e:
			print "Network error while trying to send email!"
			print str(e)

	def execute(self):
		self.attach_file()
		self.send_message()


def main():
	welcome_msg = "\n=========================================\n---------- WELCOME TO PYTHOGEN ----------\n=========================================\n"
	print welcome_msg

	user_query = ""
	while user_query.strip() == "":
		user_query = raw_input("Enter a search topic: ")

	n_records = 0	
	while n_records < 1:
		try:
			n_records = int(raw_input("\nEnter the number of retrievals to fetch per request (>=1): "))
		except:
			print "\nInvalid input!\nNumber of retrievals should be an integer..."

	print "\nYou have requested to search Google Scholar on the topic:\n" + user_query
	try:
		gs = Report(user_query, n_records)
		gs.retrieve_resultset()
		file_handle = open('result-cache.txt','w')
		while True:
			print gs
			key = raw_input("Press 'enter' to skip this source ('s' to select, 'q' to quit): ")
			if key.lower() == 'q':
				break
			elif key.lower() == 's':
				file_handle.write(json.dumps(gs.gscholar_resultset[gs.retrieval_no-1]) + "\n")
				print "\nThe above retrieval has been included in your selection.\n"
			if gs.retrieval_no % n_records == 0:
				gs.retrieve_resultset()
		file_handle.close()

		print "\nGenerating the PDF report ... "
		gs.generate()
		print "\nThe report has been generated successfully."

		name = raw_input("\nPlease enter the name of the recipient: ")
		em = ''
		while '@' not in em:
			em = raw_input("\nPlease enter the email address of the recipient: ")
		pe = PrepareEmail(name, em)
		print "\nSending the report to " + em + " ... "
		pe.execute()

	except Exception, e:
		print "Google Scholar has denied you access to its resources. Please try again later!"
		print str(e)

main()







