import hmac
import base64
import hashlib
import requests
import json
import re
from fh_flask_class import *
from fh_flask_settings import ID, API_KEY, MY_SKILLS

RE_STR = r'(?P<begin>.*)[<]a[ ].*["]>(?P<middle>.*)</a>(?P<end>.*)'
RE_BLOG_STR = r'(?P<begin>.*)[<]a[ ].*["]>(?P<middle>.*)</a>(?P<end>.*)'
METHOD = 'GET'
URL = 'https://api.freelancehunt.com/my/feed'
URL_PROJECT = 'https://api.freelancehunt.com/projects/{}'
URL_PROJECT_LIST = 'https://api.freelancehunt.com/projects'


def __sign(api_secret, url, method, post_params=''):
    msg = url + method + post_params
    h = hmac.new(api_secret, None, hashlib.sha256)
    h.update(msg.encode('utf-8'))
    return base64.b64encode(h.digest())


def re_text(line):
    try:
        r = re.compile(RE_STR)
        res = r.search(line)
        # print(res.group())
        project = res.group(2)
        # print('{} <== {}'.format(project, author))
        # print(res['middle'])
        return project
    except:
        return line


def re_blog_text(line):
    try:
        r = re.compile(RE_BLOG_STR)
        res = r.search(line)
        project = res.group(1)
        return project
    except:
        return line

def get_news():
    my_sign = __sign(API_KEY, URL, METHOD, )
    x = requests.get(URL, auth=(ID, my_sign))
    # print(x.status_code)
    # print(x.headers)
    # print(x.content)
    answ = json.loads(x.content.decode('utf-8'))
    arr = []
    for line in answ:
        new_line = FhNews()
        new_line.avatar = line['from']['avatar']
        new_line.login = line['from']['login']
        new_line.profile_id = line['from']['profile_id']
        new_line.author_url = line['from']['url']
        new_line.time = line['time']
        new_line.time_millis = line['time_millis']
        new_line.message = line['message']
        try:
            new_line.project_id = line['related']['project_id']
        except:
            new_line.project_id = ''
        if not new_line.project_id == '':
            new_line.clear_text = re_text(line['message'])
        else:
            new_line.clear_text = re_blog_text(line['message'])
#            new_line.clear_text = line['message']
        arr.append(new_line)
    return arr


def get_prj_detail(prj_id):
    url = URL_PROJECT.format(prj_id)
    my_sign = __sign(API_KEY, url, METHOD, )
    x = requests.get(url, auth=(ID, my_sign))
    answ = json.loads(x.content.decode('utf-8'))
    prj = FhProject()
    prj.avatar = answ['from']['avatar']
    prj.login = answ['from']['login']
    prj.fname = answ['from']['fname']
    prj.sname = answ['from']['sname']
    prj.author_url = answ['from']['url']
    prj.status_name = answ['status_name']
    prj.description = answ['description']
    prj.description_html = answ['description_html']
    skills = list(answ['skills'].values())
    prj.skills = skills
    prj.tags = answ.get('tags',[])
    prj.status_name = answ['status_name']
    prj.title = answ['name']
    return prj


def get_prj_list(skill_list=MY_SKILLS):
    my_skills = ','.join(str(x) for x in skill_list)

    url = '{}?skills={}'.format(URL_PROJECT_LIST, my_skills)
    my_sign = __sign(API_KEY, url, METHOD, )
    x = requests.get(url, auth=(ID, my_sign))
    answ = json.loads(x.content.decode('utf-8'))
    arr = []
    for line in answ:
        prj = FhProject()
        prj.project_id = line['project_id']
        prj.avatar = line['from']['avatar']
        prj.login = line['from']['login']
        prj.fname = line['from']['fname']
        prj.sname = line['from']['sname']
        prj.author_url = line['from']['url']
        prj.status_name = line['status_name']
        prj.description = line['description']
        prj.description_html = line['description_html']
        try:
            skills = line['skills']
        except:
            skills = []
        prj.skills = skills
        prj.tags = line.get('tags', [])
        prj.title = line['name']
        arr.append(prj)
    return arr