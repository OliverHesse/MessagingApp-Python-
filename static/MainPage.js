let currentmessagePointer = 0;
let usersLoaded = false;
let selectedUser = "";
let logoutFocus = false;
const FriendBar = document.getElementById("FriendsContainer");
const messageScreenRef = document.getElementById("chatContainer");
var socket = io()
  socket.on("connect",function(){
    socket.emit('getFriendsAndGroup', {data: 'none'},function(data){
      LoadFriends(data)
    });
  });
socket.on("receiveMessage",function(data){
  
  
  console.log("message recived")
  
  if (data["Sender"] == selectedUser ){
    
    let newMessageContainerdiv = document.createElement("div")
    let messageDiv = document.createElement("div");
    newMessageContainerdiv.setAttribute("class","baseMessageContainer MessageContainerOther")
    messageDiv.setAttribute("class","messageBase messageOther")
    messageDiv.innerHTML = data["message"]
    newMessageContainerdiv.appendChild(messageDiv)
    messageScreenRef.appendChild(newMessageContainerdiv)
    
  }else if(data["Receiver"] == selectedUser){
    
    let newMessageContainerdiv = document.createElement("div")
    let messageDiv = document.createElement("div");
    newMessageContainerdiv.setAttribute("class","baseMessageContainer MessageContainerSelf")
    messageDiv.setAttribute("class","messageBase messageSelf")
    messageDiv.innerHTML = data["message"]
    newMessageContainerdiv.appendChild(messageDiv)
    messageScreenRef.appendChild(newMessageContainerdiv)
    
  }
  setBottom()
})



function LoadFriends(friends){
  if(usersLoaded != true){
    console.log(friends["error"]);
    if (friends["error"] == 2){
      var newButton = document.createElement("button");
      
      let text = document.createTextNode("Button");
      newButton.appendChild(text);
      FriendBar.appendChild(newButton);
      newButton.addEventListener("click", this.loadAddFriend.bind(this));
      
      };
    if (friends["error"] == 1){
      
      console.log(friends["friends"]);
      console.log(friends["friends"]["Groups"].length)
      
      for ( let i = 0; i< friends["friends"]["Friends"].length;i++){
        
        var friendContainer = document.createElement("button");
        friendContainer.setAttribute("class","Friend");
        friendContainer.setAttribute("id",friends["friends"]["Friends"][i]);
        friendContainer.addEventListener("click", this.selectFriend);
        friendContainer.innerHTML = friends["friends"]["Friends"][i] ;
        FriendBar.appendChild(friendContainer);
        
      };
      for ( let i = 0; i< friends["friends"]["Groups"].length;i++){
        var friendContainer = document.createElement("button");
        friendContainer.setAttribute("class","Friend");
        friendContainer.setAttribute("id",friends["friends"]["Groups"][i]);
        friendContainer.addEventListener("click", this.selectGroup);
        friendContainer.innerHTML = friends["friends"]["Groups"][i] ;
        FriendBar.appendChild(friendContainer);      
      }
    usersLoaded = true;
  }
  };
}
function loadAddFriend(){

  console.log("i pressed this");
  document.location.href = "https://messengerapp.oliverfh.repl.co/addFriend";
};

function loadUser(e) {
  let UserDiv = document.getElementById("leftContainer");
  let MainBodyDiv = document.getElementById("centerContainer");
  MainBodyDiv.classList.add("hideCenter");
  UserDiv.classList.remove("hideLeft");
  console.log("test");
  
}
function loadFriend(e) {
  let FriendProfileDiv = document.getElementById("rightContainer");
  let MainBodyDiv = document.getElementById("centerContainer");
  MainBodyDiv.classList.add("hideCenter");
  FriendProfileDiv.classList.remove("hideRight");
  console.log("test");

  
}
function closeFriendPage(e){
  let FriendProfileDiv = document.getElementById("rightContainer");
  let MainBodyDiv = document.getElementById("centerContainer");
  MainBodyDiv.classList.remove("hideCenter");
  FriendProfileDiv.classList.add("hideRight");
}
function closeUserPage(e) {
  let MainBodyDiv = document.getElementById("centerContainer");
  MainBodyDiv.classList.remove("hideCenter");
  let UserPage = document.getElementById("leftContainer");
  UserPage.classList.add("hideLeft");
  
}

