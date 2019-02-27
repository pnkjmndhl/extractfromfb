import re
import pandas
import math
import numpy as np
import sys
from PIL import Image
from collections import Counter  # for counting number of values in a list
from datetime import datetime  # converting the datetime
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup as bs
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator


try:
    filename = sys.argv[1]
    if sys.argv[1] in ["-h", "-h"]:
        print "Usage: python extract.py <filename.html>"
except:
    print ("html filename not provided, using default messages.html")
    filename = "message.html"

#assets
path_case_insensitive_list = r"assets/case_insensitive.txt"
path_stopwords_list = r"assets/stopwords.txt"
path_replacement_dict_list = r"assets/replace.txt"

#path
path_mask_png = 'img/heart.png'



time_format = '%b %d, %Y, %I:%M %p'
first_chat_date = ""
last_chat_date = ""
date_time_df = pandas.DataFrame({"Year": [], "Month": [], "Seconds": []})

soup = bs(open(filename), "html.parser")
tds = soup.find_all(text=True)

# get names list from the most common 2 words (thats always the names)
names = Counter(x for x in tds).most_common(2)
names_list = [names[0][0], names[1][0]]
name_string = names_list[0].split(" ")[0] + "_" + names_list[1].split(" ")[0] + "_"

# converting all the unicode emos to numbers
emo_replaces_numb_dict = {
    u'\u2019': "'",
    u'\U0001f600': '~1~',
    u'\U0001f603': '~2~',
    u'\U0001f604': '~3~',
    u'\U0001f601': '~4~',
    u'\U0001f606': '~5~',
    u'\U0001f605': '~6~',
    u'\U0001f923': '~7~',
    u'\U0001f602': '~8~',
    u'\U0001f642': '~9~',
    u'\U0001f643': '~10~',
    u'\U0001f609': '~11~',
    u'\U0001f60a': '~12~',
    u'\U0001f607': '~13~',
    u'\U0001f60d': '~14~',
    u'\U0001f929': '~15~',
    u'\U0001f44d': '~16~',
    u'\U0001f937': '~17~',
    u'\U0001f3fd': '~18~',
    u'\u200d\u2640\ufe0f': '~19~',
    u'\U0001f914': '~20~',
}


# functions
# frequency
def get_frequency(x):
    return len(re.findall("\w+", x))


# converting datetime to seconds
def string_to_secs(x):
    return (datetime.strptime(x, time_format) - first_chat_date).total_seconds()


# update global first chat date and last chat date
def update_dates_and_convert_to_seconds(x):
    global first_chat_date
    global last_chat_date
    if first_chat_date == "":
        first_chat_date = datetime.strptime(x, time_format)
    last_chat_date = datetime.strptime(x, time_format)
    return (datetime.strptime(x, time_format) - first_chat_date).total_seconds()


# replace unspecified emos with ""
def ignore_unknown_emos(x):
    return x.encode('ascii', 'ignore').decode('ascii')


# get game scores
def get_scores(x):
    re_exp = ""
    for games in game_names:
        re_exp = re_exp + "^(?! )(" + games + "\d+-\d+)|"
    re_exp = re_exp[:-1]
    # print re_exp
    a = re.findall(re_exp, x)
    if a == []:
        return ""
    a = list(a[0])
    a = [x for x in a if x != ""]
    return a[0]


# get difference between scores, b-a
def get_diff(x):
    a = re.findall("(\d+)-(\d+)", x)
    return (int(a[0][1]) - int(a[0][0]))


# get time duration in minutes from call log
def get_time(x):
    if re.match("Duration:\s+(\d*)\s+minutes", x):
        return int(re.findall("Duration:\s+(\d*)\s+minutes", x)[0])
    else:
        return 0  # seconds is not working for some reason so removed the feature
        # return float(re.findall("Duration:\s+(\d*)\s+seconds", x)[0]) / 60


# datetime converted to x-axis label, global date_time_df updated
def get_time_labels():
    global first_chat_date
    global last_chat_date
    global date_time_df
    year_range = range(first_chat_date.year, last_chat_date.year + 2)
    month_range = range(1, 13)
    for year in year_range:
        for month in month_range:
            if datetime(year, month, 1, 0, 0) > last_chat_date:
                continue
            else:
                date_time_df = date_time_df.append(pandas.DataFrame({"Year": [year], "Month": [month], "Seconds": [
                    (datetime(year, month, 1, 0, 0) - first_chat_date).total_seconds()]}))
    date_time_df = date_time_df[date_time_df.Seconds > 0]
    # if the dataframe is too big divide into pieces
    every_n_value = int(math.floor(len(date_time_df) / 6))
    if every_n_value > 1:
        date_time_df = date_time_df.iloc[::every_n_value, :]
    # print date_time_df
    date_time_df = date_time_df.astype(int).astype(str)
    date_time_df['label'] = date_time_df['Month'] + '/' + date_time_df['Year']


