var express = require('express')
var fs = require('fs')
var https = require('https')
let mongoose = require('mongoose')
var ObjectId = require('mongodb').ObjectID;

var MongoClient = require('mongodb').MongoClient

let pubKeySchema = mongoose.Schema({
  chatid: String,
  pubkeyhexstr: String},
  { collection: 'publickeys' })
let pubkeys = mongoose.model('PublicKeys', pubKeySchema)

let messageSchema = mongoose.Schema({
   toid: String,
   encmessagehexstr: String,
   fromid: String},
   { collection: 'messages' })
let messages = mongoose.model('Messages', messageSchema)

var Db = require('mongodb').Db
var Server = require('mongodb').Server

var url = "mongodb://localhost:27017/chatdb"

MongoClient.connect(url, function(err, db) {
  if (err) throw err;
  console.log("Database created!");
  db.close();
});

MongoClient.connect(url, function(err, db) {
  if (err) throw err;
  var dbo = db.db("chatdb");

  dbo.createCollection("public_keys", function(err, res) {
    if (err) throw err;
    console.log("public_keys collection created");
    db.close();
  });
});

MongoClient.connect(url, function(err, db) {
  if (err) throw err;
  var dbo = db.db("chatdb");
  dbo.createCollection("messages", function(err, res) {
    if (err) throw err;
    console.log("messages collection created!");
    db.close();
  });
});


/*
 MongoClient.connect(url, function(err, db) {
   if (err) throw err;
   var dbo = db.db("chatdb");
   var testMessageObj = { toid: "testidpleaseignore", fromid: "yetanothertestidtoignore",  encmessagehexstr: "badbadbadbadbadbadbad" };

   dbo.collection("messages").insertOne(testMessageObj, function(err, res) {
     if (err) throw err;
     console.log("test message inserted!");
     db.close();
   });
 });
*/



/*
MongoClient.connect(url, function(err, db) {
    if (err) throw err;
    var dbo = db.db("chatdb");
    var testObj = { chatid: "testidpleaseignore", pubkeyhexstr: "badbadbadbadbadbadbad" };

    dbo.collection("public_keys").insertOne(testObj, function(err, res) {
      if (err) throw err;
      console.log("test pub key inserted!");


      db.close();
    });
  });

*/



function pullAllPubKeys(res) {


MongoClient.connect(url, function(err, db) {
  if (err) throw err;
  var dbo = db.db("chatdb");
  dbo.collection("public_keys").find({}, { projection: { _id: 0, chatid: 1, pubkeyhexstr: 1 } }).toArray(function(err, result) {
    if (err) throw err;
    console.log("pub keys being pulled");

    res.send(result);
    db.close();
});
});
}

   function pullAllMessagesForUser(res, user) {


   MongoClient.connect(url, function(err, db) {
     if (err) throw err;
     var dbo = db.db("chatdb");
     dbo.collection("messages").find({toid: user },
     { projection: { _id: 0, toid: 1, fromid: 1,  encmessagehexstr: 1 } }).toArray(function(err,     result) {
       if (err) throw err;
       console.log("pulling messages for " + user);

       res.send(result);
       db.close();
   });
   });
   }


//stole these shamelessly from https://steveridout.github.io/mongo-object-time/
 function getDateFromObjID(objectId) {
	return new Date(parseInt(objectId.substring(0, 8), 16) * 1000);
}

function getObjectIdStrFromDate(date) {
	return Math.floor(date.getTime() / 1000).toString(16) + "0000000000000000";
}


   function pullAllMessagesForUserAfterTimeStamp(res, user, timeInMillis) {


  MongoClient.connect(url, function(err, db) {
    if (err) throw err;
    var dbo = db.db("chatdb");
     dbo.collection("messages").find({toid: user },
     { projection: { _id: 1, toid: 1, fromid: 1,  encmessagehexstr: 1 } }).toArray(function(err,     result) {
       if (err) throw err;
	output = []

	for(var ii=0; ii <result.length; ii++) {
		if(getDateFromObjID(result[ii]["_id"] +'').getTime() > timeInMillis)
		{
		var itemtoadd = new Object();
		itemtoadd.toid = result[ii]["toid"];
		itemtoadd.fromid = result[ii]["fromid"];
		itemtoadd.encmessagehexstr = result[ii]["encmessagehexstr"];
		output.push(itemtoadd)	
		}
	}

      console.log("pulling messages after "+ timeInMillis.toString() + " for " + user);

      res.send(output);
      db.close();
  });
  });
  }

