#!/usr/bin/env python
# coding: utf-8

"""
File defining Entity Detector Function.
"""

import spacy
from spacy.tokenizer import Tokenizer
nlp = spacy.load("en_core_web_md")
tokenizer = Tokenizer(nlp.vocab)

from spacy.matcher import Matcher
import dateparser

def entity_detector(query, entities_to_detect = []):
    """
    Input parameters:
    - query::string 
        A string containing the query from which the entities are to be detected.
    - entities_to_detect::list 
        A list containing the entities that are to be detected. The entities that can be detected and inputs 
        to be provided to the list are 'dates', 'times', 'ages', 'quantities', 'amounts', 'numbers', 'emails'. 
        Note: If only the query is passed as input, all of the entities are detected by default.
    
    Output parameters:
    - results::dict
        Dict format:
        {'entity_result': [{'entity': 'entity1', 'entity': 'entity2'}], 
        'entity_result': [{'entity': 'entity1', 'entity': 'entity2'}]}

    Sample input: 
        entity_detector('Can you deliver thirteen apples and seventeen mangoes on 18th October?', ['dates', 'numbers'])
    Sample output:
        {'number_result': [{'number': 13}, {'number': 17}], 'date_result': [{'date': '2020-10-18 00:00:00'}]}
    """
    doc = nlp(query)
    results = {}
    entities_all = False
    if len(entities_to_detect) == 0:
        entities_all = True
        
    if entities_all:
        matcher = Matcher(nlp.vocab)
        num_pattern = [{"TEXT": {"REGEX": "^\d+$"}}]
        alphanum_pattern = [{'POS': {'IN': ['NUM']}}]
        matcher.add("Number", None, num_pattern, alphanum_pattern)
        results.update({'number_result': []})
        numbers = []
        email = [{"TEXT": {"REGEX": "^[^\s@]+@[^\s@]+\.[^\s@]+$"}}]
        matcher.add("Email", None, email)
        results.update({'email_result': []})
        dates = []
        results.update({'date_result': []})
        results.update({'age_result': []})
        times = []
        results.update({'time_result': []})
        quantities = []
        results.update({'quantity_result': []})
        amounts = []
        results.update({'money_result': []})
    else:
        if 'numbers' or 'emails' in entities_to_detect:
            matcher = Matcher(nlp.vocab)
            if 'numbers' in entities_to_detect:
                num_pattern = [{"TEXT": {"REGEX": "^\d+$"}}]
                alphanum_pattern = [{'POS': {'IN': ['NUM']}}]
                matcher.add("Number", None, num_pattern, alphanum_pattern)
                results.update({'number_result': []})
                numbers = []
            if 'emails' in entities_to_detect:
                email = [{"TEXT": {"REGEX": "^[^\s@]+@[^\s@]+\.[^\s@]+$"}}]
                matcher.add("Email", None, email)
                results.update({'email_result': []})

        for entity_to_detect in entities_to_detect:
            if entity_to_detect == 'dates' or entity_to_detect == 'ages':
                dates = []
                if entities_all or entity_to_detect == 'ages':
                    results.update({'age_result': []})
                if entities_all or entity_to_detect == 'dates':
                    results.update({'date_result': []})
            elif entity_to_detect == 'times':
                times = []
                results.update({'time_result': []})
            elif entity_to_detect == 'quantities':
                quantities = []
                results.update({'quantity_result': []})
            elif entity_to_detect == 'amounts':
                amounts = []
                results.update({'money_result': []})
                
    for ent in doc.ents:
        if ent.label_ == 'DATE':
            if entities_all or 'dates' in entities_to_detect or 'ages' in entities_to_detect:
                dates.append([ent, ent.start, ent.end])
                if dateparser.parse(str(ent)):
                    date = dateparser.parse(str(ent))
                    results['date_result'].append({'date': str(date)})
                else:
                    if 'years' or 'age' in ent:
                        results['age_result'].append({'age': str(ent)})
                    else:
                        results['date_result'].append({'date': str(ent)})
        if ent.label_ == 'TIME':
            if entities_all or 'times' in entities_to_detect:
                times.append([ent, ent.start, ent.end])
                if dateparser.parse(str(ent)):
                    time = dateparser.parse(str(ent))
                    results['time_result'].append({'time': str(time)})
                else:
                    results['time_result'].append({'time': str(ent)})
        if ent.label_ == 'QUANTITY':
            if entities_all or 'quantities' in entities_to_detect:
                quantities.append([ent, ent.start, ent.end])
                quantity_result = assign_unit(ent.text)
                results['quantity_result'].append(quantity_result)
        if ent.label_ == 'MONEY':
            if entities_all or 'amounts' in entities_to_detect:
                amounts.append([ent, ent.start, ent.end])
                money_result = assign_unit(ent.text)
                results['money_result'].append(money_result)
                
    if 'numbers' or 'emails' in entities_to_detect:
        for match_id, start, end in matcher(doc):
            if nlp.vocab.strings[match_id] == 'Email':
                if entities_all or 'emails' in entities_to_detect:
                    results['email_result'].append({'email': doc[start:end]})
            if nlp.vocab.strings[match_id] == 'Number':
                if entities_all or 'numbers' in entities_to_detect:
                    flag = False
                    if entities_all or 'dates' in entities_to_detect or 'ages' in entities_to_detect:
                        for entity in dates:
                            if doc[start:end].text in entity[0].text:
                                if start >= entity[1] and end <= entity[2]:
                                    flag = True
                    if entities_all or 'times' in entities_to_detect:
                        for entity in times:
                            if doc[start:end].text in entity[0].text:
                                if start >= entity[1] and end <= entity[2]:
                                    flag = True
                    if entities_all or 'quantities' in entities_to_detect:
                        for entity in quantities:
                            if doc[start:end].text in entity[0].text:
                                if start >= entity[1] and end <= entity[2]:
                                    flag = True
                    if entities_all or 'amounts' in entities_to_detect:
                        for entity in amounts:
                            if doc[start:end].text in entity[0].text:
                                if start >= entity[1] and end <= entity[2]:
                                    flag = True
                    if not flag:
                        numbers.append([doc[start:end], start, end])
        if entities_all or 'numbers' in entities_to_detect:
            textnum = []
            text_nums = []
            num_added = []
            for j in range(0, len(numbers)):
                if j == len(numbers) - 1:
                    if str(numbers[j][0]).isdigit():
                        results['number_result'].append({'number': numbers[j][0]})
                    else:
                        num = text2int(str(numbers[j][0]))
                        if num != 'Illegal word':
                            results['number_result'].append({'number': num})
                else:
                    if (numbers[j][2] == numbers[j+1][1]) or (str(doc[numbers[j][2]]) == 'and' and numbers[j][2] + 1 == numbers[j+1][1]):
                        if textnum and j != 0:
                            if numbers[j-1][2] != numbers[j][1] and str(doc[numbers[j-1][2]]) != 'and':
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
                                if num != 'Illegal word':
                                    results['number_result'].append({'number': num})
            if textnum:
                text_nums.append(textnum)
            for text_num in text_nums:
                text = ''
                for num in text_num:
                    text = text + ' ' + str(num)
                num = text2int(text)
                if num != 'Illegal word':
                    results['number_result'].append({'number': num})
    return results

