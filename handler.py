from flask import Flask, request, make_response, send_from_directory
from flask import render_template 
import os, random, threading
import json
import requests

functions = 'Data/function.json'
triggers = 'Data/trigger.json'
CONT_PORT = 9000
HANDLER_PORT = 31001
SERVER_PORT = 31000
app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['GET','POST'])
@app.route('/<path:path>', methods=['GET','POST'])
def catch_all(path):
	trigger_data = json.load(open(triggers,'r'))
	function_data = json.load(open(functions,'r'))
	for fn_name in trigger_data.keys():
		for triggers in trigger_data[fn_name]:
			if triggers[0] == path and triggers[1] == request.method:
				if request.method=="GET":
					r=requests.post(f"http://{function_data[fn_name][2]}:{CONT_PORT}/",data={"ARGS":json.dumps(request.args),"COMMAND":triggers[2],"RETURN":triggers[3]},files=request.files)

					zip_filename = 'downloaded_file.zip'
					with open(zip_filename, 'wb') as f:
						f.write(r.content)

					response = make_response(send_from_directory('', zip_filename, as_attachment=True))
					response.headers['Content-Type'] = 'application/zip'
					return response

				elif request.method=="POST":
					r=requests.post(f"http://{function_data[fn_name][2]}:{CONT_PORT}/",data={"ARGS":json.dumps(request.form),"COMMAND":triggers[2],"RETURN":triggers[3]},files=request.files)

					zip_filename = 'downloaded_file.zip'
					with open(zip_filename, 'wb') as f:
						f.write(r.content)

					response = make_response(send_from_directory('', zip_filename, as_attachment=True))
					response.headers['Content-Type'] = 'application/zip'
					return response

if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0',port=HANDLER_PORT)