# list and dataframe
my_df = pandas.DataFrame({"instant": [], "name": [], "content": [], "time": ""})
time_df = pandas.DataFrame({"instant": [], "name": [], "content": [], "time": []})
tds2 = list(reversed(tds[7:-1]))  # strip start and end junk

# Regular Expressions
# game_to_remove
game_identifiers = ["[A-z]* played back, now it is your turn!", "[A-z] has started a game with you. It's your turn",
                    "[A-z]* has invited you to play [A-z]* with them", "[A-z]* sent an attachment."]
game_identifiers_re = [re.compile(x) for x in game_identifiers]
r_date = re.compile("[A-z]+\s+\d+,\s+\d+,\s+\d:\d+\s+[A-z]+")
# reactions identifier (if the list value is emoName)
r_liked = re.compile("~[0-9][0-9]~" + names_list[0] + "|~[0-9][0-9]~" + names_list[1])
call_contents = ['The video chat ended.', "You called ", " called you."]
call_contents_re = [re.compile(x) for x in call_contents]

# cleanups
# replace all the emos with ~##~
for key, value in emo_replaces_numb_dict.iteritems():
    tds2 = [x.replace(key, value) for x in tds2]

# more clean up and create dataframe
for value in tds2:
    if value in names_list:
        name = value
        my_df = my_df.append({'instant': date, 'name': name, "content": content}, ignore_index=True)
    elif re.match(r_date, value) is not None:
        date = value
    elif re.match(r_liked, value) is not None:
        pass
    elif re.match(game_identifiers_re[0], value) is not None:  # removing game invites and blah blah
        content = ""
    elif re.match(game_identifiers_re[1], value) is not None:
        content = ""
    elif re.match(game_identifiers_re[2], value) is not None:
        content = ""
    elif re.match(game_identifiers_re[3], value) is not None:
        content = ""
    else:
        content = value

my_df['time'] = my_df['instant'].apply(update_dates_and_convert_to_seconds)
my_df['content'] = my_df['content'].apply(ignore_unknown_emos)

# creating wordcloud

# before get the name of games

text = " ".join(x for x in my_df.content)
game_names = list(set((re.findall("([A-Z]+)\d+-\d+", text))))

# cleaning up
# removing game names
for name in game_names:
    text = re.sub(name, " ", text)

re_sub_dict = {"~[0-9]*~": "", r"\\/": " ", r"[^a-zA-Z ']": "", r"\s+": " ", r"The video chat ended.": " ",
               r"sent a photo.": " ", r"sent a video": " ", r"sent an attachment.": " ",
               r"missed a video chat with": " ", r'[A-z ]* sent a GIF[A-z. ]*': " "}

# substitute ~##~ with ""
# substitute / with ""
# anything but A-z and space are removed
# multiple spaces converted to single space

for key, value in re_sub_dict.items():
    text = re.sub(key, value, text)

# remove case insensitivity
with open(path_case_insensitive_list, 'r') as f:
    case_insensitive_list = f.read().splitlines()

for value in case_insensitive_list:
    text = re.sub(r"(?i)(" + value + ")", value, text)  # missed a video chat with

# Create stopword list:
stopwords = set(STOPWORDS)

with open(path_stopwords_list, 'r') as f:
    nepali_stopwords = f.read().splitlines()

names = [names_list[0].split(" ")[0], names_list[1].split(" ")[0]]
stopwords.update(nepali_stopwords)
stopwords.update(names)

# pre-processing the text a little bit
with open(path_replacement_dict_list, 'r') as f:
    replacement_dict = f.read().splitlines()
replacement_dict = {x.split(" ")[0]: x.split(" ")[1] for x in replacement_dict}

# replace
for key, value in replacement_dict.iteritems():
    text = text.replace(key, value)

# add image
mask = np.array(Image.open(path_mask_png))
image_colors = ImageColorGenerator(mask)

# Generate a word cloud image
wordcloud = WordCloud(stopwords=stopwords, max_font_size=800, max_words=400, mode="RGBA", mask=mask,
                      font_path="comic.ttf", background_color="white").generate(text)
# wordcloud = WordCloud(stopwords=stopwords, width=2970, height=2100, max_font_size=800, max_words=400, background_color="white", font_path="comic.ttf", mode="R").generate(text)

plt.close()
plt.imshow(wordcloud.recolor(color_func=image_colors), interpolation='quadric')
# plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.savefig("img/" + name_string + "wordcloud.png", format="png", dpi=1500)

# other plots
# conversation frequency plot
get_time_labels()
my_df['frequency'] = my_df['content'].apply(get_frequency)
my_df['freq1'] = my_df.frequency[my_df.name == names_list[0]].fillna(0)
my_df['freq2'] = my_df.frequency[my_df.name == names_list[1]].fillna(0)
my_df['cumfreq1'] = my_df['freq1'].cumsum()
my_df['cumfreq2'] = my_df['freq2'].cumsum()

plt.close()
plt.tick_params(labelsize=8)
plt.plot(my_df.time[my_df['name'] == names_list[0]].values, my_df.cumfreq1[my_df['name'] == names_list[0]].values,
         c='blue',
         linewidth=2, label=names_list[0].split(" ")[0])
