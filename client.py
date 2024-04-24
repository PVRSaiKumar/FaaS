import requests
myobj = {'somekey': 'somevalue'}
r=requests.post("http://localhost:32000/idkyaar",json=myobj)
print(r.reason)
print(r.status_code)
print(r.text)