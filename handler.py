from flask import Flask, request
from flask import render_template 
import os, random, threading
import json

functions = 'Data/function.json'
triggers = 'Data/trigger.json'

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['GET','POST'])
@app.route('/<path:path>', methods=['GET','POST'])
def catch_all(path):
	function_data = json.load(open(functions,'r'))
	trigger_data = json.load(open(triggers,'r'))
	for fn_name in trigger_data.keys():
		for triggers in trigger_data[fn_name]:
			if triggers[0] == path and triggers[1] == request.method:
				#call the container with the arguments
	return "icd"

if __name__ == '__main__':
	if (0<os.system("ls Data")):
		print("Internal error, Data folder is not there")
	if (0<os.system("ls Data/function.json")):
		os.system("touch Data/function.json")
		os.system("touch Data/trigger.json")
		os.system("echo \"{}\"> Data/function.json")
		os.system("echo \"{}\"> Data/trigger.json")
	app.run(debug=True, port=32000)

# have to check if image already has commands or u have to provide at the container.yaml