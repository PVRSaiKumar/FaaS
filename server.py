from flask import Flask, request
from flask import render_template 
import os, random, threading
import json
import subprocess

functions = 'Data/function.json'
triggers = 'Data/trigger.json'


CONT_PORT = 9000
HANDLER_PORT = 31001
SERVER_PORT = 31000
SERVICE_PORT = 29000

app = Flask(__name__)

@app.route('/user.html', methods=['GET'])
def html():
	return render_template("user.html")

@app.route("/register",methods=['POST'])
def reg():
	if request.form['reg_type']=="1":
		tarfile = request.files["file"]
		print("received",tarfile.filename)
		if(tarfile.filename[-4:]==".tgz" or tarfile.filename[-7:]==".tar.gz"):
			tarfile.save("images/"+tarfile.filename)
			os.system("rm Dockerfile")
			os.system(f'''echo "FROM ubuntu
			RUN apt-get update && apt-get install -y gcc libreadline6-dev zlib1g-dev bison flex less vim git make
			RUN apt-get install -y python3.11 python3-pip
			RUN pip install pipreqs
			RUN apt-get install -y curl
			RUN apt-get install -y libicu-dev pkg-config
			RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
			RUN chmod +x ./kubectl
			RUN mv ./kubectl /usr/local/bin
			EXPOSE {CONT_PORT}
			RUN adduser client
			USER client
			WORKDIR /home/client
			COPY cont_manager.py .
			" > Dockerfile''')
			os.system("tar -xvzf images/"+tarfile.filename+" -C images/")
			os.system("rm images/"+tarfile.filename)
			os.system("echo \"COPY "+"images/"+" .\" >> Dockerfile")
			os.system('''echo "ENV PATH=\$PATH:~/.local/bin
			RUN pipreqs --encoding=iso-8859-1 .
			RUN pip3 install -r requirements.txt" >> Dockerfile''')

			os.system("docker login -u pvrsaikumar -p 123456789")
			imageno = random.randint(0,10000)
			image = "pvrsaikumar/cs695:image"+str(imageno)
			command = request.form['Command1']
			arguments = request.form['Arguments1']
			print("$"+arguments+"$")
			
			while (os.system("docker pull "+image+" 2>/dev/null") ==0):
				os.system("docker rmi "+image)
				imageno = random.randint(0,10000)
				image = "pvrsaikumar/cs695:image"+str(imageno)
			os.system("docker build -t "+image+" .")
			os.system("rm -rf images")
			os.system("mkdir images")
			os.system("docker push "+image)
			os.system("docker rmi "+image)

			function_data = json.load(open(functions,'r'))
			function_data[image]=[command,arguments]
			trigger_data = json.load(open(triggers,'r'))
			trigger_data[image]=[]

			### DEPLOYING THE DEPLOYMENT FOR THAT IMAGE
			yaml_data = f'''apiVersion: apps/v1
kind: Deployment
metadata:
  name: image{imageno}-deployment
  labels:
    app: image{imageno}-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: image{imageno}-app
  template:
    metadata:
      labels:
        app: image{imageno}-app
    spec:
      containers:
      - name: image{imageno}-cont
        image: {image}
        command: {command}
        args: {arguments}
		ports:
        - containerPort: {CONT_PORT}
'''
			file = open("user_depl.yaml","w")
			file.write(yaml_data)
			file.close()
			os.system("kubectl --kubeconfig $PWD/config.yaml apply -f user_depl.yaml")

			os.system(f"""echo "kind: Service
apiVersion: v1
metadata:
 name: image{imageno}-service
spec:
 selector:
   app: image{imageno}-app
 ports:
 - name: cont_manager
   port: {SERVICE_PORT}
   targetPort: {CONT_PORT}" > service.yaml""")
			os.system("kubectl --kubeconfig $PWD/config.yaml apply -f service.yaml")

			IP = subprocess.check_output("kubectl --kubeconfig $PWD/config.yaml get services image"+imageno+"-service | awk 'FNR == 2 {print $3; exit}'",shell=True,text=True)
			function_data[image].append(IP.replace("\n",""))
			json.dump(function_data,open(functions,'w'))
			json.dump(trigger_data,open(triggers,'w'))

			return "received "+tarfile.filename+" stored as pvrsaikumar/"+image
		else:
			return "incorrect file type"
	elif request.form['reg_type']=="2":
		image = request.form['imagename']
		command = request.form['Command2']
		arguments = request.form['Arguments2']

		if(os.system("docker pull "+image+" 2>/dev/null")>0):
			print("can't pull the image "+image+" :(")
			return "can't pull the given image "+image

		imageno = None
		myimage = None
		if(image[:18]!="pvrsaikumar/cs695:"):
			os.system("docker login -u pvrsaikumar -p 123456789")
			imageno = random.randint(0,10000)
			myimage = "pvrsaikumar/cs695:image"+str(imageno)
			
			while (os.system("docker pull "+myimage+" 2>/dev/null") ==0):
				os.system("docker rmi "+myimage)
				imageno = random.randint(0,10000)
				myimage = "pvrsaikumar/cs695:image"+str(imageno)

			os.system(f'''echo "FROM {image}
			EXPOSE {CONT_PORT}
			COPY cont_manager.py .
			" > Dockerfile''')
			os.system('''echo "ENV PATH=\$PATH:~/.local/bin
			RUN pipreqs --encoding=iso-8859-1 .
			RUN pip3 install -r requirements.txt" >> Dockerfile''')

			os.system("docker build -t "+myimage+" .")
			os.system("docker login -u pvrsaikumar -p 123456789")
			os.system("docker push "+myimage)
			os.system("docker rmi "+image)
			os.system("docker rmi "+myimage)
		else:
			imageno = image[23:]
		function_data = json.load(open(functions,'r'))
		function_data[image]=[command,arguments]
		trigger_data = json.load(open(triggers,'r'))
		trigger_data[image]=[]

		### DEPLOYING THE DEPLOYMENT FOR THAT IMAGE
		yaml_data = f'''apiVersion: apps/v1
kind: Deployment
metadata:
  name: image{imageno}-deployment
  labels:
    app: image{imageno}-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: image{imageno}-app
  template:
    metadata:
      labels:
        app: image{imageno}-app
    spec:
      containers:
      - name: image{imageno}-cont
        image: {myimage}
        command: {command}
        args: {arguments}
		ports:
        - containerPort: {CONT_PORT}
'''
		file = open("user_depl.yaml","w")
		file.write(yaml_data)
		file.close()
		os.system("kubectl --kubeconfig $PWD/config.yaml apply -f user_depl.yaml")

		os.system(f"""echo "kind: Service
apiVersion: v1
metadata:
 name: image{imageno}-service
spec:
 selector:
   app: image{imageno}-app
 ports:
 - name: cont_manager
   port: {SERVICE_PORT}
   targetPort: {CONT_PORT}" > service.yaml""")
		os.system("kubectl --kubeconfig $PWD/config.yaml apply -f service.yaml")

		IP = subprocess.check_output("kubectl --kubeconfig $PWD/config.yaml get services image"+imageno+"-service | awk 'FNR == 2 {print $3; exit}'",shell=True,text=True)
		function_data[image].append(IP.replace("\n",""))
		json.dump(function_data,open(functions,'w'))
		json.dump(trigger_data,open(triggers,'w'))
		
		return "image "+myimage+" deployed successfully"
	elif request.form['reg_type']=="3":
		url = request.form['url']
		type = request.form['trigger']
		image = request.form['image']
		command = request.form['command3']
		returnfiles = request.form['return']

		function_data = json.load(open(functions,'r'))
		if image in function_data.keys():
			trigger_data = json.load(open(triggers,'r'))
			trigger_data[image].append([url,type,command,returnfiles])
			json.dump(trigger_data,open(triggers,'w'))
			return "trigger registration successful"
		else:
			return "Image is not registered"

if __name__ == '__main__':
	if (0<os.system("ls Data")):
		print("Internal error, Data folder is not there")
		os.system("mkdir Data")
	if (0<os.system("ls Data/function.json")):
		os.system("touch Data/function.json")
		os.system("touch Data/trigger.json")
		os.system("echo \"{}\"> Data/function.json")
		os.system("echo \"{}\"> Data/trigger.json")
	app.run(debug=True,host='0.0.0.0', port=SERVER_PORT)

	