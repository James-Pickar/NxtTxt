import requests

headers = {
    'Content-type': 'text/plain',
    'Accept': 'application/xml',
}

data = open('/Users/jamiepickar/Downloads/pdfs/Allianz.txt', 'rb').read()
response = requests.post('http://ec2-35-174-241-30.compute-1.amazonaws.com:8080/api/v1/articles/analyzeText', headers=headers, data=data)

print(response.content)
