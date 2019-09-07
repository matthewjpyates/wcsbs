import os
import re
import sys
import time
import socket


license = """
Copyright 2019 Matthew J P Yates

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


<!--Begin trust tree-->
This is my first node.js or mongo db thingy. Its also my first ever deployable server script.
You probably should not use any of this code for anything high end or remotly concidered production.
Mostly I wanted to get a way for people to use end to end chat encrypted apps without having to rely on google, aws, firebase, or whowever as a backend.
<!--End trust tree-->
"""


help_text = """

This script will deploy a Werewolf Chat Simple Backend Server (WCSBS).
You need python3, node.js, npm, and mongodb already installed.
This definitly works on ubunut 18.04, it probably will have issues on non linux systems.
You probably will also need to run this either as root or with sudo.

-y or --assumeyes will autoanswer the configuration for you

-v or --version will show you the version of the script

-h or --help will show you the help dialog, which you must already know because you are reading the help dialog



"""

version = "0.1"

current_milli_time = lambda: int(round(time.time() * 1000))


def check_args():
    if len(sys.argv) > 1:
        str_to_test = str(sys.argv[1])
        str_to_test = str_to_test.lower()
        if(str_to_test == "-y" or str_to_test == "--assumeyes"):
            return True
        if(str_to_test == "-v" or str_to_test == "--version"):
             print("Version is " + version)
             sys.exit()
        if(str_to_test == "-l" or str_to_test == "--license"):
              print(license)
              sys.exit()
        if(str_to_test == "-h" or str_to_test == "--help"):
              print(help_text)
              sys.exit()

    return False

def check_for_yes_no(input_from_user):
    input_str = str(input_from_user)
    input_str = input_str.lower()
    return input_str == "yes" or input_str == "no" or input_str == "y" or input_str == "n"

def get_user_choice(str_to_ask, empty_result):
    try:
        ans_from_user = input(str_to_ask)
        if not ans_from_user:
            return empty_result
    except SyntaxError:
        ans_from_user = None
    if ans_from_user is None:
        return empty_result
    while (not check_for_yes_no(ans_from_user)):
        print("Sorry I could not read that, please use Y, N, Yes, or No (case insensitive)")
        try:
            ans_from_user = input(str_to_ask)
            if not ans_from_user:
                return empty_result
        except SyntaxError:
            ans_from_user = None
        if ans_from_user is None:
            return empty_result
    str_to_check = str(ans_from_user)
    str_to_check = str_to_check.lower()
    return str_to_check == "y" or str_to_check == "yes"


def get_input_from_user(str_to_ask):
    try:
        input_to_return = str(input(str_to_ask))
    except SyntaxError:
        input_to_return = None
    while input_to_return is None:
        try:
            input_to_return = str(input(str_to_ask))
        except SyntaxError:
            input_to_return = None
    return input_to_return


def check_for_port_numbers(input_str):
    try:
        val = int(input_str)
        return val >0 and val < 65536
    except ValueError:
        print("Not a number")
        return False

defaults_for_everything = check_args()

if defaults_for_everything:
    print("going to skip all user input and options, good for testing, probably bad for production, but I am not your boss")


print("Welcome to the Werewolf Chat Simple Backend Server (WCSBS) Installer Script")

print("This script will allow you to run your own private end-to-end post-quantum encryption chat server")

print("installing express with npm, if you dont have npm this will fail")
os.system("npm install -g express-generator")
os.system("npm install mongoose body-parser --save")
os.system("npm install express --save")
os.system("npm install mongodb --save")
os.system("service mongod start")


print("here is some ip information if you are testing")
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
print("Your Computer Name is:" + hostname)
print("Your Computer IP Address is:" + IPAddr)

print("here is some timing information")
print("the time in milliseconds is " + str(current_milli_time()) + " just in case you are testing querying by time")
print("")
print("now lets make some https certs or use some you already have")

if defaults_for_everything:
    os.system("openssl req -nodes -new  -x509 -keyout server.key -out server.cert -subj \"/C=US/ST=Denial/L=Springfield/O=Dis/CN=www.example.com\"")
    server_key_path = "server.key"
    server_cert_path = "server.cert"
else:
    wants_self_signed = get_user_choice("Do you want generate self signed certs? [Y/n]", True)

    if wants_self_signed:
        print("using openssl to gen a key and cert")
        os.system("openssl req -nodes -new  -x509 -keyout server.key -out server.cert")
        server_key_path = "server.key"
        server_cert_path = "server.cert"
    else:
        server_key_path = get_input_from_user("What is the path to your server's key file")
        server_cert_path = get_input_from_user("What is the path to your server's cert file")

if defaults_for_everything:
    port_num = "8080"

