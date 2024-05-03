from flask import Flask, request, make_response, send_from_directory
import os
from werkzeug.utils import secure_filename
import zipfile

CONT_PORT = 9000
app = Flask(__name__)


@app.route('/', defaults={'path': ''}, methods=['GET','POST'])
@app.route('/<path:path>', methods=['POST'])
def catch_all(path):
	received_args = eval(dict(request.form)['ARGS'])
	command = dict(request.form)['COMMAND']
	returnfiles = [i.replace(" ", "").replace("\t", "") for i in dict(request.form)['RETURN'].split(",")]
	received_files = []
	
	for file in request.files:
		fobj = request.files[file]
		fobj.save(secure_filename(fobj.filename))
		received_files.append(secure_filename(fobj.filename))

	exec_command = command+" "+str(len(received_args))
	for i in received_args.keys():
		exec_command+=" "+received_args[i]
	exec_command = exec_command+" "+str(len(received_files))
	for i in received_files:
		exec_command+=" "+i
	
	os.system(exec_command)#+" > output")
	
	zip_filename = 'multiple_files.zip'

	with zipfile.ZipFile(zip_filename, 'w') as zip_file:
		for filename in returnfiles:
			zip_file.write(filename)

	response = make_response(send_from_directory('', zip_filename, as_attachment=True))
	response.headers['Content-Type'] = 'application/zip'
	return response


if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0',port=CONT_PORT)