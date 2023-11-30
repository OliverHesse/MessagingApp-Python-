from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room
import sqlite3
import json
import os
import bcrypt

app = Flask(__name__)
app.secret_key = os.environ['Flask_Key']
socketio = SocketIO(app)
onlineUsers = []


def HashPassword(password, salt):
  bytes = password.encode("utf-8")
  hash = bcrypt.hashpw(bytes,
                       salt + os.environ["Flask_Pepper"].encode("utf-8"))
  return hash


def get_db_connection():
  conn = sqlite3.connect('database.db')
  conn.row_factory = sqlite3.Row
  return conn


def get_db_connection2():
  conn = sqlite3.connect('database.db')
  return conn


@app.route("/logOut")
def logOut():
  if "Username" in session:
    session.pop("Username")
    session.pop("UserID")
  return redirect(url_for("login_page", data=""))


#all the webpage functions
@app.route('/')
def index():
  if "Username" in session:

    return redirect(url_for("main_page"))
  else:
    return redirect(url_for('login_page', data=""))


@app.route("/addFriend")
def addFriend():
  if "Username" in session:

    return render_template("addFriendPage.html")
  else:
    return redirect(url_for('login_page', data=""))


@app.route("/profile")
def profile():
  if "Username" in session:
    return render_template("profile.html")
  else:
    return redirect(url_for('login_page', data=""))


@app.route('/signUp', methods=["POST", "GET"])
def signUp():
  if request.method == "GET":
    if "Username" in session:
      return redirect(url_for("index"))

    return render_template("signUp.html", data="")
  else:
    if "Username" not in session:
      #check if they left blanks
      if request.form["Username"] == "" or request.form["Password"] == "":
        return render_template(
          "signUp.html", data="Username and password cannot be left blank")
      else:
        salt = bcrypt.gensalt()
        hashed = HashPassword(request.form["Password"], salt)
        conn = get_db_connection2()
        conn.execute(
          "INSERT INTO UserData (Username,HashedPassword,Salt) VALUES ((?),(?),(?))",
          (request.form["Username"], hashed, salt))
        conn.commit()
        conn.close()
        #now get info for session
        conn = get_db_connection()
        User = conn.execute(
          'SELECT UserID,Username,HashedPassword,Salt FROM UserData WHERE Username = (?)',
          (request.form["Username"], )).fetchall()
        conn.close()
        if User:
          session["Username"] = User[0]["Username"]
          session["UserID"] = User[0]["UserID"]
          return redirect(url_for("index"))


@app.route("/addToGroup")
def addToGroup():
  if "Username" in session and request.method == "GET":
    return render_template("addUserToGroup.html")
  elif request.method == "GET":
    return redirect(url_for("login_page", data=""))


@app.route("/CreateGroupChat", methods=["POST", "GET"])
def CreateGroupChat():
  if "Username" in session and request.method == "GET":
    return render_template("CreateGroupChat.html")
  elif request.method == "GET":
    return redirect(url_for("login_page", data=""))
  elif request.method == "POST" and "Username" in session:
    print("test")
    conn = get_db_connection2()
    doesGroupExist = conn.execute("SELECT GroupChatName From GroupChatData Where GroupChatName = (?)",(request.form["GroupChatName"],)).fetchall()
    conn.close()
    if doesGroupExist:
      pass
    else:
      conn = get_db_connection()
      returnData = conn.execute("INSERT INTO GroupChatData (GroupChatName,creator) VALUES (?,?)",(request.form["GroupChatName"],session["UserID"]))
      conn.commit()
      returnData = conn.execute("INSERT INTO GroupChatUsers (GroupChatName,UserID,UserName) VALUES (?,?,?)",(request.form["GroupChatName"],session["UserID"],session["Username"]))
      conn.commit()
      conn.close()
      
      return redirect(url_for("main_page"))
@app.route("/login", methods=["POST", "GET"])
def login_page():
  if request.method == "GET":
    if "Username" not in session:
      return render_template("login.html", data="")
    return redirect(url_for("index"))
  else:

    if "Username" not in session:
      data_user = request.form["Username"]

      conn = get_db_connection()
      User = conn.execute(
        'SELECT UserID,Username,HashedPassword,Salt FROM UserData WHERE Username = (?)',
        (data_user, )).fetchall()
      conn.close()

      if User:
        hash = HashPassword(request.form["Password"], User[0]["Salt"])
        if User[0]["HashedPassword"] == hash:
          #session["Username"] = request.form["Username"]
          session["Username"] = User[0]["Username"]
          session["UserID"] = User[0]["UserID"]
          #join_room(session["Username"])
          return redirect(url_for("index"))
        else:
          return render_template('login.html', data="password incorrect")
      else:
        return render_template('login.html', data="User Doesnt Exist")
    else:
      return redirect(url_for("index"))


