from flask import Flask
from flask import  request
from flask import render_template
import re
from difflib import SequenceMatcher
from flask import url_for

app = Flask(__name__)

pwds = {}
comments = []

score_html_template = "<h3> Score: {{score}}</h3>"
comment_html_template = "<p class='col-md-12 navbar-text'>{{comment}}</p>"

html_page_template = '''
<html>
<head>
    <meta charset="utf-8">
    <title>Password validator</title>
    <meta name="viewport" content="width=1000, initial-scale=1.0, maximum-scale=1.0">

    <!-- Loading Bootstrap -->
    <link href="./static/flat-ui/dist/css/vendor/bootstrap/css/bootstrap.min.css" rel="stylesheet">
    <!-- Loading Flat UI -->
    <link href="./static/flat-ui/dist/css/flat-ui.css" rel="stylesheet">
    <link href="./static/flat-ui/docs/assets/css/demo.css" rel="stylesheet">
</head>
<body>
    <div class="container">
        <div style="margin-bottom: 20px" class="row">
            <img src="./static/password_validator.png" class="img-responsive col-md-2" alt="Password Validator">
            <h2 style="text-align: center" >Validate your password</h2>
            <h4 style="text-align: center">Share your score with your friends</h4>
        </div>
        <div class="col-md-offset-2">
            <div style="margin-bottom: 10px" class="row">
                <div class="col-md-4">
                    <form action="/" method="post">
                        <label for="username">Enter username and password:</label>
                        <input type="text" id="username" name="username" placeholder="Username" class="form-control" style="margin-bottom: 2px;"/>
                        <input type="password" id="password" name="password" placeholder="Password" class="form-control" style="margin-bottom: 2px;" />
                        <input type="submit" class="btn btn-primary btn-block" value="Evaluate">
                    </form>
                    {{MYSCORE}}
                </div>
            </div>
            <div class="row">
                <label class="col-md-8" for="comment">Enter your comment:</label>
                <div class="col-md-8">
                    <form action="/" method="post">
                        <div class="col-md-10" style="padding: 0; padding-right: 2px;">
                            <input type="text" id="comment" name="comment" placeholder="Comment" class="form-control" />
                        </div>
                        <input type="submit" class="btn btn-primary col-md-2" value="Share">
                    </form>
                </div>
            </div>

            <div class="row" style="margin-top: 20px">
                <h3 class="navbar-text">Comments:</h3>
            </div>

            <div class="row comments">
                {{COMMENTS}}
            </div>
        </div>
    </div>
</body>
</html>
'''



@app.route("/", methods=['GET', 'POST'])
# @app.route("/index", methods=['GET', 'POST'])
def hello():
    global comments
    score_html = ""
    comments_html = ""
    if("username" in request.form.keys() and "password" in request.form.keys()):
        score = password_strength(request.form["username"], request.form["password"])
        score_html = score_html_template.replace("{{score}}", str(score))
        # return render_template("index.html", score=score)
        # return html_page

    if("comment" in request.form.keys()):
        comments.append(request.form["comment"])
        # return render_template("index.html", comments=comments)    
    
    
    for comment in reversed(comments):
        comment_html = comment_html_template.replace("{{comment}}", comment)
        comments_html = comments_html + comment_html

    
    html_page = html_page_template
    
    html_page = html_page.replace("{{MYSCORE}}", score_html)
    html_page = html_page.replace("{{COMMENTS}}", comments_html)
    # return render_template("index.html")
    return html_page


@app.route("/flatui")
def flatui():
    return render_template("flat-ui/index.html")

def password_strength(username, passwd):
    if(username not in pwds.keys()):
        pwds[username] = []
    pwds[username].append(passwd)

    passwd = passwd.replace(" ", "")
    digits = re.findall(r"\d", passwd)
    letters = re.findall(r"[a-zA-Z]", passwd)

    lowercase = float(len(re.findall(r"[a-z]", passwd)))
    uppercase = float(len(re.findall(r"[A-Z]", passwd)))
    bonus_points = 0

    d = float(len(digits))
    l = float(len(letters))

    bonus_points += int(len(digits)>0)*4 \
                    + int(lowercase>0)*2 \
                    + int(uppercase>0)*2 \
                    + (len(passwd) - d - l) * 8

    match = SequenceMatcher(None, username, passwd)\
                .find_longest_match(0, len(username), 0, len(passwd))
    
    # common_substr_penalty = max(match.size - 3, 0) * 10
    common_substr_penalty = float(match.size)/len(letters) * 30 if match.size > 2 else 0
    # print( min(len(passwd), 16), " * 2")
    # print( min(l/d, d/l), " * 20")
    # print( min(lowercase/uppercase, uppercase/lowercase), " * 10")
    # print( len(passwd) - d - l, " * 8")
    # print( 0 - common_substr_penalty)
    letters_digit_ratio = min(l/d, d/l) if l >0 and d > 0 else 0
    lower_upper_ratio = min(lowercase/uppercase, uppercase/lowercase) if lowercase > 0 and uppercase > 0 else 0
    score =     min(len(passwd), 12)*2 \
                + letters_digit_ratio * 20  \
                + lower_upper_ratio * 10  \
                + bonus_points \
                - common_substr_penalty
    return score

@app.route('/login', methods=['GET', 'POST'])
def parse_request():
    '''
    request can have:
    username: String
    password: String
    field: String -- raises exception if its 'fuzzed'
    age: Int
    '''
    username = "username"
    password = "password"

    data = request.args  # data is empty
    # need posted data here
    print( request.args)
    print( request.form)
    # print( "field" in request.form.keys())
    if "field" in request.form.keys() and request.form['field'] == "fuzzed":
        raise Exception('Fuzzed')
    
    
    sameUsername = (request.form['username'] == username) if request.form['username'] else None

    if request.form['password']:
        # unsafe password comparison
        samePass=True
        for i in range(len(password)):
            if(request.form['password'][i] != password[i]):
                samePass=False
    
    age=None
    if request.form['age']:
        age = int(request.form['age'])

    if sameUsername and samePass:
        return "You have logged in successfully"
    
    return "This is the login url. You are not authenticated"
if __name__ == "__main__":
	app.run()
