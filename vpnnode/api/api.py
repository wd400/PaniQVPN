import os
#import shutil
import re
#import string
#import socket
import secrets
import requests
from requests_tor import RequestsTor
import time
#import sys
#import json
from stem.control import Controller


# useralphabet = string.ascii_letters + string.digits
# passalphabet = string.punctuation + useralphabet

weburl = os.environ['WEBURL']

# session = requests.session()
# session.proxies = {}
# session.proxies['http'] = 'socks5h://localhost:9050'
# session.proxies['https'] = 'socks5h://localhost:9050'


rt = RequestsTor(tor_ports=(9050,), tor_cport=9051,password='bE8m6WuVY8UMiJTfNfwTtQW34CbiRTTG')# , autochange_id=1  # for Tor


userregex = re.compile(r"^[A-Za-z0-9]{20}$")
passregex = re.compile(r"^\$6\$[A-Za-z0-9\\.\/]{16}\$[A-Za-z0-9\\.\/]{86}$")
expregex = re.compile(r"^[1-9][0-9]{9,10}$")


#def urlencode(string: str):
#    return urllib.parse.quote(string)


def addUser(username: str, password: str, expiration: str):
    if not re.match(userregex, username):
        print("invalid username: ", username)
        return
    if not re.match(passregex, password):
        print("invalid password: ", password)
        return
    if not re.match(expregex, expiration):
        print("invalid expiration: ", expiration)
        return
   # ret=os.system("/tmp/addUser.sh '"+ username + "' '" + password+"' '"+expiration+"'")
    r = requests.post("http://175.18.18.12:8080/addUser.sh",
                      data={'user': username, 'pass': password, 'duration': expiration})
 #   print("response openvpn", r, r.text,file = sys.stderr)
    # todo: boucler
    print("user added")


# @app.route('/addUser',methods = ['POST'])
# def index():
#     print("on veut ajouter un user!")
#     print(request,request.form,file = sys.stderr)
#     username = request.form.get('username')
#     password = request.form.get('hashpass')
#     duration = request.form.get('duration')
#  #   print("route:",username,type(username),password,type(password),expiration,type(expiration))
#     addUser(username, password, duration)
#     return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 


print("done@")

with Controller.from_port(address='173.18.18.10', port=9051) as controller:
    controller.authenticate(password='QbqLsuvnXMEQJzqu8FzVkYx5')
    print("Tor is running version %s" % controller.get_version())

    confport = 1024+secrets.randbelow(49151+1)
    vpnport = confport
    while vpnport == confport:
        vpnport = 1024+secrets.randbelow(49151+1)

    confport = 7777
    vpnport = 8888
    # vpn
    responsevpn = controller.create_ephemeral_hidden_service(
        {vpnport: '174.18.18.12:1194'},
        #   key_type='NEW',
        key_content='ED25519-V3',
        await_publication=True
    )

    responseconf = controller.create_ephemeral_hidden_service(
        {confport: '174.18.18.12:8080'},
     #   {confport: '173.18.18.11:5000'},
        #  key_type='NEW',
        key_content='RSA1024',
        #   key_content = 'ED25519-V3',
        await_publication=True,
        basic_auth={
            '1': None
        },
        # max_streams=1,
        # discard_key=True
    )

    data = {'vpn': responsevpn.service_id+".onion:" +
            str(vpnport), 'config': responseconf.service_id+".onion:"+str(confport), 'key': responseconf.client_auth['1']}
    print("data", data)

    while True:
        try:
            r = rt.post('http://'+weburl+'/updatevpn', data=data, headers={})
        except requests.exceptions.ConnectionError:
            print("web down?")
            time.sleep(60+secrets.randbelow(60*10))
            continue

        if r.status_code == 200:
            lines = r.text.split('\n')
            print("lines", lines)
            if lines != ['']:
                for line in lines:
                    print("line", line)
                    username, pwd, expiration = line.split()
                    addUser(username, pwd, expiration)
            time.sleep(60*60*6+secrets.randbelow(60*60*24))


        time.sleep(60+secrets.randbelow(60*5))



    # try:
    #     app.run(host='0.0.0.0')
    # finally:
    #     # Shut down the hidden service and clean it off disk. Note that you *don't*
    #     # want to delete the hidden service directory if you'd like to have this
    #     # same *.onion address in the future.

    #     print(" * Shutting down our hidden service")
    #     controller.remove_hidden_service(hidden_service_dir)
    #     shutil.rmtree(hidden_service_dir)