@app.route("/main")
def main_page():
  if "Username" in session:
    return render_template("MainPage.html")
  else:
    return redirect(url_for('login_page', data=""))


#all the websocket functions

@socketio.on("addToGroup")
def addToGroup(data):
  pass

@socketio.on("getFriends")
def getFriends(data):
  getFriends
@socketio.on("getUsers")
def returnUsers(data):
  if "Username" in session:
    #first check if username exists
    conn = get_db_connection2()

    Users = conn.execute(
      'SELECT Username,UserID FROM UserData WHERE Username LIKE (?) AND Username != (?) ORDER BY Username ASC LIMIT (?) OFFSET (?)   ',
      (data["filter"] + "%", session["Username"], 5,
       data["currentRow"])).fetchall()
    conn.close()
    conn = get_db_connection2()
    friendStatus = conn.execute(
      "SELECT User1ID,User2ID,Status FROM FriendsTable").fetchall()
    conn.close()

    if Users:

      UserData = []
      for user in Users:

        conn = get_db_connection2()
        friendStatus = conn.execute(
          "SELECT User1ID,User2ID,Status FROM FriendsTable WHERE (User1ID = (?) AND User2ID = (?) OR (User1ID = (?) AND User2ID = (?)))",
          (session["UserID"], user[1], user[1], session["UserID"])).fetchall()
        conn.close()

        if friendStatus:

          if friendStatus[0][0] == session["UserID"] and friendStatus[0][
              2] == "pending":
            #the sesisonHolder has already sent a request to this user
            UserData.append([user[0], "already sent"])
          elif friendStatus[0][1] == session["UserID"] and friendStatus[0][
              2] == "pending":
            #the session holder is recieving a frind request from this user
            UserData.append([user[0], "pending"])
          if friendStatus[0][2] == "accepted":
            #the session holder and user are already friends
            UserData.append([user[0], "accepted"])
        else:
          #no relationship found
          UserData.append([user[0], "none"])

      return {"error": "none", "data": UserData}

    else:
      return {"error": "No User Found", "data": "none"}


@socketio.on("retrieveMessages")
def returnMessages(data):
  if "Username" in session:
    conn = get_db_connection2()
    otherUserID = conn.execute(
      "SELECT UserID FROM UserData WHERE Username = (?)",
      (data["otherUser"], )).fetchall()[0][0]
    conn.close()
    if otherUserID:
      maxMessages = 30

      conn = get_db_connection2()
      messages = conn.execute(
        'SELECT SenderID,messageContent,messageTimeStamp FROM MessageTable WHERE (SenderID = (?) AND ReceiverID = (?)) OR (SenderID = (?) AND ReceiverID = (?)) ORDER BY messageTimeStamp ASC',
        (session["UserID"], otherUserID, otherUserID,
         session["UserID"])).fetchall()
      conn.close()

      if messages:
        return {
          "error": "none",
          "refID": {
            session["UserID"]: session["Username"],
            otherUserID: data["otherUser"]
          },
          "messages": messages,
          "messagesRetreived": len(messages)
        }
      else:
        return {
          "error": "noMessage",
          "messages": "none",
          "messagesRetreived": 0
        }

@socketio.on("retrieveGroupMessages")
def retrieveGroupMessages(data):
  print("this is a test")
  if "Username" in session:
    conn = get_db_connection2()
    otherUserID = conn.execute(
      "SELECT GroupChatID FROM GroupChatData WHERE GroupChatName = (?)",
      (data["otherUser"], )).fetchall()[0][0]
    conn.close()
    print(otherUserID)
    if otherUserID:
      maxMessages = 30

      conn = get_db_connection2()
      messages = conn.execute(
        'SELECT SenderID,Message,ChatTimeStamp FROM GroupChatMessages WHERE GroupChatID = (?) ORDER BY ChatTimeStamp ASC',
        (otherUserID,)).fetchall()
      conn.close()
      print("test")
      if messages:
        print(messages)
        return {
          "error": "none",
          "refID": {
            session["UserID"]: session["Username"],
            otherUserID: data["otherUser"]
          },
          "messages": messages,
          "messagesRetreived": len(messages)
        }
      else:
        return {
          "error": "noMessage",
          "messages": "none",
          "messagesRetreived": 0
        }
 
@socketio.on("connectEcho")
def echo(data):
  print(f"echo: {data['data']}")
  if "Username" in session:
    print(f"this was sent by {session['Username']}")
  else:
    pass


