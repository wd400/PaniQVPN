# -*- coding: utf-8 -*-
import os
import requests
#import falcon.asgi
from blacksheep.server import Application
from blacksheep.messages import Response

from blacksheep.contents import StreamedContent
from blacksheep.server.responses import text,status_code,file,ContentDispositionType
from blacksheep.server.templating import use_templates
from jinja2 import PackageLoader
from collections import defaultdict
import string
import crypt
import secrets
import psycopg2
import uvicorn
from threading import Thread #, Lock
import hashlib
import re
import json
import time
import random
#from datetime import timezone
#from requests_tor import RequestsTor
import datetime
from stem.control import Controller
#import queue
#import sys
from concurrent.futures import ThreadPoolExecutor

import base64
from Crypto import Random
from Crypto.Cipher import AES
from CaptchaGenerator import ImageCaptcha

captchagen = ImageCaptcha()

# rt = RequestsTor(tor_ports=(9050,), tor_cport=9051, password='bE8m6WuVY8UMiJTfNfpTtQW34CbiRTTG', autochange_id=1)  # for Tor

# time.sleep(100000)


prices = {
    1:0,
    2:0.001,
    3:0.006,
    4:0.024,
    5:0.14,
    6:0.27
}

times = {
    1:60,
    2:60*24,
    3:60*24*7,
    4:60*24*31,
    5:60*24*31*6,
    6:60*24*31*12
}

BS = 16
pad = lambda s: bytes(s + (BS - len(s) % BS) * chr(BS - len(s) % BS), 'utf-8')
unpad = lambda s : s[0:-ord(s[-1:])]

class AESCipher:

    def __init__( self, key ):
        self.key = bytes(key, 'utf-8')
    


    def encrypt( self, raw ):
        raw = pad(raw)
        iv = Random.new().read( AES.block_size )
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        return base64.b64encode( iv + cipher.encrypt( raw ) )

    def decrypt( self, enc ):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        return unpad(cipher.decrypt( enc[16:] )).decode('utf8')




maxtime=max(times.values())
mintime=min(times.values())

app=Application()
view = use_templates(app, loader=PackageLoader("app", "templates"))

pool = ThreadPoolExecutor(max_workers=20)


controller = Controller.from_port()
controller.authenticate(password="bE8m6WuVY8UMiJTfNfpTtQW34CbiRTTG")

session = requests.session()

session.proxies = {}
session.proxies['http'] = 'socks5h://localhost:9050'
session.proxies['https'] = 'socks5h://localhost:9050'


useralphabet = string.ascii_letters + string.digits
passalphabet = string.punctuation + useralphabet
hexalphabet = 'abcdef0123456789'

morero_address = os.environ['MONERO_ADDRESS']
monero_host = os.environ['MONERO_HOST']

db_name=os.environ['DB_NAME']

insert_message = os.environ['INSERT_MESSAGE']
insert_message_pass = os.environ['INSERT_MESSAGE_PASS']

insert_vpnnode = os.environ['INSERT_VPNNODE']
insert_vpnnode_pass = os.environ['INSERT_VPNNODE_PASS']

select_vpnnode = os.environ['SELECT_VPNNODE']
select_vpnnode_pass = os.environ['SELECT_VPNNODE_PASS']

update_vpnnode = os.environ['UPDATE_VPNNODE']
update_vpnnode_pass = os.environ['UPDATE_VPNNODE_PASS']


insert_user = os.environ['INSERT_USER']
insert_user_pass = os.environ['INSERT_USER_PASS']

activation_user = os.environ['ACTIVATION']
activation_pass = os.environ['ACTIVATION_PASS']

transaction = os.environ['TRANSACTION']
transaction_pass = os.environ['TRANSACTION_PASS']

select_user =  os.environ['SELECT_USER']
select_user_pass =  os.environ['SELECT_USER_PASS']

