import requests,json,re
from requests_toolbelt import MultipartEncoder
import os, pyperclip

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

def login(username, password):
    url = 'https://leetcode.com'
    cookies = session.get(url).cookies
    for cookie in cookies:
        if cookie.name == 'csrftoken':
            csrftoken = cookie.value

    url = "https://leetcode.com/accounts/login"
        
    params_data = {
        'csrfmiddlewaretoken': csrftoken,
        'login': username,
        'password':password,
        'next': 'problems'
    }
    headers = {'User-Agent': user_agent, 'Connection': 'keep-alive', 'Referer': 'https://leetcode.com/accounts/login/', "origin": "https://leetcode.com"}
    m = MultipartEncoder(params_data)   

    headers['Content-Type'] = m.content_type
    session.post(url, headers = headers, data = m, timeout = 10, allow_redirects = False)
    is_login = session.cookies.get('LEETCODE_SESSION') != None
    return is_login

def convert(src):
    # pre内部预处理
    def remove_label_in_pre(matched):
        tmp = matched.group()
        tmp = re.sub("<[^>p]*>", "", tmp)  # 不匹配>与p
        return tmp

    src = re.sub("<pre>[\s\S]*?</pre>", remove_label_in_pre,
                 src)  # 注意此处非贪心匹配，因为可能有多个示例
    # 可以直接删除的标签
    for curPattern in Remove:
        src = re.sub(curPattern, "", src)
    # 需要替换内容的标签
    for curPattern, curRepl in Replace:
        src = re.sub(curPattern, curRepl, src)
    return src

def gen_markdown(content, title, url, tags):
    #file = open(path, 'a', encoding="utf-8")
    markdowncontent = """
###### tags: {Tags}
# {Title}
## Description
{Content}
## Solution

```python=

```
    """.format(Title = title, Url = url, Content = content, Tags = tags)
    #file.write(markdowncontent)
    #print(path)
    #file.close()
    pyperclip.copy(markdowncontent)
    print("Copied to scrapbook!")

def get_problems():
    url = "https://leetcode.com/api/problems/all/"
    headers = {'User-Agent': user_agent, 'Connection': 'keep-alive'}
    resp = session.get(url, headers = headers, timeout = 10)
       
    question_list = json.loads(resp.content.decode('utf-8'))

    for question in question_list['stat_status_pairs']:
        # 题目编号
        question_id = question['stat']['question_id']
        # 题目名称
        question_slug = question['stat']['question__title_slug']
        # 题目状态
        question_status = question['status']

        # 题目难度级别，1 为简单，2 为中等，3 为困难
        level = question['difficulty']['level']

        # 是否为付费题目
        if question['paid_only']:
            continue
        print(question_slug)      

def get_problem_by_slug(slug):
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
    #print(content['data'])
    title = content['data']['question']['questionFrontendId'] + '. ' + content['data']['question']['questionTitle']
    description = convert(content['data']['question']['content'])
    #description = content['data']['question']['content']
    #print(description)
    #description = convert(description)
    tags = ""
    for tagsName in content['data']['question']['topicTags']:
        tags += "`" + tagsName['name'] + "` "
    #base_dir = os.getcwd()
    #newfolder = os.path.join(base_dir,
    #                         title.replace(". ", ".").replace(" ", "-"))
    #if not os.path.exists(newfolder):
        #os.makedirs(newfolder)
    #    print("create new folder ", newfolder)
    #else:
    #    print("already exist folder:", newfolder)

    # 生成 markdown 文件
    #filepath = os.path.join(base_dir, newfolder, "README.md")
    #gen_markdown(filepath, description, title, url, tags)
    gen_markdown(description, title, url, tags)

def get_submissions(slug):
    if slug.startswith("https://leetcode.com/problems/"):
        slug = slug.replace("https://leetcode.com/problems/", "", 1).strip('/')
    url = "https://leetcode.com/graphql"
    params = {'operationName': "Submissions",
        'variables':{"offset":0, "limit":20, "lastKey": '', "questionSlug": slug},
            'query': '''query Submissions($offset: Int!, $limit: Int!, $lastKey: String, $questionSlug: String!) {
                submissionList(offset: $offset, limit: $limit, lastKey: $lastKey, questionSlug: $questionSlug) {
                lastKey
                hasNext
                submissions {
                    id
                    statusDisplay
                    lang
                    runtime
                    timestamp
                    url
                    isPending
                    __typename
                }
                __typename
            }
        }'''
    }

    json_data = json.dumps(params).encode('utf8')

    headers = {'User-Agent': user_agent, 'Connection': 'keep-alive', 'Referer': 'https://leetcode.com/accounts/login/',
        "Content-Type": "application/json"}  
    resp = session.post(url, data = json_data, headers = headers, timeout = 10)
    content = resp.json()
    for submission in content['data']['submissionList']['submissions']:
        print(submission)

def get_submission_by_id(submission_id):
    url = "https://leetcode.com/submissions/detail/" + submission_id
    headers = {'User-Agent': user_agent, 'Connection': 'keep-alive', "Content-Type": "application/json"}
    code_content = session.get(url, headers = headers, timeout = 10)

    pattern = re.compile(r'submissionCode: \'(?P<code>.*)\',\n  editCodeUrl', re.S)
    m1 = pattern.search(code_content.text)
    code = m1.groupdict()['code'] if m1 else None
    print(code)

print(login('JgtL13', 'Lkrfgklgjkfd8813'))
# get_problems()

#while True:
#    url = input("LeetCode URL: ")
#    get_problem_by_slug(url)

get_problem_by_slug('https://leetcode.com/problems/add-two-numbers/')
#get_submissions('https://leetcode.com/problems/add-two-numbers/')
#get_submission_by_id('711949935')