@socketio.on("connect")
def connect(auth):
  if "Username" in session:
    join_room(session["Username"])


@socketio.on("message")
def handleMessage(data):

  if data["Target"] in onlineUsers:
    socketio.emit(data["message"], {'sender': data["sender"]},
                  to=data["Target"])
    socketio.emit(data["message"], {'sender': data["sender"]},
                  to=data["sender"])
  else:
    socketio.emit(data["message"], {'sender': data["sender"]},
                  to=data["sender"])


  #save message to db
@socketio.on("getFriendsAndGroup")
def getFriendsAndGroup(data):
  if "Username" in session:
    dataList = {"Groups": [],"Friends":[]}
    conn = get_db_connection2()
    Groups = conn.execute("SELECT GroupChatName FROM GroupChatUsers WHERE (UserID = (?))",(session["UserID"],)).fetchall()
    conn.close()
    if Groups:
      print(Groups)
      for each in Groups:
        dataList["Groups"].append(each[0])
      print(dataList)

    
    conn = get_db_connection2()
    Friends = conn.execute(
      'SELECT * FROM FriendsTable WHERE (User1ID = (?) Or User2ID = (?)) AND Status = (?)',
      (session["UserID"], session["UserID"], "accepted")).fetchall()

    conn.close()
    if Friends:
      

      for friendRow in Friends:

        User = None
        if friendRow[1] == session["UserID"]:
          conn = get_db_connection2()
          User = conn.execute(
            'SELECT Username FROM UserData WHERE UserID = (?)',
            (friendRow[2], )).fetchall()
          conn.close()

        if friendRow[2] == session["UserID"]:
          conn = get_db_connection()
          User = conn.execute(
            'SELECT Username FROM UserData WHERE UserID = (?)',
            (friendRow[1], )).fetchall()
          conn.close()

        if User:

          dataList["Friends"].append(User[0][0])
      print(dataList)
      return {"error": 1, "friends": dataList}
    elif Groups:
      return {"error": 1, "friends": dataList}
    else:
      return {"error": 2, "friends": ""}
    return {"error": 3, "freinds": ""}
  else:
    return {"error": "must be logged in"}


@socketio.on("sendMessage")
def sendMessage(data):
  if "Username" in session:
    conn = get_db_connection2()
    userId = conn.execute("SELECT UserID FROM UserData WHERE Username = (?)",
                          (data["targetUsername"], )).fetchall()
    conn.close()
    if userId:
      conn = get_db_connection()
      conn.execute(
        "INSERT INTO MessageTable (SenderID,ReceiverID,messageContent) Values ((?),(?),(?))",
        (session["UserID"], userId[0][0], data["message"]))
      conn.commit()
      conn.close()
      print("sending message")
      socketio.emit("receiveMessage", {
        "Sender": session["Username"],
        "Receiver": data["targetUsername"],
        "message": data["message"]
      },
                    to=data["targetUsername"])
      socketio.emit("receiveMessage", {
        "Sender": session["Username"],
        "Receiver": data["targetUsername"],
        "message": data["message"]
      },
                    to=session["Username"])


@socketio.on("accept_friend_request")
def accept_friend_request(data):
  if "Username" in session:
    conn = get_db_connection2()
    UserStatus = conn.execute(
      "Select UserID FROM UserData WHERE Username = (?)",
      (data["user"], )).fetchall()
    conn.commit()
    if UserStatus:

      conn = get_db_connection2()
      conn.execute(
        "UPDATE FriendsTable Set Status = (?) WHERE User1ID = (?) AND User2ID = (?)",
        ("accepted", UserStatus[0][0], session["UserID"]))
      conn.commit()
      conn.close()
      return {"status": "success"}
  return {"status": "success"}


@socketio.on("send_friend_request")
def send_friend_request(data):
  if "Username" in session:
    conn = get_db_connection2()
    UserStatus = conn.execute(
      "Select UserID FROM UserData WHERE Username = (?)",
      (data["user"], )).fetchall()
    conn.commit()
    if UserStatus:

      conn = get_db_connection2()
      conn.execute(
        "INSERT INTO FriendsTable (User1ID,User2ID,Status) VALUES (?,?,?)",
        (session["UserID"], UserStatus[0][0], "pending"))
      conn.commit()
      conn.close()
      return {"status": "success"}
    else:
      return {"status": "error"}


@socketio.on("disconnect")
def client_disconnect():
  if "Username" in session:
    room = session["Username"]
    leave_room(room)


if __name__ == "__main__":
  print("server running")
  socketio.run(app, host='0.0.0.0', port=81)