clean_vpn = os.environ['CLEAN_VPN']
clean_vpn_pass = os.environ['CLEAN_VPN_PASS']

v3uripattern = re.compile("^[a-z2-7]{55}d.onion:[1-9][0-9]{3,4}$")
v2uripattern = re.compile("^[a-z2-7]{16}.onion:[1-9][0-9]{3,4}$")
#http:\\\\ \.onion
v3privkeypattern = re.compile('^[A-Z2-7]{52}$')
v2privkeypattern = re.compile('^[0-9a-zA-Z/+]{22}$')
#mutextorrc = Lock()

def randomSequence(alphabet:str,length:int):
    return ''.join(secrets.choice(alphabet) for i in range(length))

def linHash(password:str):
    return crypt.crypt(password, crypt.mksalt(crypt.METHOD_SHA512))


c = AESCipher(key=randomSequence(passalphabet, 16))

def clean_db():
    while True:
        print("clean")
        conn = psycopg2.connect(
        host='db',
        database=db_name,
        user=clean_vpn,
        password=clean_vpn_pass)
        cur = conn.cursor()
        cur.execute("SELECT url FROM vpnnodes WHERE lastseen<=(now() at time zone 'utc' ) - interval '1 hour'")
        userstodelete=cur.fetchall()
    #    for user in userstodelete:
            #todo vérifier statut retour
    #        os.system("/app/deletev2.sh "+url)
    #    if len(userstodelete) >0:
    #        os.system('/app/restart.sh')
        cur.execute('DELETE FROM vpnnodes WHERE url = ANY (%s)',(userstodelete,))
        conn.commit()
        cur.close()
        time.sleep(60)

x = Thread(target=clean_db, args=())
x.start()

def pingVPNs():
    startup=True
    while True:
        print("ping")
        conn = psycopg2.connect(
        host='db',
        database=db_name,
        user=select_vpnnode,
        password=select_vpnnode_pass)
        cur = conn.cursor()
        cur.execute('SELECT config FROM vpnnodes')
        vpnlist=cur.fetchall()
        cur.close()

        for vpn in vpnlist:
            if not startup:
                try:
                    session.get('http://'+vpn[0], headers={},timeout=120)
                except (requests.exceptions.Timeout,requests.exceptions.ConnectionError):
                    print("mort:",vpn)
                    continue
            startup=False
            print("alive:",vpn)
            conn = psycopg2.connect(
            host='db',
            database=db_name,
            user=update_vpnnode,
            password=update_vpnnode_pass)
            cur = conn.cursor()
            cur.execute("UPDATE vpnnodes SET lastseen=(now() at time zone 'utc') WHERE config=%s ",vpn)
            conn.commit()
            cur.close()
            
            time.sleep(1+secrets.randbelow(60))

        
        time.sleep(60+secrets.randbelow(60*10))

y = Thread(target=pingVPNs, args=())
y.start()


def synchronizeVpns(username:str,hashpass:str,duration:int):
    print("s1")
    conn = psycopg2.connect(
    host='db',
    database=db_name,
    user=select_vpnnode,
    password=select_vpnnode_pass)
    print("s2")
    cur = conn.cursor()
    cur.execute('SELECT config FROM vpnnodes')
    vpnlist=cur.fetchall()
    cur.close()
    conn.close()
    print("s3")
    for vpnurl in vpnlist:
        print("ajout a` ",vpnurl)
        pool.submit(requestThread,"http://"+vpnurl[0]+"/addUser.sh",
        {'user':username,'pass':hashpass,'duration':int(datetime.datetime.now().timestamp())+duration*60})


