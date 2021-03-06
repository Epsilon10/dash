'''
MIT License

Copyright (c) 2017 cgrok

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''



from sanic import Sanic
from sanic.response import html
from jinja2 import Environment, PackageLoader
import aiohttp
import os
import discord
import json

app = Sanic(__name__)
env = Environment(loader=PackageLoader('app', 'templates'))

app.static('/assets', './templates/assets')
app.static('/templates', './templates')

botname = 'Statsy'

def login_required():
    def decorator(f):
        def wrapper(request, **kwargs):
            #do shit
            pass
        return wrapper
    return decorator

@app.listener('before_server_start')
async def init(app, loop):
    app.session = aiohttp.ClientSession(loop=loop)
    with open('data/config.json') as f:
        data = json.load(f)
        app.password = data.get('password')
        app.webhook_url = data.get('webhook_url')

    await app.session.post(
        app.webhook_url, 
        json=format_embed('deploy')
        )

@app.route('/')
async def index(request):
    print(request.path)
    template = env.get_template('dashboard.html')
    return html(template.render(
            index='active',
            botname=botname
            ))

@app.route('/bot')
async def bot(request):
    template = env.get_template('bot_profile.html')
    return html(template.render(
            bot='active',
            botname=botname
            ))

@app.route('/config')
async def config(request):
    template = env.get_template('configuration.html')
    return html(template.render(
            config='active',
            botname=botname
            ))

@app.route('/commands')
async def cmds(request):
    template = env.get_template('commands.html')
    return html(template.render(
            commands='active',
            botname=botname
            ))

def format_embed(event):
    event = event.lower()
    em = discord.Embed(color=discord.Color.green())
    if event == 'update':
        em.title = event.title()
    elif event == 'deploy':
        cmd = r'git show -s HEAD~1..HEAD --format="[{}](https://github.com/cgrok/dash/commit/%H) %s (%cr)"'

        if os.name == 'posix':
            cmd = cmd.format(r'\`%h\`')
        else:
            cmd = cmd.format(r'`%h`')

        em.title = event.title()
        em.description = os.popen(cmd).read().strip()
    return {'embeds': [em.to_dict()]}

@app.route('/hooks/github', methods=['POST'])
async def upgrade(request):
    await app.session.post(
        app.webhook_url, 
        json=format_embed('update')
        )
    command = 'sh ../dash.sh'
    p = os.system(f'echo {app.password}|sudo -S {command}')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
