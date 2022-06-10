import requests,json,re
import pyperclip
import tkinter as tk
import pyautogui


session = requests.Session()
user_agent = r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'

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
    for i in range(len(Remove)):
        src = re.sub(Remove[i], "", src)
    for i in range(len(Replace)):
        src = re.sub(Replace[i][0], Replace[i][1], src)
    return src

def gen_markdown(content, title, url, tags):
    markdowncontent = """###### tags: {Tags}
# {Title}
## Description
{Content}
## Solution

```python=

```""".format(Title = title, Url = url, Content = content, Tags = tags)
    pyperclip.copy(markdowncontent)
    print("Copied to scrapbook!")   

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
    title = content['data']['question']['questionFrontendId'] + '. ' + content['data']['question']['questionTitle']
    description = convert(content['data']['question']['content'])
    tags = ""
    for tagsName in content['data']['question']['topicTags']:
        tags += "`" + tagsName['name'] + "` "
    gen_markdown(description, title, url, tags)


def scrape():
    pyautogui.click(0, 200) # a random click for focusing the browser
    pyautogui.press('f6')
    pyautogui.hotkey('ctrl', 'c')
    url = pyperclip.paste()
    if url.startswith("https://leetcode.com"):
        get_problem_by_slug(url)
        label = tk.Label(window, text = 'Problem copied to clipboard!')
        label.pack()
        label.after(2000, label.destroy)
    else:
        label = tk.Label(window, text = 'There are no problems on this page!')
        label.pack()
        label.after(2000, label.destroy)

window = tk.Tk()
window.wm_attributes("-topmost", 1)

window.title('LeetCode.md')
w = 300
h = 100
ws = window.winfo_screenwidth()
hs = window.winfo_screenheight()
x = ws - w - 50
y = hs - h - 100

window.geometry('%dx%d+%d+%d' % (w, h, x, y))
label = tk.Label(window, text = '\n')
label.pack()
button = tk.Button(window,
                   text = 'Scrape', 
                   command = scrape)
button.pack()
window.mainloop()