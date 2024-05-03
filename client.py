import requests
IP_kubernetes = "10.129.2.183"
myobj = {'somekey': 'somevalue'}
file={"myfile":open("Example_codes/Dockerfile","r"),"myfile2":open("Dind_Dockerfile","r")}
r=requests.get(f"http://{IP_kubernetes}:31001/trigger_url",params=myobj,files=file)
r=requests.post(f"http://{IP_kubernetes}:31001/trigger_url",data=myobj,files=file)
with open('downloaded_file_client.zip', 'wb') as f:  # Adjust filename and mode as needed
    f.write(r.content)
    print('File downloaded successfully.')