from bs4 import BeautifulSoup as bs
import re
import pandas
import math
import numpy as np
from collections import Counter #for counting number of values in a list
import re



soup = bs(open("message (440).html"), "html.parser")
tds = soup.find_all(text=True)

#get names list
names = Counter(x for x in tds).most_common(2)
names_list = [names[0][0], names[1][0]]


#first I need to replace values with actual
emo_replaces_dict = {
'Riju':'Rija',
'\u2019':"'",
'\U0001f600':'~grinning face~',
'\U0001f603':'~grinning face with big eyes~',
'\U0001f604':'~grinning face with smiling eyes~',
'\U0001f601':'~beaming face with smiling eyes~',
'\U0001f606':'~grinning squinting face~',
'\U0001f605':'~grinning face with sweat~',
'\U0001f923':'~rolling on the floor laughing~',
'\U0001f602':'~face with tears of joy~',
'\U0001f642':'~slightly smiling face~',
'\U0001f643':'~upside-down face~',
'\U0001f609':'~winking face~',
'\U0001f60a':'~smiling face with smiling eyes~',
'\U0001f607':'~smiling face with halo~',
'\U0001f60d':'~smiling face with heart-eyes~',
'\U0001f929':'~star-struck~'
}



#remove all emos and '
tds1 = [x.encode('ascii', 'ignore').decode('ascii') for x in tds]





#experiment
tds1 = tds
tds1 = tds1[5:50]


for key,value in emo_replaces_dict.iteritems():
    print "Replacing " + key + " with " + value
    tds2 = [x.replace('\u2019',"'",) for x in tds1]
    
tds2[10]




# tds_1 = [tds[i] for i in range(0, len(tds), 3)]
# tds_2 = [tds[i] for i in range(1, len(tds), 3)]
# tds_3 = [tds[i] for i in range(2, len(tds), 3)]

pandas.DataFrame(tds_sublists [1:], columns=tds_sublists [0])
    

#using regular expression
r = re.compile("")



size = math.ceil(len(tds)/3)


df = pandas.DataFrame(np.array(tds).reshape(3,100), columns = list("abc"))

extracteddf = pandas.DataFrame({'1':[], '2':[], '3':[]})







df = pandas.DataFrame({"col1": list(tds2)})
df.to_csv("./file.csv", sep=',',index=False)




for values in tds:
    
    
    






month_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

tds = [x for x in tds if x not in remove_list]
for month in month_list:
    tds = [x for x in tds if month not in x]


