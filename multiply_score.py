import wsgiref.simple_server
import random
import urllib.parse
import sqlite3
import http.cookies
connection = sqlite3.connect('users.db')
stmt = "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
cursor = connection.cursor()
result = cursor.execute(stmt)
r = result.fetchall()
if r == []:
    exp = 'CREATE TABLE users (username,password)'
    connection.execute(exp)


def application(environ, start_response):
    headers = [('Content-Type', 'text/html; charset=utf-8')]
    path = environ['PATH_INFO']
    params = urllib.parse.parse_qs(environ['QUERY_STRING'])
    un = params['username'][0] if 'username' in params else None
    pw = params['password'][0] if 'password' in params else None
    if path == '/register' and un and pw:
        user = cursor.execute('SELECT * FROM users WHERE username = ?', [un]).fetchall()
        if user:
            start_response('200 OK', headers)
            return ['Sorry, this username {} has already been taken'.format(un).encode()]
        else:
            connection.execute('INSERT INTO users VALUES (?, ?)', [un, pw])
            connection.commit()
            headers.append(('Set-Cookie', 'session={}:{}'.format(un, pw)))
            start_response('200 OK', headers)
            return ['Username created successfully registered. <a href="/multiply">Account</a>'.format(
                un).encode()]
    elif path == '/login' and un and pw:
        user = cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', [un, pw]).fetchall()
        if user:
            headers.append(('Set-Cookie', 'session={}:{}'.format(un, pw)))
            headers.append(('Set-Cookie', 'score={}:{}'.format(0, 0)))
            start_response('200 OK', headers)
            return ['User {} logged in successfully. Click <a href="/multiply">here</a> to start the fun!'.format(
                un).encode()]
        else:
            start_response('200 OK', headers)
            return ['Incorrect username or password'.encode()]
    elif path == '/logout':
        headers.append(('Set-Cookie', 'session=0; expires=Thu, 01 Jan 1970 00:00:00 GMT'))
        start_response('200 OK', headers)
        return ['You are logged out. <a href="/">Login</a>'.encode()]
    elif path == '/multiply':
        start_response('200 OK', headers)
        if 'HTTP_COOKIE' not in environ:
            return ['Not logged in <a href="/">Login</a>'.encode()]
        cookies = http.cookies.SimpleCookie()
        cookies.load(environ['HTTP_COOKIE'])
        if 'session' not in cookies:
            return ['Not logged in <a href="/">Login</a>'.encode()]
        [un, pw] = cookies['session'].value.split(':')
        user = cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', [un, pw]).fetchall()
        handler = []
        resetScore = False
        if user:
            cookies = http.cookies.SimpleCookie()
            cookies.load(environ['HTTP_COOKIE'])
            if 'HTTP_COOKIE' in environ:
                [correct, wrong] = (cookies['score'].value.split(':'))
                page = '<!DOCTYPE html><html><head><title>Multiply with Score</title></head><body>'
            if 'factor1' in params and 'factor2' in params and 'selectedAnswer' in params:
                if 'selectedAnswer' in params:
                    fact1 = params['factor1'][0] if 'factor1' in params else None
                    fact2 = params['factor2'][0] if 'factor2' in params else None
                    selection = params['selectedAnswer'][0] if 'selectedAnswer' in params else None
                    if int(selection) == int(fact1) * int(fact2):
                        correct = int(correct) + 1
                        headers.append(('Set-Cookie', 'score={}:{}'.format(correct, wrong)))
                        return ['''<p style="background-color: green">Correct</p>
                        <a href="/multiply?reset=false">Click here to continue the game</a><br>'''.encode()]
                    else:
                        wrong = int(wrong) + 1
                        headers.append(('Set-Cookie', 'score={}:{}'.format(correct, wrong)))
                        return ['''<p style="background-color: red">Incorrect</p>
                        <a href="/multiply?reset=false">Click here to continue</a><br>'''.encode()]
            elif 'reset' in params:
                if params['reset'][0] == 'true':
                    correct = 0
                    wrong = 0
                    resetScore = True
                    headers.append(('Set-Cookie', 'score={}:{}'.format(correct, wrong)))
            f1 = random.randrange(10) + 1
            f2 = random.randrange(10) + 1
            cookies = http.cookies.SimpleCookie()
            cookies.load(environ['HTTP_COOKIE'])
            if 'HTTP_COOKIE' in environ:
                [correct, wrong] = cookies['score'].value.split(':')
            page = page + '<h1>What is {} x {}</h1>'.format(f1, f2)
            correctAns = f1 * f2
            randomAns1 = random.randint(0, 100)
            randomAns2 = random.randint(0, 100)
            randomAns3 = random.randint(0, 100)
            options = [correctAns, randomAns1, randomAns2, randomAns3]
            random.shuffle(options)
            if resetScore:
                correct = 0
                wrong = 0
            hyperlink = '<a href="/multiply?username={}&amp;password={}&amp;factor1={}&amp;factor2={}&amp;options={}">{}: {}</a><br>'
            String = '''<h2>
            a: <a href="/multiply?reset=false&factor1={}&factor2={}&selectedAnswer={}">{}</a><br>
            b:  <a href="/multiply?reset=false&factor1={}&factor2={}&selectedAnswer={}">{}</a><br>
            c:  <a href="/multiply?reset=false&factor1={}&factor2={}&selectedAnswer={}">{}</a><br>
            d:  <a href="/multiply?reset=false&factor1={}&factor2={}&selectedAnswer={}">{}</a>
            </h2>'''.format(f1, f2, options[0], options[0], f1, f2, options[1], options[1], f1, f2, options[2],
                            options[2], f1, f2, options[3], options[3])
            page += String
            page += '''<h2>Score</h2>
            Correct: {}<br>
            Wrong: {}<br>
            <a href="/multiply?reset=true">Reset Score</a>
            #<a href="/logout"> Logout</a>
            </body></html>'''.format(correct, wrong)
            return [page.encode()]
        else:
            return ['Not logged in. <a href="/">Login</a>'.encode()]
    elif path == '/':
            login_form = '''
                <style>
                p.a {
                    font: monospace;
                }
                </style>
                <form action= "/" style="background-color:pink">
                    <h1>Ready for some Multiplication?</h1>
                    <h2>Let's play!!!<h2>
                </form>
                <form action="/login" style="background-color:lightyellow">
                <h1>Login</h1>
                Username <input type="text" name="username"><br>
                Password <input type="password" name="password"><br>
                <input type="submit" value="Log in" formaction="/login">
                <input type="submit" value="Register" formaction="/register">
                </form>'''
            start_response('200 OK', headers)
            return [login_form.encode()]
    else:
        start_response('404 Not Found', headers)
        return ['Status 404: Resource not found'.encode()]


httpd = wsgiref.simple_server.make_server('', 8000, application)
httpd.serve_forever()

