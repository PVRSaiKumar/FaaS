import requests
IP_kubernetes = "192.168.49.2"
# myobj = {'somekey': 'somevalue'}
file={"myfile":open("actual.png","rb")}#,"myfile2":open("Dind_Dockerfile","r")}
# r=requests.get(f"http://{IP_kubernetes}:32001/trigger_url",params=myobj,files=file)
# r=requests.post(f"http://{IP_kubernetes}:32001/invert",data=myobj,files=file)
r=requests.post(f"http://{IP_kubernetes}:32001/invert",files=file)
with open('downloaded_file_client.zip', 'wb') as f:  # Adjust filename and mode as needed
    f.write(r.content)
    print('File downloaded successfully.')