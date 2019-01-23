from bs4 import BeautifulSoup as bs
import re
import pandas
import math
import numpy as np
from collections import Counter #for counting number of values in a list
from datetime import datetime #converting the datetime

time_format = '%b %d, %Y, %I:%M %p'
oct1 = datetime.strptime('Oct 1, 2018, 12:00 AM', time_format)


soup = bs(open("message (440).html"), "html.parser")
tds = soup.find_all(text=True)

#get names list
names = Counter(x for x in tds).most_common(2)
names_list = [names[0][0], names[1][0]]


#first I need to replace values with actual
# numb_to_emo_dict = {
# '~1~':'~grinning face~',
# '~2~':'~grinning face with big eyes~',
# '~3~':'~grinning face with smiling eyes~',
# '~4~':'~beaming face with smiling eyes~',
# '~5~':'~grinning squinting face~',
# '~6~':'~grinning face with sweat~',
# '~7~':'~rolling on the floor laughing~',
# '~8~':'~face with tears of joy~',
# '~9~':'~slightly smiling face~',
# '~10~':'~upside-down face~',
# '~11~':'~winking face~',
# '~12~':'~smiling face with smiling eyes~',
# '~13~':'~smiling face with halo~',
# '~14~':'~smiling face with heart-eyes~',
# '~15~':'~star-struck~'
# }

emo_replaces_numb_dict = {
u'\u2019':"'",
u'\U0001f600':'~1~',
u'\U0001f603':'~2~',
u'\U0001f604':'~3~',
u'\U0001f601':'~4~',
u'\U0001f606':'~5~',
u'\U0001f605':'~6~',
u'\U0001f923':'~7~',
u'\U0001f602':'~8~',
u'\U0001f642':'~9~',
u'\U0001f643':'~10~',
u'\U0001f609':'~11~',
u'\U0001f60a':'~12~',
u'\U0001f607':'~13~',
u'\U0001f60d':'~14~',
u'\U0001f929':'~15~',
u'\U0001f44d':'~16~',
u'\U0001f937':'~17~',
u'\U0001f3fd':'~18~',
u'\u200d\u2640\ufe0f':'~19~',
u'\U0001f914':'~20~',
}


#game_to_remove
game_contents_res = [ "[A-z]* played back, now it is your turn!", "[A-z] has started a game with you. It's your turn", "[A-z]* has invited you to play [A-z]* with them", "[A-z]* sent an attachment."]
geme_contents_re = [re.compile(x) for x in game_contents_res]

#experiment
tds1 = tds


r_date = re.compile("[A-z]+\s+\d+,\s+\d+,\s+\d:\d+\s+[A-z]+")

r_liked = re.compile("~[0-9][0-9]~"+names_list[0]+"|~[0-9][0-9]~"+names_list[1])

df = pandas.DataFrame({"instant":[], "name":[], "content":[], "time":[]})
tds2 = list(reversed(tds1[7:-1]))

for key,value in emo_replaces_numb_dict.iteritems():
    tds2 = [x.replace(key,value) for x in tds2]

for value in tds2:
    if value in names_list:
        name = value
        df = df.append({'instant':date, 'name':name, "content":content}, ignore_index=True) 
    elif re.match(r_date, value) is not None:
        date = value   
    elif re.match(r_liked, value) is not None:
        pass
    elif re.match(geme_contents_re[0], value) is not None: #removing game invites and blah blah
        content = ""
    elif re.match(geme_contents_re[1], value) is not None:
        content = ""
    elif re.match(geme_contents_re[2], value) is not None:
        content = ""
    elif re.match(geme_contents_re[3], value) is not None:
        content = ""
    else:
        content = value
        
        
#remove remaining all emos and '
#time conversion
df['time'] = ""
def string_to_secs(x):
    return (datetime.strptime(x, time_format)-oct1).total_seconds()

def ignore_unknown_emos(x):
    return x.encode('ascii', 'ignore').decode('ascii')

df['time'] = df['instant'].apply(string_to_secs)
df['content'] = df['content'].apply(ignore_unknown_emos)

df.to_csv("output.csv") #to a csv file


#plots are here
#removing the emos

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import pillow
import matplotlib.pyplot as plt

text = ""
#text = " ".join(x for x in df.content[df.name == "Pankaj Mani Dahal"])
text = " ".join(x for x in df.content)
text = re.sub("~[0-9]*~", "",text)
text = re.sub("~[0-9]*~", "",text)
text = re.sub(r"\\/"," ",text)
text = re.sub(r"[^a-zA-Z ']","",text)
text = re.sub(r"WB"," ",text)
text = re.sub(r"LU"," ",text)
text = re.sub(r"\s+"," ",text)


# Create stopword list:
stopwords = set(STOPWORDS)
stopwords.update(["Riju", "sent", "photo", "ko", "ni", "maa","video", "haru", "bhane", "ra", "Kei"])

# Generate a word cloud image
wordcloud = WordCloud(stopwords = stopwords, width = 2048, height = 1536, max_font_size=500, max_words=200, background_color="white").generate(text)

plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")

plt.savefig("img/wordcloud.png", format="png")


#other plots
#frequency
def get_frequency(x):
    return len(re.findall("\w+", x))

df['frequency'] = df['content'].apply(get_frequency)
df['freq1'] = df.frequency[df.name == names_list[0]].fillna(0)
df['freq2'] = df.frequency[df.name == names_list[1]].fillna(0)

df['cumfreq1'] = df['freq1'].cumsum()
df['cumfreq2'] = df['freq2'].cumsum()

plt.plot(df.time[df['name']==names_list[0]].values, df.cumfreq1[df['name']==names_list[0]].values, c = 'blue', label = names_list[0], linewidth = 2)
plt.plot(df.time[df['name']==names_list[1]].values, df.cumfreq2[df['name']==names_list[1]].values, c = 'red', label = names_list[1], linewidth = 2)
plt.show()


#get game scores
def get_scores(x):
    a = re.findall("(LU\d+-\d+)|(WB\d+-\d+)", x)
    if a==[]:
        return ""
    elif a[0][0] == "":
        return a[0][1]
    else:
        return a[0][0]

def get_diff(x):
    a = re.findall("(\d+)-(\d+)", x)
    print a
    return (int(a[0][1]) - int(a[0][0]))    

#get scores in scores column
df['scores'] = df['content'].apply(get_scores)
df_games = df[df.scores !=""]

df_games['diff'] = df_games['scores'].apply(get_diff)

WB = plt.scatter(df_games[df_games.scores.str.contains("WB")]['time'].values, df_games[df_games.scores.str.contains("WB")]['diff'].values, c = 'red', label = names_list[0], marker='x')
LU = plt.scatter(df_games[df_games.scores.str.contains("LU")]['time'].values, df_games[df_games.scores.str.contains("LU")]['diff'].values, c = 'blue', label = names_list[0],  marker='o')

plt.tick_params(labelsize=8)

plt.legend((WB, LU), ("Word Blitz", "Ludo"), loc='lower left', fontsize=8)
plt.savefig("img/WB_LU.png", format="png")



