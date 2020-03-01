from pythonping import ping

x=range(1)
for a in range(1):
    print(a)

response_list = ping('128.0.0.2', size=40, count=4)
print(response_list)