else:
    print("Need a port to listen on, please make sure that your firewall will allow inbound connections for the port you pick")
    port_num = get_input_from_user("What port do you want to listen on? (from 1 to 65535) [8080] ")
    if not port_num:
        port_num = "8080"
    while(not check_for_port_numbers(port_num)):
        print("sorry could not use "+port_num+" as a listening port")
        port_num = get_input_from_user("What port do you want to listen on? (from 1 to 65535) [8080]")
        if not port_num:
            port_num = "8080"

if defaults_for_everything:
    server_passcode = ""
else:
    print("for a little extra privacy and to prevent your serer from being flooded you can add a passcode")
    print("you will need to distrbute it yourself and it will only take alphanumeric chars")
    try:
        server_passcode = input("Enter your server's passcode or simply press enter to have none")
        server_passcode = re.sub(r'\W+', '', server_passcode)
        print("your passcode is "+server_passcode)
        if server_passcode:
            server_passcode = server_passcode + "/"
    except SyntaxError:
        server_passcode = ""
        print("no passcode submitted or something else weird happended")


print("writing app.js now...")

config_str = '''\
var express = require('express')
var fs = require('fs')
var https = require('https')
let mongoose = require('mongoose')
var ObjectId = require('mongodb').ObjectID;

var MongoClient = require('mongodb').MongoClient

let pubKeySchema = mongoose.Schema({{
  chatid: String,
  pubkeyhexstr: String}},
  {{ collection: 'publickeys' }})
let pubkeys = mongoose.model('PublicKeys', pubKeySchema)

let messageSchema = mongoose.Schema({{
   toid: String,
   encmessagehexstr: String,
   fromid: String}},
   {{ collection: 'messages' }})
let messages = mongoose.model('Messages', messageSchema)

var Db = require('mongodb').Db
var Server = require('mongodb').Server

var url = "mongodb://localhost:27017/chatdb"

MongoClient.connect(url, function(err, db) {{
  if (err) throw err;
  console.log("Database created!");
  db.close();
}});

MongoClient.connect(url, function(err, db) {{
  if (err) throw err;
  var dbo = db.db("chatdb");

  dbo.createCollection("public_keys", function(err, res) {{
    if (err) throw err;
    console.log("public_keys collection created");
    db.close();
  }});
}});

MongoClient.connect(url, function(err, db) {{
  if (err) throw err;
  var dbo = db.db("chatdb");
  dbo.createCollection("messages", function(err, res) {{
    if (err) throw err;
    console.log("messages collection created!");
    db.close();
  }});
}});

 MongoClient.connect(url, function(err, db) {{
   if (err) throw err;
   var dbo = db.db("chatdb");
   var testMessageObj = {{ toid: "testidpleaseignore", fromid: "yetanothertestidtoignore",  encmessagehexstr: "badbadbadbadbadbadbad" }};

   dbo.collection("messages").insertOne(testMessageObj, function(err, res) {{
     if (err) throw err;
     console.log("test message inserted!");
     db.close();
   }});
 }});



MongoClient.connect(url, function(err, db) {{
    if (err) throw err;
    var dbo = db.db("chatdb");
    var testObj = {{ chatid: "testidpleaseignore", pubkeyhexstr: "badbadbadbadbadbadbad" }};

    dbo.collection("public_keys").insertOne(testObj, function(err, res) {{
      if (err) throw err;
      console.log("test pub key inserted!");


      db.close();
    }});
  }});





function pullAllPubKeys(res) {{


MongoClient.connect(url, function(err, db) {{
  if (err) throw err;
  var dbo = db.db("chatdb");
  dbo.collection("public_keys").find({{}}, {{ projection: {{ _id: 0, chatid: 1, pubkeyhexstr: 1 }} }}).toArray(function(err, result) {{
    if (err) throw err;
    console.log("pub keys being pulled");

    res.send(result);
    db.close();
}});
}});
}}

   function pullAllMessagesForUser(res, user) {{


   MongoClient.connect(url, function(err, db) {{
     if (err) throw err;
     var dbo = db.db("chatdb");
     dbo.collection("messages").find({{toid: user }},
     {{ projection: {{ _id: 0, toid: 1, fromid: 1,  encmessagehexstr: 1 }} }}).toArray(function(err,     result) {{
       if (err) throw err;
       console.log("pulling messages for " + user);

       res.send(result);
       db.close();
   }});
   }});
   }}


//stole these shamelessly from https://steveridout.github.io/mongo-object-time/
 function getDateFromObjID(objectId) {{
	return new Date(parseInt(objectId.substring(0, 8), 16) * 1000);
}}

function getObjectIdStrFromDate(date) {{
	return Math.floor(date.getTime() / 1000).toString(16) + "0000000000000000";
}}


   function pullAllMessagesForUserAfterTimeStamp(res, user, timeInMillis) {{


  MongoClient.connect(url, function(err, db) {{
    if (err) throw err;
    var dbo = db.db("chatdb");
    dbo.collection("messages").find({{ $and: [ {{_id: {{$gt: ObjectId(getObjectIdStrFromDate(new Date(timeInMillis))) }} }},
    {{toid: user }}] }},
    {{ projection: {{ _id: 0, toid: 1, fromid: 1,  encmessagehexstr: 1 }} }}).toArray(function(err,     result) {{
      if (err) throw err;
      console.log("pulling messages after "+ timeInMillis.toString() + " for " + user);

      res.send(result);
      db.close();
  }});
  }});
  }}

function addMessage(tochatid, fromchatid, message, restouser)
{{
 MongoClient.connect(url, function(err, db) {{
   if (err) throw err;
   var dbo = db.db("chatdb");
       var messageObj = {{ toid: tochatid, fromid: fromchatid,  encmessagehexstr:message }};

dbo.collection("messages").insertOne(messageObj, function(err, res) {{
       if (err)
       {{
       throw err;
       res.send("fail")
       }}
       console.log("Message being added from " + fromchatid +" to "+ tochatid );
       restouser.send("success")
       db.close();
     }});

}});

}}


var  isTaken = false;

function seeIfChatIDIsTaken(chatidtopub, keystr, response)
{{

 return MongoClient.connect(url, function(err, db) {{
     if (err) throw err;
     var dbo = db.db("chatdb");
     //var pubKeyObj = {{ chatid: chatidtopub, pubkeyhexstr: keystringtopub }};

 return dbo.collection("public_keys").find({{chatid: chatidtopub}}, {{ projection: {{ _id: 0, chatid: 1, pubkeyhexstr: 1 }} }}).toArray(function(err,     result) {{
      if (err)
         {{
          throw err;
          }}
 if(result.length > 0)
  {{
   console.log("id taken for " + chatidtopub);
 response.send("chatidtaken")

    db.close();
}}
else
{{
          console.log("Pubkey being added for " + chatidtopub );

      publishPubKey(chatidtopub, keystr, response)

db.close();

}}
}}

);
}}
);
}}

function publishPubKey(chatidtopub, keystringtopub,  restouser)
{{

  MongoClient.connect(url, function(err, db) {{
    if (err) throw err;
    var dbo = db.db("chatdb");
    var pubKeyObj = {{ chatid: chatidtopub, pubkeyhexstr: keystringtopub }};



 dbo.collection("public_keys").insertOne(pubKeyObj, function(err, res) {{
        if (err)
        {{
        throw err;
        res.send("fail")
        }}
        console.log("Pubkey being added for " + chatidtopub );
        restouser.send("success")
        db.close();
      }});
      }}
);
}}



var app = express()

app.get('/{pc}pubkeys', function (req, res) {{
  pullAllPubKeys(res)
}})

app.get('/{pc}messages/:chatid', function (req, res) {{
  var chatIdToCheck = req.params.chatid;
    pullAllMessagesForUser(res, chatIdToCheck)
 }})

app.get('/{pc}messagesaftertime/:chatid/:time', function (req, res) {{
   var chatIdToCheck = req.params.chatid;
   var timeinmillisecs = parseInt(req.params.time)
   if(timeinmillisecs <1567322250000)
   {{       res.send('[]')}}
    else
    {{

     pullAllMessagesForUserAfterTimeStamp(res, chatIdToCheck,timeinmillisecs)
  }}

  }})

app.get('/{pc}sendmessage/:tochatid/:fromchatid/:messagetosend', function (req, res) {{
    var sender = req.params.fromchatid;
    var getter = req.params.tochatid;
    var mes = req.params.messagetosend;
    addMessage(getter, sender, mes, res)
   }})

app.get('/{pc}publishpubkey/:chatid/:pubkeystring', function (req, res) {{
     var chatidtopub = req.params.chatid;
     var keystringtopub = req.params.pubkeystring;
     seeIfChatIDIsTaken(chatidtopub, keystringtopub, res)
}})


app.get('/{pc}version', function (req, res) {{
      res.send('{ver}')
 }})



https.createServer({{
  key: fs.readFileSync('{sk}'),
  cert: fs.readFileSync('{sc}')
}}, app)
.listen({listenport}, function () {{
  console.log('Your WCSBS is listening on port {listenport}! Go to https://localhost:{listenport}/{pc}pubkeys to see what public keys are being posted and go to https://localhost:{listenport}/{pc}messages to see messages get posted')
}})'''.format(pc = server_passcode, sk = server_key_path, sc = server_cert_path,  listenport = port_num, ver = version)

index_file = open('app.js', 'w')
index_file.write(config_str)
index_file.close()
print("all done, you are now running a WCSBS on " + port_num)

os.system("node app.js")


