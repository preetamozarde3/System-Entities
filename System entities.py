#!/usr/bin/env python
# coding: utf-8

# In[25]:


import spacy
nlp = spacy.load("en_core_web_md")


# In[28]:


num_pattern = [{"TEXT": {"REGEX": "^\d+$"}}]
alphanum_pattern = [{'POS': {'IN': ['NUM']}}]
email = [{"TEXT": {"REGEX": "^[^\s@]+@[^\s@]+\.[^\s@]+$"}}]


# In[29]:


from spacy.matcher import Matcher


# In[30]:


matcher = Matcher(nlp.vocab)


# In[31]:


matcher.add("Number", None, num_pattern, alphanum_pattern)
matcher.add("Email", None, email)


# In[56]:


def text2int(textnum, numwords={}):
    flag = False
    if 'lakh' in textnum or 'crore' in textnum:
        flag = True
    if not numwords:
        units = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen",
        ]

        tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

        if flag == True:
            scales = ["hundred", "thousand", "lakh", "crore"]
        else:
            scales = ["hundred", "thousand", "million", "billion", "trillion"]


        numwords["and"] = (1, 0)
        for idx, word in enumerate(units):  
            numwords[word] = (1, idx)
        for idx, word in enumerate(tens):
            numwords[word] = (1, idx * 10)
        for idx, word in enumerate(scales):
            if flag == True:
                if idx <= 1:
                    numwords[word] = (10 ** (idx * 3 or 2), 0)
                else:
                    numwords[word] = (10 ** (idx * 2 + 1), 0)
            else:
                numwords[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0
    for word in textnum.split():
        if word not in numwords:
            return 'Illegal word'
#             raise Exception("Illegal word: " + word)

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current


# In[94]:


doc1 = nlp("I want to buy 50 apples tomorrow")
doc2 = nlp("I want to buy 50 apples tomorrow at 9 PM")
doc3 = nlp("My email address is preetam@gmail.com")
doc4 = nlp("Can you send me 5 invitations on test@test.com?")
doc5 = nlp("I can send you the 10 invitations tomorrow at 3 PM on preetam@gmail.com")
doc6 = nlp("I need a delivery of five hundred forty thousand six hundred and seventy seven apples by tomorrow evening. Is it possible for you to contact me on preetam@floatbot.com")
doc7 = nlp("My name is Preetam and I am 23 years old. You can contact me on preetam@gmail.com")
doc8 = nlp("There is an urgent need of 50 people for the event held at 9 PM on the 18th. Can you confirm that the availability on test@test.com if you are fifteen years of age or over?")
doc9 = nlp("You can contact me on preetam@gmail.com by tomorrow evening or Sunday at the latest if you are eighteen years or older.")
doc10 = nlp("Can you deliver thirteen apples and seventeen mangoes on 18th October?")
docs = [doc1, doc2, doc3, doc4, doc5, doc6, doc7, doc8, doc9, doc10]


# In[95]:


import pandas as pd
import dateparser


# In[96]:


import datetime


# In[110]:


results = {'date_result': [], 'time_result': [], 'number_result': [], 'email_result': []}
for i in range(0, len(docs)):
    for ent in docs[i].ents:
        if ent.label_ == 'DATE':
            if dateparser.parse(str(ent)):
                date = dateparser.parse(str(ent))
                results['date_result'].append({'date': str(date)})
            else:
                results['date_result'].append({'date': str(ent)})
        if ent.label_ == 'TIME':
            if dateparser.parse(str(ent)):
                time = dateparser.parse(str(ent))
                results['time_result'].append({'time': str(time)})
            else:
                results['time_result'].append({'time': str(ent)})
    numbers = []
    for match_id, start, end in matcher(docs[i]):
        if nlp.vocab.strings[match_id] == 'Email':
            results['email_result'].append({'email': docs[i][start:end]})
        if nlp.vocab.strings[match_id] == 'Number':
            numbers.append([docs[i][start:end], start, end])
    textnum = []
    text_nums = []
    num_added = []
    for j in range(0, len(numbers)):
        if j == len(numbers) - 1:
            if str(numbers[j][0]).isdigit():
                results['number_result'].append({'number': numbers[j][0]})
            else:
                num = text2int(str(numbers[j][0]))
                results['number_result'].append({'number': num})
        else:
            if (numbers[j][2] == numbers[j+1][1]) or (str(docs[i][numbers[j][2]]) == 'and' and numbers[j][2] + 1 == numbers[j+1][1]):
                if textnum and j != 0:
                    if numbers[j-1][2] != numbers[j][1] and str(docs[i][numbers[j-1][2]]) != 'and':
                        text_nums.append(textnum)
                        textnum = []
                if len(textnum) > 0:
                    if textnum[-1] != numbers[j][0]:
                        textnum.append(numbers[j][0])
                        num_added.append(numbers[j][1])
                else:
                    textnum.append(numbers[j][0])
                textnum.append(numbers[j+1][0])
                num_added.append(numbers[j+1][1])
            else:
                if numbers[j][1] not in num_added:
                    if str(numbers[j][0]).isdigit():
                        results['number_result'].append({'number': numbers[j][0]})
                    else:
                        num = text2int(str(numbers[j][0]))
                        results['number_result'].append({'number': num})
    if textnum:
        text_nums.append(textnum)
    for text_num in text_nums:
        text = ''
        for num in text_num:
            text = text + ' ' + str(num)
        num = text2int(text)
        results['number_result'].append({'number': num})
print(results)


# In[ ]:




