"""
@urbanij
===
Jan 2021
    Run this script inside the root folder, where all the `messages.html` files are.
    It has a whole lot of room for improvements, you're very welcome to contribute/fork etc.

"""
import os
import bs4
import datetime
import time
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import matplotlib.ticker as mtick
import seaborn as sns
import re

PLOT_DATE_FORMAT = "%b %d, %Y" # Check [Here](https://strftime.org/) if you prefer a different one.

class MsgFileName:
    """ Only required for getting the number out of
    the filename and thus sort the list of messages.html file names.
    Had I not sorted it, the timestamps would have resulted in a non-sorted order.
    
    Parameters
    ----------
    filename: string

    Examples
    --------
    >>> import os, re
    >>> [ i for i in os.listdir() if str(i).startswith('messages') ]
    ['messages33.html',
     'messages25.html',
     'messages13.html',
     'messages44.html',
     'messages2.html',
     ...
    ]

    >>> messages_files = [MsgFileName(i) for i in os.listdir() if str(i).startswith('messages')]
    >>> messages_files = sorted(messages_files, key=lambda x : x.getNumber(), reverse=False)
    """
    
    MESSAGES_REGEX_PATTERN = r'(messages)(|\d+)(.html)'

    def __init__(self, filename):
        self.filename = filename
        self.number = self._extractNumber()

    def _extractNumber(self):
        if self.filename == "messages.html": return 1
        m = re.search(self.MESSAGES_REGEX_PATTERN, self.filename)
        if m: return int(m.group(2))

    def getFilename(self):
        return self.filename

    def getNumber(self):
        return self.number

class Message:
    """ Models the single message 
    
    Examples
    --------
    >>> Message('29.05.2019 11:26:30')
    <__main__.Message at 0x11a0e1130>
    
    >>> Message('29.05.2019 11:26:30').getEpochDate()
    1559121990.0

    >>> Message('29.05.2019 11:26:30').getReadableDate()
    'May 29, 2019'
    """
    def __init__(self, timestamp_string: str):
        self.timestamp_string: str = timestamp_string
        self.dt: datetime.datetime = datetime.datetime.strptime(timestamp_string, '%d.%m.%Y %H:%M:%S')
  
    def getEpochDate(self) -> float:
        return self.dt.timestamp()

    def getReadableDate(self) -> str:
        return self.dt.strftime(PLOT_DATE_FORMAT)



messages_files = [MsgFileName(i) for i in os.listdir() if str(i).startswith('messages')]
messages_files = sorted(messages_files, key=lambda x : x.getNumber(), reverse=False)


msgs = []
for file in messages_files:
    with open(file.getFilename(), 'r') as f:
        content = f.read()

        soup = bs4.BeautifulSoup(content, 'lxml')

        texts = soup.find_all('div', {'class':'body'})

        for group in soup.find_all('div', {'class':'body'}):
            try:
                msgs.append( Message(group.find('div', {'class': 'pull_right date details'})['title']) )
            except Exception as e:
                # it's not a text message, maybe a sticker, gif or else.
                pass


timestamps = [ msg.getEpochDate() for msg in msgs ]


NUM_BINS = 900
plt.title(f"# messages from {msgs[0].getReadableDate()} to {msgs[-1].getReadableDate()}:\n{len(msgs)}")
# plt.hist(timestamps, bins=NUM_BINS); 
sns.histplot(data=timestamps, bins=NUM_BINS, kde=True)
plt.gcf().autofmt_xdate()
plt.gca().xaxis.set_major_formatter(
    mtick.FuncFormatter(lambda pos,_: time.strftime("%b %d, %Y",time.localtime(pos)))
    )
plt.xlim(timestamps[0], timestamps[-1])
plt.tight_layout()
plt.show()
