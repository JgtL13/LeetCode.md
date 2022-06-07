# -*- coding: UTF-8 -*-
import os
import requests, json
import re

# 获取题目的方法来自下面的博客，并且添加了一些修改来更好地符合个人需要。
# https://wanakiki.github.io/2020/leetcode-spider/
Remove = ["</?p>", "</?ul>", "</?ol>", "</li>", "</sup>"]
Replace = [["&nbsp;", " "], ["&quot;", '"'], ["&lt;", "<"], ["&gt;", ">"],
           ["&le;", "≤"], ["&ge;", "≥"], ["<sup>", "^"], ["&#39", "'"],
           ["&times;", "x"], ["&ldquo;", "“"], ["&rdquo;", "”"],
           [" *<strong> *", " **"], [" *</strong> *", "** "],
           [" *<code> *", " `"], [" *</code> *", "` "], ["<pre>", "```\n"],
           ["</pre>", "\n```\n"], ["<em> *</em>", ""], [" *<em> *", " *"],
           [" *</em> *", "* "], ["</?div.*?>", ""], ["	*</?li>", "- "]]


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


def get_today_name() -> str:
    """
        获取今天的每日一题的 slug
    """
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"
    session = requests.Session()
    url = "https://leetcode-cn.com/graphql"
    params = {
        'oprationName':
        "questionOfToday",
        'query':
        '''
        query questionOfToday {
            todayRecord {
                question {
                    questionFrontendId
                    questionTitleSlug
                    __typename
                }
                lastSubmission {
                    id
                    __typename
                }
                date
                userStatus
                __typename
            }
        }
        '''
    }
    json_data = json.dumps(params).encode('utf8')
    headers = {
        'User-Agent': user_agent,
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Referer': 'https://leetcode-cn.com/problemset/all/'
    }
    resp = session.post(url, data=json_data, headers=headers, timeout=10)
    resp.encoding = 'utf8'
    content = resp.json()
    # 题目详细信息
    # print(content)
    question = content['data']['todayRecord'][0]['question']
    return question['questionTitleSlug']


def get_today_url():
    return "https://leetcode-cn.com/problems/" + get_today_name


def get_all(slug: str) -> dict:
    """根据题目的 id 获取题目的名字，内容，代码块，标签，返回 json 格式的 dict 对象
    """
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"
    session = requests.Session()
    url = "https://leetcode-cn.com/graphql"
    params = {
        'operationName':
        "getQuestionDetail",
        'variables': {
            'titleSlug': slug
        },
        'query':
        '''query getQuestionDetail($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                questionId
                questionFrontendId
                title
                titleSlug
                content
                translatedTitle
                translatedContent
                difficulty
                topicTags {
                    name
                    slug
                    translatedName
                    __typename
                }
                codeSnippets {
                    lang
                    langSlug
                    code
                    __typename
                }
                __typename
            }
        }'''
    }
    json_data = json.dumps(params).encode('utf8')
    headers = {
        'User-Agent': user_agent,
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Referer': 'https://leetcode-cn.com/problems/' + slug
    }
    resp = session.post(url, data=json_data, headers=headers, timeout=10)
    resp.encoding = 'utf8'
    content = resp.json()
    # 题目详细信息
    # print(content)
    question = content['data']['question']
    return question


def get_problem_content(slug: str) -> str:
    question = get_all(slug)
    res = convert(question['translatedContent'])
    # 在正文后面填上标签
    res += "\n \n**标签**\n"
    tags = question['topicTags']
    for tag in tags:
        if tag['translatedName'] != None:
            tagName = tag['translatedName']
        else:
            tagName = tag['name']
        res += "`" + tagName + "` "

    return res + "\n"


def get_solution_by_lang(slug: str, lang: str) -> str:
    """
        获取给定题目的对应语言的函数

        支持的参数如下

        C++ Java Python Python3 C C# JavaScript Ruby Swift Go Scala Kotlin
        Rust PHP TypeScript Racket
    """
    question = get_all(slug)
    # 获取对应语言的函数
    codeSnippets = question['codeSnippets']
    for x in codeSnippets:
        if x['lang'] == lang:
            return x['code']


def gen_markdown(path, content, title, url):
    """ 生成 markdown 文件
    """
    file = open(path, 'a', encoding="utf-8")
    markdowncontenct = """# {titlename}
[{Url}]({Url}) 
## 原题
{Content}

## 
```go

```
>
""".format(titlename=title, Url=url, Content=content)
    file.write(markdowncontenct)
    print(path)
    file.close()


def gen_gofile(path: str, title: str, url: str, func: str) -> None:
    """ 生成 solution_test.go 文件
    
    """
    file = open(path, 'a', encoding="utf-8")
    go_content = """package leetcode

import (
	"reflect"
	"testing"
)

// {0}
// {1}
{2}
func TestSolution(t *testing.T) {{
	testCases := []struct {{
		desc string
		want 
	}}{{
		{{
            want: ,
		}},
	}}
	for _, tC := range testCases {{
		t.Run(tC.desc, func(t *testing.T) {{
			get := 
			if !reflect.DeepEqual(tC.want,get){{
				t.Errorf("input: %+v get: %v\\n",tC,get)
			}}
		}})
	}}
}}
""".format(title.replace(" ", ""), url, func)
    file.write(go_content)
    print(path)
    file.close()


def gen_go_mod(path: str) -> None:
    """
        生成 go.mod 文件
    """
    file = open(path, 'a', encoding="utf-8")
    file.write("module leetcode\ngo 1.15")
    file.close()


def gen_files(url: str):
    """
        根据 url 生成对应的文件

        当 url 为空时自动爬取每日一题
        当 url 不为空时爬取对应的题目
    """
    if url.startswith("https://leetcode-cn.com/problems/"):
        slug = url.replace("https://leetcode-cn.com/problems/", "",
                           1).strip('/')
    elif len(url) > 0:
        print(
            "Wrong URL ! Please Check\n.It should be like https://leetcode-cn.com/problems/evaluate-division/"
        )
    else:
        slug = get_today_name()
    url = "https://leetcode-cn.com/problems/" + slug
    question = get_all(slug=slug)
    title = question['questionFrontendId'] + '.' + question['translatedTitle']

    content = get_problem_content(slug)

    func = get_solution_by_lang(slug, 'Go')
    content = re.sub(r'\n\n\n\n*', "\n", content)  # 替换掉多个换行符

    base_dir = os.getcwd()
    newfolder = os.path.join(base_dir,
                             title.replace(". ", ".").replace(" ", "-"))
    if not os.path.exists(newfolder):
        os.makedirs(newfolder)
        print("create new folder ", newfolder)
    else:
        print("already exist folder:", newfolder)

    # 生成 markdown 文件
    filepath = os.path.join(base_dir, newfolder, "README.md")
    gen_markdown(filepath, content, title, url)

    # 生成 solution_test.go 文件
    filepath = os.path.join(base_dir, newfolder, "solution_test.go")
    gen_gofile(filepath, title, url, func)

    # 生成 go.mod 文件
    filepath = os.path.join(base_dir, newfolder, "go.mod")
    gen_go_mod(filepath)
    return


if __name__ == '__main__':
    # 只用修改这个 url 即可
    # 比如题目链接为 https://leetcode-cn.com/problems/evaluate-division/ 就直接全部复制即可
    # 当 url 为空的时候爬取每日一题
    url = ""

    gen_files(url=url)