import re

s = "Balthar's blunts and blades"
print(s.find('\''))
num = s.find("\'")
print(num)
s = s.replace("'", "\\'")

print(s)