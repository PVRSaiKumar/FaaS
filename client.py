import requests
myobj = {'somekey': 'somevalue'}
file={"myfile":open("Example_codes/Dockerfile","r"),"myfile2":open("Dind_Dockerfile","r")}
# r=requests.get("http://localhost:8000/idkyaar",params=myobj,files=file)
r=requests.post("http://localhost:8000/idkyaar2",data=myobj,files=file)
with open('downloaded_file_client.zip', 'wb') as f:  # Adjust filename and mode as needed
    f.write(r.content)
    print('File downloaded successfully.')