function addMessage(tochatid, fromchatid, message, restouser)
{
 MongoClient.connect(url, function(err, db) {
   if (err) throw err;
   var dbo = db.db("chatdb");
       var messageObj = { toid: tochatid, fromid: fromchatid,  encmessagehexstr:message };

dbo.collection("messages").insertOne(messageObj, function(err, res) {
       if (err)
       {
       throw err;
       res.send("fail")
       }
       console.log("Message being added from " + fromchatid +" to "+ tochatid );
       restouser.send("success")
       db.close();
     });

});

}


var  isTaken = false;

function seeIfChatIDIsTaken(chatidtopub, keystr, response)
{

 return MongoClient.connect(url, function(err, db) {
     if (err) throw err;
     var dbo = db.db("chatdb");
     //var pubKeyObj = { chatid: chatidtopub, pubkeyhexstr: keystringtopub };

 return dbo.collection("public_keys").find({chatid: chatidtopub}, { projection: { _id: 0, chatid: 1, pubkeyhexstr: 1 } }).toArray(function(err,     result) {
      if (err)
         {
          throw err;
          }
 if(result.length > 0)
  {
   console.log("id taken for " + chatidtopub);
 response.send("chatidtaken")

    db.close();
}
else
{
          console.log("Pubkey being added for " + chatidtopub );

      publishPubKey(chatidtopub, keystr, response)

db.close();

}
}

);
}
);
}

function publishPubKey(chatidtopub, keystringtopub,  restouser)
{

  MongoClient.connect(url, function(err, db) {
    if (err) throw err;
    var dbo = db.db("chatdb");
    var pubKeyObj = { chatid: chatidtopub, pubkeyhexstr: keystringtopub };



 dbo.collection("public_keys").insertOne(pubKeyObj, function(err, res) {
        if (err)
        {
        throw err;
        res.send("fail")
        }
        console.log("Pubkey being added for " + chatidtopub );
        restouser.send("success")
        db.close();
      });
      }
);
}



var app = express()

app.get('/pubkeys', function (req, res) {
  pullAllPubKeys(res)
})

app.get('/messages/:chatid', function (req, res) {
  var chatIdToCheck = req.params.chatid;
    pullAllMessagesForUser(res, chatIdToCheck)
 })

app.get('/messagesaftertime/:chatid/:time', function (req, res) {
   var chatIdToCheck = req.params.chatid;
   var timeinmillisecs = parseInt(req.params.time)
        
   if(timeinmillisecs <1700000000)
   {       res.send('[]')}
    else
    {
console.log("checking for all messages for " + chatIdToCheck + " after time " + timeinmillisecs);
     pullAllMessagesForUserAfterTimeStamp(res, chatIdToCheck,timeinmillisecs)
  }

  })

app.get('/sendmessage/:tochatid/:fromchatid/:messagetosend', function (req, res) {
    var sender = req.params.fromchatid;
    var getter = req.params.tochatid;
    var mes = req.params.messagetosend;
    addMessage(getter, sender, mes, res)
   })

app.get('/publishpubkey/:chatid/:pubkeystring', function (req, res) {
     var chatidtopub = req.params.chatid;
     var keystringtopub = req.params.pubkeystring;
     seeIfChatIDIsTaken(chatidtopub, keystringtopub, res)
})


app.get('/version', function (req, res) {
      res.send('0.1')
 })



https.createServer({
  key: fs.readFileSync('server.key'),
  cert: fs.readFileSync('server.cert')
}, app)
.listen(8080, function () {
  console.log('Your WCSBS is listening on port 8080! Go to https://localhost:8080/pubkeys to see what public keys are being posted and go to https://localhost:8080/messages to see messages get posted')
})