def text2int(textnum, numwords={}):
    scalar = ["hundred", "thousand", "million", "billion", "trillion", "lakh", "crore"]
    words = tokenizer(textnum)
    if str(words[0]) in scalar:
        textnum = 'one ' + textnum
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

        if flag:
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

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current

def assign_unit(text):
    words = tokenizer(text)
    nums = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", 
           "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", 
           "fifty", "sixty", "seventy", "eighty", "ninety", "hundred", "thousand", "lakh", "crore", "hundred", "thousand", 
           "lakh", "crore"]
    flag = False
    for word in words:
        if str(word) in nums:
            flag = True
            break
    if flag:
        result = has_num(words)
    else:
        result = has_special_char(words)
    return result
    
def has_special_char(words):
    unit = ''
    number = ''
    if len(words) == 1:
        for c in str(words[0]): 
            if not c.isdigit() and not c.isspace():
                unit = unit + c
            elif c.isdigit():
                number = number + c
    else:
        for word in words:
            if str(word).isdigit():
                number = number + ' ' + str(word)
            else:
                unit = unit + ' ' + str(word)
    return [{'number': number}, {'unit': unit}]

def has_num(words):
    nums = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", 
           "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", 
           "fifty", "sixty", "seventy", "eighty", "ninety", "hundred", "thousand", "lakh", "crore", "hundred", "thousand", 
           "lakh", "crore"]
    
    unit = ''
    number = ''
    for word in words:
        if str(word) not in nums:
            unit = unit + ' ' + str(word)
        else:
            number = number + ' ' + str(word)
    number = text2int(number)
    return [{'number': number}, {'unit': unit}]
