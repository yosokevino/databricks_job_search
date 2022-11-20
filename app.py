from flask import *
import requests
import re

def scrub_search_terms(search_terms):

    term_list = search_terms.split(',')

    cleaned_search = ''

    for term in term_list:
        cleaned_search += f'{term.strip()},'

    return cleaned_search[:-1]

def highlight_search_terms(search_terms, html):

    working_html = html

    search_terms_list = re.split(",", search_terms)

    search_terms_list = [term.strip() for term in search_terms_list]   

    for term in search_terms_list:

        highlight_search_terms = f'<strong><mark style="background-color: yellow;">{term.upper()}</mark></strong>'

        working_html = highlight_search_terms.join(re.split(term, working_html, flags=re.IGNORECASE))

    return working_html

def get_data(url):

    response = requests.get(url)

    data = response.json()

    return data

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':

        search_terms = 'All'

        api_url = f'https://databricks-jobs-api.azurewebsites.net/?search_term'

        job_data = get_data(api_url)

        jobs = job_data['results']

        if jobs == 'No Results Found':
            job_count = 0
        else:
            job_count = len(job_data['results'])

        return render_template('index.html', jobs = jobs, job_count = job_count, search_terms = search_terms)

    if request.method == 'POST':

        search_terms = request.form['searchterms_name']

        scrubbed_terms = scrub_search_terms(search_terms)

        api_url = f'https://databricks-jobs-api.azurewebsites.net/?search_term={scrubbed_terms}'

        job_data = get_data(api_url)

        jobs = job_data['results']

        if jobs == 'No Results Found':
            job_count = 0
        else:
            job_count = len(job_data['results'])

        return render_template('index.html', jobs = jobs, job_count = job_count, search_terms = search_terms)

@app.route('/job', methods=['GET', 'POST'])
def job():
    if request.method == 'GET':

        return render_template('index.html')

    if request.method == 'POST':

        job_id = request.form['job_id_name']
        job_search_terms = request.form['job_id_search_terms']

        api_url = f'https://databricks-jobs-api.azurewebsites.net/?job_content={job_id}'

        job_content_data = get_data(api_url)

        if job_search_terms != 'All':

            job_content = highlight_search_terms(job_search_terms, job_content_data['results'][0]['html_content'])

        else:

            job_content = job_content_data['results'][0]['html_content']

        return render_template('job.html', job_content = job_content, job_id = job_id, job_search_terms = job_search_terms)
        
if __name__ == '__main__':

    app.run(debug=True, port=6969)