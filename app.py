from flask import Flask
from flask import request, render_template, url_for
from flask import Response, redirect, abort
from fh_flask_api import *
from fh_flask_settings import REFRESH_TIME, MAX_LINES

app = Flask(__name__)

def add_headers_http(refresh, request, redirect=''):
    if redirect == '':
        redirect = request.url
    return {'Content-type':'text/html; charset=utf-8', 'Refresh':'{}; url={}'.format(refresh, redirect)}


@app.route('/')
def hello_world():
    table_head = 'Freelancehunt projects'
    try:
        arr = get_news()
        content = []

        for i in arr:
            tmp = {}
            tmp['project'] = i.clear_text
            tmp['author'] = i.login
            tmp['time'] = i.time.split('T')[1].split('+')[0][:-3]
            tmp['detail_url'] = url_for('project', project_id=i.project_id)
            content.append(tmp)
        return render_template('base.html', content_arr=content[:MAX_LINES], table_head=table_head), 200, add_headers_http(REFRESH_TIME, request, redirect='')
    except:
        return render_template('base.html', content_arr=[], table_head=table_head), 200, add_headers_http(REFRESH_TIME, request, redirect='')

@app.route('/detail/<project_id>')
def project(project_id):
    base_url = url_for('hello_world')
    try:
        detail = get_prj_detail(project_id)
        content = []
        author = "{} {} ({}) ".format(detail.fname, detail.sname, detail.login)
        content.append({'name':'Author : ', 'value': author})
        content.append({'name':'Title : ', 'value': detail.title})
        content.append({'name':'Status : ', 'value': detail.status_name})
        tags = ', '.join(detail.tags)
        content.append({'name':'Tags : ', 'value': tags})
        category = ', '.join(detail.skills)
        content.append({'name':'Category : ', 'value': category})
        content.append({'name':'Text : ', 'value': detail.description_html})
        return render_template('project.html', content=content, base_url=base_url), 200, add_headers_http(REFRESH_TIME, request, redirect='')
    except:
        return render_template('project.html', content=[], base_url=base_url), 200, add_headers_http(REFRESH_TIME, request, redirect='')


@app.route('/detail/')
def project_redirect():
    return redirect(url_for('hello_world'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
