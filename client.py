import requests
myobj = {'somekey': 'somevalue'}
file={"myfile":open("Example_codes/Dockerfile","r"),"myfile2":open("Dind_Dockerfile","r")}
r=requests.get("http://{IP_Kubernetes}:31001/trigger_url",params=myobj,files=file)
r=requests.post("http://{IP_Kubernetes}:31001/trigger_url",data=myobj,files=file)
with open('downloaded_file_client.zip', 'wb') as f:  # Adjust filename and mode as needed
    f.write(r.content)
    print('File downloaded successfully.')