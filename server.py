from flask import Flask, request
from flask import render_template 
import os, random, threading
import json

functions = 'Data/function.json'
triggers = 'Data/trigger.json'

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
			os.system('''echo "FROM ubuntu
			RUN apt-get update && apt-get install -y gcc libreadline6-dev zlib1g-dev bison flex less vim git make
			RUN apt-get install -y python3.11 python3-pip
			RUN pip install pipreqs
			RUN apt-get install -y curl
			RUN apt-get install -y libicu-dev pkg-config
			RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
			RUN chmod +x ./kubectl
			RUN mv ./kubectl /usr/local/bin
			RUN adduser client
			USER client
			WORKDIR /home/client" > Dockerfile''')
			os.system("tar -xvzf images/"+tarfile.filename+" -C images/")
			os.system("rm images/"+tarfile.filename)
			os.system("echo \"COPY "+"images/"+" .\" >> Dockerfile")
			os.system('''echo "ENV PATH=\$PATH:~/.local/bin
			RUN pipreqs --encoding=iso-8859-1 .
			RUN pip3 install -r requirements.txt" >> Dockerfile''')

			os.system("docker login -u pvrsaikumar -p 123456789")
			imageno = random.randint(0,10000)
			image = "pvrsaikumar/cs695:image"+str(imageno)
			command = request.form['Command']### HAVE TO SEE WHEN TO USE IT
			
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
			function_data[image]=command
			trigger_data = json.load(open(triggers,'r'))
			trigger_data[image]=[]
			json.dump(function_data,open(functions,'w'))
			json.dump(trigger_data,open(triggers,'w'))

			### DEPLOYING THE DEPLOYMENT FOR THAT IMAGE
			os.system("cp user_depl.yaml user_depl2.yaml")
			os.system("sed -i 's/<IMAGE>/image"+imageno+"/' user_depl2.yaml")
			os.system("kubectl apply -f user_depl2.yaml")

			return "received "+tarfile.filename+" stored as pvrsaikumar/"+image
		else:
			return "incorrect file type"
	elif request.form['reg_type']=="2":
		image = request.form['imagename']
		command = request.form['Command']### HAVE TO SEE WHEN TO USE IT
		if(os.system("docker pull "+image+" 2>/dev/null")>0):
			print("can't pull the image "+image+" :(")
			return "can't pull the given image "+image

		imageno = None
		if(image[:18]!="pvrsaikumar/cs695:"):
			os.system("docker login -u pvrsaikumar -p 123456789")
			imageno = random.randint(0,10000)
			myimage = "pvrsaikumar/cs695:image"+str(imageno)
			
			while (os.system("docker pull "+myimage+" 2>/dev/null") ==0):
				os.system("docker rmi "+myimage)
				imageno = random.randint(0,10000)
				myimage = "pvrsaikumar/cs695:image"+str(imageno)

			os.system("docker tag "+image+" "+myimage)
			os.system("docker push "+myimage)
			os.system("docker rmi "+image)
			os.system("docker rmi "+myimage)
		else:
			print("$1")
			imageno = image[18:]
		function_data = json.load(open(functions,'r'))
		function_data[image]=command
		trigger_data = json.load(open(triggers,'r'))
		trigger_data[image]=[]
		json.dump(function_data,open(functions,'w'))
		json.dump(trigger_data,open(triggers,'w'))


		### DEPLOYING THE DEPLOYMENT FOR THAT IMAGE
		print("came here")
		os.system("cp user_depl.yaml user_depl2.yaml")
		os.system("sed -i 's/<IMAGE>/"+imageno+"/' user_depl2.yaml")
		os.system("kubectl apply -f user_depl2.yaml")
		# os.system("rm user_depl2.yaml")
		
		return "image "+image+" received successfully"
	
	elif request.form['reg_type']=="3":
		url = request.form['url']
		type = request.form['trigger']
		image = request.form['image']

		function_data = json.load(open(functions,'r'))
		if image in function_data.keys():
			trigger_data = json.load(open(triggers,'r'))
			trigger_data[image].append([url,type])
			json.dump(trigger_data,open(triggers,'w'))
			return "trigger registration successful, please use port 32000 for triggers instead of 31000 for user interface"
		else:
			return "Image is not registered"
	
if __name__ == '__main__':
	if (0<os.system("ls Data")):
		print("Internal error, Data folder is not there")
	if (0<os.system("ls Data/function.json")):
		os.system("touch Data/function.json")
		os.system("touch Data/trigger.json")
		os.system("echo \"{}\"> Data/function.json")
		os.system("echo \"{}\"> Data/trigger.json")
	app.run(debug=True, port=31000)

	