def fakeData():
    while True:
        #TODO:add timing ici
        print("add fake data")
        minutes=min(maxtime,secrets.randbelow(int(maxtime*1.1)))
        username=randomSequence(useralphabet, 20)
        hashpass=linHash(randomSequence(passalphabet, 30))

        conn = psycopg2.connect(
            host='db',
            database=db_name,
            user=insert_user,
            password=insert_user_pass)
        cur = conn.cursor()
        cur.execute("INSERT INTO users VALUES (%s,%s,interval '%s minutes' + (now() at time zone 'utc'))",(username,hashpass,minutes))
        cur.close()
        conn.commit()
        

        hash=hashlib.sha512( ("EspR!w&o26S3ZCqb6kIO4Unv7#iNh" + randomSequence(hexalphabet,64)).encode('utf-8') ).hexdigest()

        conn = psycopg2.connect(
            host='db',
            database=db_name,
            user=transaction,
            password=transaction_pass)
        cur = conn.cursor()
        cur.execute("INSERT INTO TRANSACTIONS VALUES (%s)", (hash,))
        cur.close()
        conn.commit()
        conn.close()

        synchronizeVpns(username, hashpass, minutes)
        print("fake data added")
        time.sleep(60*60*3+secrets.randbelow(60*60*24*2))

z = Thread(target=fakeData, args=())
z.start()

def initVPNConfigs():
    print("dans initconfig")
    conn = psycopg2.connect(
    host='db',
    database=db_name,
    user=select_vpnnode,
    password=select_vpnnode_pass)
    cur = conn.cursor()
    cur.execute('SELECT config,key FROM vpnnodes')
    vpnlist=cur.fetchall()
    cur.close()
    conn.close()

    for vpn in vpnlist:
        url,key=vpn
        print("init de",'HidServAuth', '{} {}'.format(url.split(':')[0],key))
        controller.set_conf('HidServAuth', '{} {}'.format(url.split(':')[0],key))

initVPNConfigs()

def requestThread(url:str,data:set):
    print("pool",url,data)

    #check if not dead
    conn = psycopg2.connect(
    host='db',
    database=db_name,
    user=select_vpnnode,
    password=select_vpnnode_pass)

    cur = conn.cursor()
    cur.execute('SELECT exists (SELECT 1 FROM vpnnodes WHERE config = %s LIMIT 1);',(url.split('/')[2],))
    result=cur.fetchone()
    cur.close()
    conn.close()
    if result[0]:
        try:
            r = session.post(url, headers={},data=data,timeout=60)
            if r.status_code!=200:
                time.sleep(1+secrets.randbelow(10))
                pool.submit(requestThread,url,data)
        except requests.exceptions.ConnectionError as e:
            time.sleep(1+secrets.randbelow(10))
            pool.submit(requestThread,url,data)

def addVPNtoDB(url:str,config:str,key:str):
    conn = psycopg2.connect(
    host='db',
    database=db_name,
    user=insert_vpnnode,
    password=insert_vpnnode_pass)
    cur = conn.cursor()
    cur.execute("INSERT INTO vpnnodes(url,config,key,lastseen) VALUES (%s,%s,%s, now() at time zone 'utc') ON CONFLICT (url) DO UPDATE SET lastseen = now() at time zone 'utc';",(url,config,key))
    conn.commit()
    cur.close()
    conn.close()

def generateCaptchaToken(solution:str):
    if len(solution)!=8:
        raise Exception('invalid solution length')
    timestamp=str(int(datetime.datetime.now().timestamp()))  
    random=randomSequence(passalphabet, 13)
    decodedtoken=random+timestamp+solution
    print(len(decodedtoken),decodedtoken)
    return c.encrypt(decodedtoken)

def returncaptchapage(template:str,msgerr:str=None):
    solution=randomSequence(useralphabet, 8)
    captchaimg="/captcha/"+randomSequence(hexalphabet, 10)+".png"
    captchagen.write(solution, "/app"+captchaimg )
    variables={'captchaimg':captchaimg,'captchakey':generateCaptchaToken(solution).decode('utf-8')}
    if msgerr:
        variables['msgerr']=msgerr
    rep=view(template,variables)
    rep.set_header(b'cache-control',b'no-cache,max-age=0,no-store,private,must-revalidate')
    return rep

