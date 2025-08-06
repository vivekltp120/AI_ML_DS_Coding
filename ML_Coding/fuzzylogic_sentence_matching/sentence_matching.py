from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from fuzzywuzzy import string_processing
a='my india'
b=['Cirque du Soleil-Zarkana','this is my india','I love my india']
print(fuzz.QRatio(a,b))
print(process.extractOne(a,b,scorer=fuzz.ratio))