from bs4 import BeautifulSoup as bs
import requests as req
import pandas as pd
import numpy as np
from transformers import GPT2TokenizerFast

tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

def count_tokens(text: str) -> int:
    #count the number of tokens in a string
    return len(tokenizer.encode(text))

def get_codes(req: object) -> list:
    codes = set()
    soup = bs(req.text,'html.parser')
    soup.prettify()

    parent = soup.find("div",id='toc')
    ids = parent.find_all("div",class_='Sect1')
    for i in ids:
        codes.add(i.get('id')[1:])
    return codes

def Sect1_Fetch(codes):
    for i in codes:
        c_list=[]
        print(i)
        request = req.get(f"https://www.mun.ca/regoff/calendar/sectionNo={i}")
        if request.ok:
            soup = bs(request.text,"html.parser")
            soup.prettify()
        
        parent = soup.find("div",id="content")
        sect1 = parent.find('div',class_="Sect1Title")
        sec = sect1.text.split()
        c_list.append(" ".join(sec[1:]))

        p_tags = sect1.find_next_siblings('p')
        p_text = ""
        for j in p_tags:
            p_text += j.text.strip()
        c_list.append(p_text)

        p_text = p_text.strip()
        token_length = count_tokens(p_text)
        c_list.append(token_length)
        course_list.append(c_list)

def course_descriptions(codes):
    for i in codes:
        c_list = []
        print(i)
        request = req.get(f"https://www.mun.ca/regoff/calendar/sectionNo={i}")
        if request.ok:
            soup = bs(request.text,"html.parser")
            soup.prettify()

            #Title 
            title = soup.find('div',class_='Sect2Title').text.split()
            title = title[1:]

            # CourseInfo
            course_info = soup.find_all('div',class_='CourseBlock')
            if course_info == None:
                continue
            for i in course_info:
                course = i.find_all('div',class_='course')
                for j in course:
                    cd = []
                    j = j.text.split()
                    cd.append(f"Course Descriptions of {' '.join(title)} courses")
                    cd.append(' '.join(j))
                    cd_text = ' '.join(cd)
                    token_length = count_tokens(cd_text)
                    cd.append(token_length)
                    c_list.append(cd)
            
            #Legend
            arr =[]
            legend = soup.find('div',class_='CourseLegend')
            if legend == None:
                continue
            legend = legend.text.strip()
            token_length = count_tokens(legend)
            arr.append("Glossary of Terms")
            arr.append(legend)
            arr.append(token_length)
            c_list.append(arr)

codes = ['SCI-2448', 'SCI-4418', 'SCI-0580', 'SCI-5276', 'SCI-2563', 'SCI-3705', 'SCI-4420', 'SCI-3086', 'SCI-4151', 'SCI-0579', 'SCI-2603', 'SCI-4166', 'SCI-4300']

def Sect2_Fetch(codes):
    for i in codes:
        c_list = []
        print(i)
        request = req.get(f'https://www.mun.ca/regoff/calendar/sectionNo={i}')
        if request.ok:
            soup = bs(request.text,'html.parser')
            soup.prettify()
        
        parent = soup.find("div",id="content")
        sect1 = parent.find('div',class_="Sect2Title")
        sect = sect1.text.split()
        c_list.append(" ".join(sect[1:]))

        p_tags = sect1.find_next_siblings('p')
        p_text = ''
        for j in p_tags:
            p_text += j.text.strip()
        c_list.append(p_text)

        p_text = p_text.strip()
        token_length = count_tokens(p_text)
        c_list.append(token_length)
        course_list.append(c_list)

def OL(codes):
    for i in codes:
        print(i)
        request = req.get(f'https://www.mun.ca/regoff/calendar/sectionNo={i}')
        if request.ok:
            soup = bs(request.text,'html.parser')
            soup.prettify()
        parent = soup.find("div",id="content")
        s4 = parent.find("div",class_="Sec4Title",string="11.2.3.2 Major in Biology (Co-operative) Program (BCOP) ")
        print(s4.text)
        ol = s4.find('ol',class_="Arabic")
        li = ol.find_all('li')
        for a in li:
            print(a.text)
    
def rec_sec2Fetch(codes):
    for i in codes:
        print(i)
        request = req.get(f'https://www.mun.ca/regoff/calendar/sectionNo={i}')
        if request.ok:
            soup = bs(request.text,'html.parser')
            soup.prettify()

            parent = soup.find("div",id="content")
            sect1 = parent.find_all('div',class_="Sect4Title")
            for i in sect1:
                arr = []
                name = i.text.split()
                arr.append(" ".join(name[1:]))
                text = ""

                ol = i.find_next_sibling('ol',class_='Arabic')
                if ol == None:
                    break
                ol = ol.text.split()
                ol = " ".join(ol)
                text += ol
                arr.append(text)

                token_length = count_tokens(text)
                arr.append(token_length)
                course_list.append(arr)

def fetchNext(codes):
    print(codes[0])
    request = req.get(f'https://www.mun.ca/regoff/calendar/sectionNo={codes[0]}')
    if request.ok:
        s = ""
        soup = bs(request.text,'html.parser')
        soup.prettify()
        parent = soup.find("div",id="content")
        for a in range(2,5):
            print(f'Sect{str(a)}Title')
            sec = parent.find_all('div',class_=f'Sect{str(a)}Title')
            
            for i in sec:
                r = i.text.split()
                r = " ".join(r)
                if(r.__eq__(s)):
                    continue
                else:
                    arr = []
                    name = i.text.split()
                    arr.append(" ".join(name[1:]))
                    text = ""

                    next = i.find_next_sibling()
                    while next.name != 'div':
                        content =  next.text.split()
                        content = " ".join(content)
                        text += content
                        next = next.find_next_sibling()
                    arr.append(text)

                    token_length = count_tokens(text)
                    arr.append(token_length)
                    course_list.append(arr)

def table(codes):
    print(codes[0])
    request = req.get(f'https://www.mun.ca/regoff/calendar/sectionNo={codes[0]}')
    if request.ok:
        soup = bs(request.text,'html.parser')
        soup.prettify()
        parent = soup.find("div",id="content")
        cap = parent.find_all("div",class_="caption")
        for i in cap:
            arr = []
            table_text = ""
            arr.append(i.text.strip())
            tab = i.find_next_sibling()
            tr = tab.find_all("tr")
            for a in tr:
                if (a == tr[0]):
                    continue
                text = "("
                td = a.find("td").text.split()
                text += " ".join(td) + ": "
                td2 = a.find("td",colspan="2")
                li = td2.find_all("li")
                for b in li:
                    con = b.text.split()
                    con = " ".join(con)
                    if b == li[-1]:
                        text += con + ")" + "," 
                    else:
                        text += con + ";"
                table_text += text
            arr.append(table_text)
            token_length = count_tokens(table_text)
            arr.append(token_length)
            course_list.append(arr)


course_list = []
# table(['SCI-1626'])
# # for i in course_list:
# #     print(i)

# df = pd.DataFrame(course_list,columns=['Heading','Content','Token Length'])
# df.insert(0,"Title","Information about Faculty of Science at Memorial University of Newfoundland")
# df.to_csv('FScience_CourseDes.csv',mode='a',index=False,header=0)