plt.plot(my_df.time[my_df['name'] == names_list[1]].values, my_df.cumfreq2[my_df['name'] == names_list[1]].values,
         c='red',
         linewidth=2, label=names_list[1].split(" ")[0])
plt.legend(loc='upper left', fontsize=8)
plt.xticks(list(date_time_df.Seconds.astype(int).values), list(date_time_df.label.values))
plt.savefig("img/" + name_string + "conversation_frequency.png", format="png")

# plot scores
# get scores in scores column
my_df['scores'] = my_df['content'].apply(get_scores)
df_games = my_df[my_df.scores != ""]
df_games['diff'] = df_games['scores'].apply(get_diff)
plt.close()

a = {}
c = ['red', 'green', 'blue', 'yellow', 'pink']
m = ['x', 'o', '+', '*', 't']
count = 0
for name in game_names:
    a[name] = plt.scatter(df_games[df_games.scores.str.contains(name)]['time'].values,
                          df_games[df_games.scores.str.contains(name)]['diff'].values, c=c[count], marker=m[count])
    count = count + 1
plt.tick_params(labelsize=8)
plt.xticks(list(date_time_df.Seconds.astype(int).values)[2:],
           list(date_time_df.label.values)[2:])  # first 2 months no play

plt.legend(a.values(), a.keys(), loc='lower left', fontsize=8)
plt.savefig("img/" + name_string + "games_plot.png", format="png")

# plot calls
for value in tds2:
    matched = re.match(call_contents_re[0], value) or re.match(call_contents_re[1], value) or re.match(
        call_contents_re[2], value)
    if matched is not None:
        time_df = time_df.append({'instant': date, 'name': name, "content": content}, ignore_index=True)
    elif value in names_list:
        name = value
    elif re.match(r_date, value) is not None:
        date = value
    else:
        content = value

time_df['calltime'] = time_df['content'].apply(get_time)
time_df['time'] = time_df['instant'].apply(string_to_secs)
time_df['cumtime'] = time_df['calltime'].cumsum()

plt.close()
plt.tick_params(labelsize=8)
plt.plot(time_df.time.values, time_df.cumtime.values, c='blue',
         linewidth=2, label="Time in minutes")
plt.legend(loc='upper left', fontsize=8)
plt.xticks(list(date_time_df.Seconds.astype(int).values), list(date_time_df.label.values))
plt.savefig("img/" + name_string + "callinminutes.png", format="png")

# combined plot
plt.close()
plt.tick_params(labelsize=8)
plt.plot(my_df.time[my_df['name'] == names_list[0]].values, my_df.cumfreq1[my_df['name'] == names_list[0]].values,
         c='blue',
         linewidth=2, label=names_list[0].split(" ")[0])
plt.plot(my_df.time[my_df['name'] == names_list[1]].values, my_df.cumfreq2[my_df['name'] == names_list[1]].values,
         c='red',
         linewidth=2, label=names_list[1].split(" ")[0])
plt.plot(time_df.time.values, time_df.cumtime.values, c='blue',
         linewidth=2, label="Time in minutes")
plt.legend(loc='upper left', fontsize=8)
plt.xticks(list(date_time_df.Seconds.astype(int).values), list(date_time_df.label.values))
plt.savefig("img/" + name_string + "conversation_frequency.png", format="png")

plt.close()
plt.tick_params(labelsize=8)
plt.legend(loc='upper left', fontsize=8)
plt.xticks(list(date_time_df.Seconds.astype(int).values), list(date_time_df.label.values))
plt.savefig("img/" + name_string + "callinminutes.png", format="png")

# write a csv file
my_df.to_csv("output/" + name_string + "report.csv")  # to a csv file


# combined plot
plt.close()

fig, ax1 = plt.subplots()

t11 = my_df.time[my_df['name'] == names_list[0]].values
t12 = my_df.time[my_df['name'] == names_list[1]].values
t3 = time_df.time.values
s11 = my_df.cumfreq1[my_df['name'] == names_list[0]].values
s12 = my_df.cumfreq2[my_df['name'] == names_list[1]].values
s3 = time_df.cumtime.values

ax1.plot(t11, s11, c='blue', linewidth=2, label=names_list[0].split(" ")[0])
ax1.plot(t12, s12, c='red', linewidth=2, label=names_list[1].split(" ")[0])
ax1.set_xlabel('Day')
# Make the y-axis label, ticks and tick labels match the line color.
ax1.set_ylabel('Words', color='blue')
ax1.tick_params('y', colors='blue')

ax2 = ax1.twinx()

ax2.plot(t3, s3, 'green', label='Time in minutes')
ax2.set_ylabel('time(minutes)', color='green')
ax2.tick_params('y', colors='green')

fig.tight_layout()
# fig.xticks(list(date_time_df.Seconds.astype(int).values), list(date_time_df.label.values))


plt.savefig("img/" + name_string + "combined.png", format="png")