@app.router.get('/getaccess')
async def access():  
    return returncaptchapage("access")
    

def returnUsers():
    conn = psycopg2.connect(
    host='db',
    database=db_name,
    user=select_user,
    password=select_user_pass)
    cur = conn.cursor()
    cur.execute('SELECT username,hash,expiration FROM users')
    users=cur.fetchall()
    cur.close()
    conn.close()
    return users

@app.router.post('/contact')
async def contact(request):   
        
        
       # raw_data = await req.get_media()
        raw_data= await request.form() 
        message=raw_data.get('message')


        if message is not None and len(message)<=500:
            conn = psycopg2.connect(
            host='db',
            database=db_name,
            user=insert_message,
            password=insert_message_pass)
            cur = conn.cursor()
            cur.execute('INSERT INTO messages VALUES (%s)',(message,))
            cur.close()
            conn.commit()
            conn.close()
            return text("ok")
        return text("fail")

def checkCaptcha(raw_data:defaultdict):
    return None
    captchakey=raw_data['captchakey']
    captcha=raw_data['captcha']

    if len(captcha)!=8:
        return "invalid captcha"
    
    if len(captchakey)!=64:
        return "invalid captcha key"

    decodedtoken=c.decrypt(captchakey)
    
    print("decodedtoken",len(decodedtoken),decodedtoken)
    if len(decodedtoken)!=31:
        return "invalid captcha key"
    timestamp=decodedtoken[13:23]
    try:
        timestamp=int(timestamp)
    except ValueError:
        return "invalid captcha key"
    print("timestamp",timestamp)
    timestampnow=int(datetime.datetime.now().timestamp())
    if timestamp>timestampnow:
        return"invalid captcha key"
    if timestampnow-timestamp>60*5:
        return "captcha expired"
    print("input",captcha)
    print("initial captcha",decodedtoken[23:])
    if decodedtoken[23:]!=captcha:
        return "invalid captcha"


def newUserpage(minutes:int):
        username=randomSequence(useralphabet, 20)
        password=randomSequence(passalphabet, 30)
        hashpass=linHash(password)
        #asynchronous
        # thread = Thread(target=synchronizeVpns, args=(username, hashpass,minutes))
        # thread.daemon = True
        # thread.start()
        synchronizeVpns(username, hashpass,minutes)
        addUserToDB(username, hashpass,minutes)

        rep=view("credentials",{'username':username,'password':password})

        rep.set_header(b'cache-control',b'no-cache,max-age=0,no-store,private,must-revalidate')
        return rep

@app.router.post('/activation')
async def activation(request):
    raw_data= await request.form()
    raw_data=defaultdict(str,raw_data)
    res=checkCaptcha(raw_data)
    if res!=None:
        return returncaptchapage("activation",res)
    
    if len(raw_data['key'])!=20:
        return returncaptchapage("activation","Invalid activation key")

    conn = psycopg2.connect(
    host='db',
    database=db_name,
    user=activation_user,
    password=activation_pass)

    cur = conn.cursor()
    cur.execute("DELETE FROM activation where key=%s RETURNING duration ", (raw_data['key'],))
    duration=cur.fetchone()
    cur.close()
    conn.commit()
    conn.close()
    if duration is None:
        return returncaptchapage("activation","Invalid activation key")
    return newUserpage(duration[0])
    #select minutes where key=raw_data['key'] limit 1

@app.router.get('/activation')
async def activation():
    return returncaptchapage("activation")


def getvpnurl():
    conn = psycopg2.connect(
    host='db',
    database=db_name,
    user=select_vpnnode,
    password=select_vpnnode_pass)
    cur = conn.cursor()
    cur.execute('SELECT url FROM vpnnodes')
    vpnlist=cur.fetchall()
    cur.close()
    conn.close()
    return '\n'.join('remote '+x[0].replace(':',' ') for x in vpnlist)


