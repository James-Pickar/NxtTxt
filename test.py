import requests
try:
    response = requests.get('http://ec2-35-174-241-30.compute-1.amazonaws.com:8080/management/health')
except requests.exceptions.ConnectionError:
    print("Connection failed")
except requests.exceptions.Timeout:
    print("Connection Timeout")
except requests.exceptions.TooManyRedirects:
    print("Too Many Redirects")
except requests.exceptions.RequestException:
    print("Other Exception")
else:
    print("success")
