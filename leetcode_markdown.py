import requests,json,re
import pyperclip
from flask import Flask, request, render_template

session = requests.Session()
user_agent = r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'

Remove = ["</?p>", "</?ul>", "</?ol>", "</li>", "</sup>"]
Replace = [["&nbsp;", " "], ["&quot;", '"'], ["&lt;", "<"], ["&gt;", ">"],
           ["&le;", "≤"], ["&ge;", "≥"], ["<sup>", "^"], ["&#39", "'"],
           ["&times;", "x"], ["&ldquo;", "“"], ["&rdquo;", "”"],
           [" *<strong> *", " **"], [" *</strong> *", "** "],
           [" *<code> *", " `"], [" *</code> *", "` "], ["<pre>", "```"],
           ["</pre>", "```"], ["<em> *</em>", ""], [" *<em> *", " *"],
           [" *</em> *", "* "], ["</?div.*?>", ""], ["	*</?li>", "- "]]

def convert(src):
    def remove_label_in_pre(matched):
        tmp = matched.group()
        tmp = re.sub("<[^>p]*>", "", tmp)
        return tmp

    src = re.sub("<pre>[\s\S]*?</pre>", remove_label_in_pre, src)
    for curPattern in Remove:
        src = re.sub(curPattern, "", src)
    for curPattern, curRepl in Replace:
        src = re.sub(curPattern, curRepl, src)
    return src

def gen_markdown(content, title, url, tags):
    markdowncontent = """
###### tags: {Tags}
# {Title}
## Description
{Content}
## Solution

```python=

```
    """.format(Title = title, Url = url, Content = content, Tags = tags)
    pyperclip.copy(markdowncontent)
    print("Copied to scrapbook!")   

def get_problem_by_slug(slug):
    print("here")
    if slug.startswith("https://leetcode.com/problems/"):
        slug = slug.replace("https://leetcode.com/problems/", "", 1).strip('/')
    url = "https://leetcode.com/graphql"
    params = {'operationName': "getQuestionDetail",
        'variables': {'titleSlug': slug},
        'query': '''query getQuestionDetail($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                questionId
                questionFrontendId
                questionTitle
                questionTitleSlug
                content
                difficulty
                stats
                similarQuestions
                categoryTitle
                topicTags {
                        name
                        slug
                }
            }
        }'''
    }

    json_data = json.dumps(params).encode('utf8')
                        
    headers = {'User-Agent': user_agent, 'Connection': 
        'keep-alive', 'Content-Type': 'application/json',
        'Referer': 'https://leetcode.com/problems/' + slug}
    resp = session.post(url, data = json_data, headers = headers, timeout = 10)
    content = resp.json()

    #generate markdown file
    title = content['data']['question']['questionFrontendId'] + '. ' + content['data']['question']['questionTitle']
    description = convert(content['data']['question']['content'])
    tags = ""
    for tagsName in content['data']['question']['topicTags']:
        tags += "`" + tagsName['name'] + "` "
    gen_markdown(description, title, url, tags)


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/convert', methods = ['POST'])
def search():
    get_problem_by_slug('https://leetcode.com/problems/add-two-numbers/')
    return render_template('home.html')
    
if __name__ == '__main__':
    app.run(debug=True)