defaultconfig="""client
dev tun
proto tcp
{}
remote-random
resolv-retry infinite
nobind
socks-proxy 127.0.0.1 9150
key-direction 1
ecdh-curve p521_kyber90s1024
tls-version-min 1.3
cipher AES-256-CBC
auth SHA512
comp-lzo
verb 9
route-method exe
route-delay 2
auth-user-pass
push "dhcp-option DNS 1.1.1.1"
push "block-outside-dns"
<ca>
-----BEGIN CERTIFICATE-----
MIIFVTCCAz2gAwIBAgIUFeBiu5xoAg9DVAfnitmI4ae2QhcwDQYJKoZIhvcNAQEF
BQAwFjEUMBIGA1UEAwwLcGFuaXF2cG4gQ0EwHhcNMjEwNDI0MjIyMzIxWhcNMjIw
NDI0MjIyMzIxWjAWMRQwEgYDVQQDDAtwYW5pcXZwbiBDQTCCAiIwDQYJKoZIhvcN
AQEBBQADggIPADCCAgoCggIBAKPb/RKFox4WRaRX6Y0qmAyvFvF+rlyTs+7Bpgt0
/xqrVvZrhaQuZ6HqgeVXtTobwwfWA8+w71iSEBQFEss9iFqf2onMWAgai7ACBwHI
ZG5Jn3tZVEC0/jsRWIvGRhTPHIGbIZkgJbqx4vKvuXGX6er6tWMsZSDzTSj/Z/K/
DBxeyhCDDbv0w/QB73rcNIMV67yrUC76EfvknuysfNb3Cnab9+KxljYHZbX7V+/c
hIhqn3CpqY+4odWnpcTCpUuThz7P1aZUdwuvPQ4mjNieKkYcilzMDjpUqIRHegos
oUrtgtemsDBo6i0BTidYT9ZhBrr+0CaHx09S4d97DMrYCPNhDqnm1Qur2ur/tW/G
tZ2rTw7N88SwkpfiYUpR/943M1N4Nxs4MLGzFItAUNhkOJiE2/v3mSYJfKdykXdl
hqnsMWTZmRQSBpetAGXnIQZJ4oJMlZZWoh295D/1fzWwrYo8byn3FZ5byoqVNZAH
54X8d+hK0rGLDq7iOO/jzgAlwt2917gPxoJvc9JxJ4HeEmA9JuCUEJKKRuBqrPD4
b7edctvJeA7HIA7hXoOmA3lr6cHu7zmWadE1PYoWWE3CWpxAblm32E9hOPCBc3HI
q79RfTY9peoGx4tDkIw1PjwXjI9S0G0tGCCh1+SXEdQilo5CWLCI83nduLnUMhZM
frfDAgMBAAGjgZowgZcwHQYDVR0OBBYEFA5kKrUUxAfU4rbpLkl4Qw5j4RwTMB8G
A1UdIwQYMBaAFA5kKrUUxAfU4rbpLkl4Qw5j4RwTMA8GA1UdEwEB/wQFMAMBAf8w
DgYDVR0PAQH/BAQDAgH+MDQGA1UdJQEB/wQqMCgGCCsGAQUFBwMBBggrBgEFBQcD
AgYIKwYBBQUHAwMGCCsGAQUFBwMEMA0GCSqGSIb3DQEBBQUAA4ICAQAxOoPwd5hS
wRbtjZbJLWBEh/51OVF3JRFCWpVhXc2mRl2G5o4i/3CnxMGfqUOSnekETcgd7lPA
05lgON9WMFds1C0rVqmINIfWO+WueJSMbXSylDV5hHTK8XGplk8S1sy36UQ+Q92a
aSWJOlNZxJmMfWEwERXxf7rPE6Asua88HQGUFrm7k3e4jbxqiFq+4vE0n0Nugng0
4LFumdA44oQP6ySVnMbaKIWfpLnPdMsd7BPLPsqsiDtMbB7izkQayiOY8bF12uio
Xp7gTC9P9qontMvmlUk08VouZomRrwKFfnBjMY5iCS+MDPETisjFiunH/+mGYUaT
CNmtyR5yA1IK8c2X0hu7ORkExaW07SSTpGJgyfexJ6YStyIG6+dfVzOhBj4SHBoq
ZqUb4fQFvplJkUzyRrBG3C9afWmDruGFUhXCH1F09VqCT6iC5OZt4hV+gRzO2prJ
3zXiz08R0g28eral1YgflW8sc8BHvTPQXBP43ZATotiQVSwddSGyw1IfHj7jbXoI
p+47ixdZMRL6FUFoIF7gQik9qS8xCJhlY31iJNp3uhi1wZAQD+EV3cF25hdCLIIE
rR64KDGHmKFhIvbILCuuFn/qPQS/4OUUCTRFUMfUFVhcqJycCVoooLyJbMVHd5A4
cL/2niDAM7qPwMAR4tceSjUHswNS0guzJA==
-----END CERTIFICATE-----
</ca>
<tls-auth>
-----BEGIN OpenVPN Static key V1-----
db66c0f9a8c2f0f9361b1558d72073b4
d117a0dcb7c4b64e06a93efdf77aafdd
01c51f04a13cb76832dd64ee69585e96
360487db75f343739edd86d3e9cd3f57
ac4a8b13378ff528508fb1f755223445
4efcf901a176f504906d2aa84d94f7ae
2c2d5f76bb688bc91d38574c60dc877b
49717dc18a1d7476e84afc265a482aec
da4e1fc77b3875d802707a1f42b18944
2ee7381df43205402df07e2816e249a4
d3655656095400fa2bc9129c3974d023
d8d25e35ba6a669dd097dd2e288dcadf
44cf8e3452e3244e578bcd4ee170f6ca
119d82555d71e7f3e5850440e8dc5f43
8c9c504df8f24dceed4ecca59003cf79
e3f684e7b6ddf3acc95020aa46a2b5cb
-----END OpenVPN Static key V1-----
</tls-auth>
"""