function LoadOldMessages(refId,messages,mLength) {
  console.log(messages);
  for(let i = 0;i<mLength;i++){
    console.log(refId[messages[i][0]])
    console.log(messages[0])
    
    if (refId[messages[i][0]] == selectedUser ){
      
      let newMessageContainerdiv = document.createElement("div")
      let messageDiv = document.createElement("div");
      newMessageContainerdiv.setAttribute("class","baseMessageContainer MessageContainerOther")
      messageDiv.setAttribute("class","messageBase messageOther")
      messageDiv.innerHTML = messages[i][1]
      newMessageContainerdiv.appendChild(messageDiv)
      messageScreenRef.appendChild(newMessageContainerdiv)
      
    }else {
      
      let newMessageContainerdiv = document.createElement("div")
      let messageDiv = document.createElement("div");
      newMessageContainerdiv.setAttribute("class","baseMessageContainer MessageContainerSelf")
      messageDiv.setAttribute("class","messageBase messageSelf")
      messageDiv.innerHTML = messages[i][1]
      newMessageContainerdiv.appendChild(messageDiv)
      messageScreenRef.appendChild(newMessageContainerdiv)
      
    } 
  }
  
}
function selectGroup(e) {
  closeUserPage()
  console.log("this is a test");
  if(selectedUser != e.target.id && selectedUser != ""){
    console.log(selectedUser);
    e.target.classList.add("FriendFocused");
    document.getElementById(selectedUser).classList.remove("FriendFocused");
    selectedUser = e.target.id;
    messageScreenRef.replaceChildren();
    socket.emit("retrieveGroupMessages",{"otherUser":selectedUser},function(data) {
      console.log(data);
      if(data["error"] != "noMessage"){
        LoadOldMessages(data["refID"],data["messages"],data["messagesRetreived"])
        setBottom()
      }
    })
  }else if (selectedUser == ""){
    selectedUser = e.target.id;
    e.target.classList.add("FriendFocused");
    messageScreenRef.replaceChildren();
    socket.emit("retrieveGroupMessages",{"otherUser":selectedUser},function(data) {
      console.log(data);
      if(data["error"] != "noMessage"){
        LoadOldMessages(data["refID"],data["messages"],data["messagesRetreived"])
        setBottom()
      }
    })
  }
  
}
function selectFriend(e) {
  closeUserPage()
  console.log(e);
  if(selectedUser != e.target.id && selectedUser != ""){
    console.log(selectedUser);
    e.target.classList.add("FriendFocused");
    document.getElementById(selectedUser).classList.remove("FriendFocused");
    selectedUser = e.target.id;
    messageScreenRef.replaceChildren();
    socket.emit("retrieveMessages",{"otherUser":selectedUser},function(data) {
      console.log(data);
      if(data["error"] != "noMessage"){
        LoadOldMessages(data["refID"],data["messages"],data["messagesRetreived"])
        setBottom()
      }
    })
  }else if (selectedUser == ""){
    selectedUser = e.target.id;
    e.target.classList.add("FriendFocused");
    messageScreenRef.replaceChildren();
    socket.emit("retrieveMessages",{"otherUser":selectedUser},function(data) {
      console.log(data);
      if(data["error"] != "noMessage"){
        LoadOldMessages(data["refID"],data["messages"],data["messagesRetreived"])
        setBottom()
      }
    })
  }

}
function setBottom(){
  messageScreenRef.scrollTo(0, messageScreenRef.scrollHeight);
}
function sendMessage(e){
  if (selectedUser != ""){
    console.log("send MEssage")
    let sendBox = document.getElementById("inputBox");
    if(sendBox.value != ""){
      console.log("send MEssage")
      socket.emit("sendMessage",{"targetUsername": selectedUser,"message": sendBox.value})
    }
  }     
}
function showLogOut(e) {
  //id - dropDownMenue
  // hideclass-dropdown-content-hide
  console.log(logoutFocus);
  if(logoutFocus == false){
    logoutFocus = true;
    //remove hide class
    document.getElementById("dropDownMenue").classList.remove("dropdown-content-hide")
  }else{
    logoutFocus = false;
    //add hide class
    document.getElementById("dropDownMenue").classList.add("dropdown-content-hide")
  }
}