def windowsprovider():
        return defaultconfig.format(getvpnurl())

def linuxprovider():
    return windowsprovider() +  "\nuser nobody\ngroup nogroup"

    

@app.router.get('/linconf.config')
async def linconf():    
    return text(linuxprovider())



@app.router.get('/winconf.config')
async def winconf():
    return text(windowsprovider())


# @app.router.get('/howto')
# async def winconf():
#     return view("howto",{{lastupdate}})


# class UpdateVPN:
#     async def on_post(self, req, resp):
@app.router.post('/updatevpn')
async def updatevpn(request):
        """ handles post requests"""
       # raw_data = await req.get_media()
        raw_data= await request.form()
        if raw_data['vpn'] is not None and raw_data['config'] is not None and raw_data['key'] is not None:
            if re.match(v3uripattern,raw_data['vpn']) and re.match(v2uripattern,raw_data['config']) and re.match(v2privkeypattern,raw_data['key']):
                

                print("iciiiiiiiiiii")
                # mutextorrc.acquire()
                # print("lancement addv2")
                # print("/app/addv2.sh '"+raw_data['config'].split(':')[0]+"' '"+raw_data['key']+"'")
                # ret=os.system("/app/addv2.sh '"+raw_data['config'].split(':')[0]+"' '"+raw_data['key']+"'")
                # print("fin addv2")
                # if ret!=0:
                #     print("error during add")

                # ret=os.system('/app/restart.sh')
                # mutextorrc.release()
                # if ret !=0:
                #     print("error during restart")
                #v2
                print('HidServAuth', '{} {}'.format(raw_data['config'].split(':')[0],raw_data['key']))
                controller.set_conf('HidServAuth', '{} {}'.format(raw_data['config'].split(':')[0],raw_data['key']))
                print('done')
                #todo:check if good status



                addVPNtoDB(raw_data['vpn'],raw_data['config'],raw_data['key'])

                print("ok")
                #resp.content_type = falcon.MEDIA_TEXT
                
                users=returnUsers()
                random.shuffle(users)
                return text('\n'.join(x[0]+' '+x[1]+' '+str(int(x[2].timestamp())) for x in users))

        #resp.status = falcon.HTTP_400
        return status_code(400)

def addUserToDB(username:str,hashpass:str,duration:int):
    conn = psycopg2.connect(
    host='db',
    database=db_name,
    user=insert_user,
    password=insert_user_pass)
    cur = conn.cursor()
    cur.execute("INSERT INTO users VALUES (%s,%s,interval '%s minutes' + (now() at time zone 'utc'))",(username,hashpass,duration))
    conn.commit()
    cur.close()
    conn.close()

def is_hex(test:str,l:int):
    if len(test)!=l:
        return False
    for letter in test:
        if not ('a'<= letter <='f' or '0'<=letter<='9'):
            return False
    return True

@app.router.post('/getaccess')
async def getaccess(request):
        """ handles post requests"""
       # raw_data = await req.get_media()
        raw_data= await request.form()
        raw_data=defaultdict(str,raw_data)

        #check captcha
        res=checkCaptcha(raw_data)
        if res!=None:
            return returncaptchapage("access",res)

        duration = raw_data.get("duration")
        if duration is None:
            return returncaptchapage("access","invalid duration")


        if len(duration)!=1:
            return returncaptchapage("access","invalid duration")

        try:
            duration=int(duration)
        except ValueError:
            return returncaptchapage("access","invalid duration")

        if duration>6 or duration<1:
            return returncaptchapage("access","invalid duration")
        


        #il faut payer
        if duration>1:
            topay=prices[duration]

            trID=raw_data.get("trID")
            if not is_hex(trID,64):
                return returncaptchapage("access","the transaction ID is not a hexadecimal string of length 64")
            
            trKey=raw_data.get("trKey")
            if not is_hex(trKey,64):
                return returncaptchapage("access","the transaction key is not a hexadecimal string of length 64")
            


            # simplewallet' procedure/method to call
            rpc_input = {
                "method": "check_tx_key",
                "params": {"txid": txid,"tx_key":tx_key,"address":morero_address}
            }

            # add standard rpc values
            rpc_input.update({"jsonrpc": "2.0", "id": "0"})

            # execute the rpc request
            response = requests.post(
                "http://"+monero_host+"/json_rpc",
                data=json.dumps(rpc_input),
                headers={'content-type': 'application/json'})
            response=response.json()
            if "result" in response.keys():
                res = response["result"]
                received=res["received"]
                if res["in_pool"]!="true":
                    return returncaptchapage("access","the transaction is not in the pool")
                if res["received"]!=topay:
                    return returncaptchapage("access","bad amount")
                if res["confirmations"]<10:
                    return returncaptchapage("access","not enough confirmations, please wait a few minutes and retry")
            else:
                return returncaptchapage("access","internal error please contact us")

            #todo stocker le salt ailleurs
            hash=hashlib.sha512( ("EspR!w&o26S3ZCqb6kIO4Unv7#iNh" + data['trID']).encode('utf-8') ).hexdigest()

            conn = psycopg2.connect(
            host='db',
            database=db_name,
            user=transaction,
            password=transaction_pass)

            cur = conn.cursor()
            cur.execute("select 1 from TRANSACTIONS where hash=%s", (hash,))
        
            if cur.rowcount>0:
                return returncaptchapage("access","Transaction already Used")
            cur.execute("INSERT INTO TRANSACTIONS VALUES (%s)", (hash,))
            cur.close()
            conn.commit()
            conn.close()

        return newUserpage(times[duration])

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, log_level="info")