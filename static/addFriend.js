
var socket = io()
socket.on("connect",function(){
  socket.emit('connectEcho', {data: 'I am connected!'});
});
let lastFilter = "";
let currentRow = 0;
let loadedUsers = [];
const users_Container = document.getElementById("usersContainer");

function loadUsers(users) {
  console.log(users)
  for(let i =0; i < users.length;i++){
    console.log(users[i])
    var newContainer = document.createElement("div");
    let text = document.createElement("p");
    text.setAttribute("id","test");
    text.setAttribute("class","baseName");
    text.appendChild(document.createTextNode(users[i][0]));
    
    newContainer.setAttribute("id","user_Container");
    newContainer.appendChild(text);
    let element2;

    if(users[i][1] == "none"){
      element2 = document.createElement("button");
      element2.setAttribute("id",i+currentRow);
      element2.setAttribute("class","baseButton send");
      element2.addEventListener("click",this.sendReq);
      let btnTxt = document.createTextNode("send request");
      element2.appendChild(btnTxt);
    }
    else if(users[i][1] == "pending"){
      element2 = document.createElement("button");
      element2.setAttribute("id",i+currentRow);
      element2.setAttribute("class","baseButton pending");
      element2.addEventListener("click",this.acceptReq);
      let btnTxt = document.createTextNode("accept request");
      element2.appendChild(btnTxt);
    }
    else{
      element2 = document.createElement("p");
      element2.appendChild(document.createTextNode(users[i][1]));
      element2.setAttribute("class","baseText");
    }
    loadedUsers.push(users[i][0])
    newContainer.appendChild(element2);
    users_Container.appendChild(newContainer);
  };    
  let moreDiv = document.createElement("div");
  moreDiv.setAttribute("id","moreDiv");
  let moreButton = document.createElement("button");
  moreButton.setAttribute("id","moreButton");
  moreButton.addEventListener("click",this.loadmore);
  moreButton.appendChild(document.createTextNode("Load More"));
  moreDiv.append(moreButton);
  users_Container.appendChild(moreDiv);
}
function loadmore(e){
  e.target.remove();
  getUsers();
}
function acceptReq(e){
  console.log("accept request");
  console.log(e.target.id);
  socket.emit("accept_friend_request", {user: loadedUsers[e.target.id]}, function(params){
    if(params["status"] == "success"){
      let element = e.target
      let elementContainer = e.target.parentElement;
      element.remove();
      let text = document.createElement("p");
      text.setAttribute("class","baseText");
      text.appendChild(document.createTextNode("friends"));
      elementContainer.appendChild(text);
      console.log("success");       
    }
  });
}
function sendReq(e){
  console.log("send request");
  console.log(e.target.id);
  socket.emit('send_friend_request', {user: loadedUsers[e.target.id]},function(params){
    console.log(params);
    if(params["status"] == "success"){
      let element = e.target;
      let elementContainer = e.target.parentElement;
      element.remove();
      let text = document.createElement("p");
      text.setAttribute("class","baseText");
      text.appendChild(document.createTextNode("request Sent"));
      elementContainer.appendChild(text);
      console.log("success");
    }
  });
}
function getUsers() {
  
  socket.emit('getUsers', {filter:document.getElementById('Username').value,currentRow:currentRow}, function(data){
    console.log(data);
    if(data["error"] != "No User Found"){
      loadUsers(data["data"]);
      currentRow += 5;
    }

  });
  
}
function searchUsers(params){
  if(document.getElementById('Username').value != lastFilter){
    lastFilter = document.getElementById('Username').value;
    currentRow = 0;
    users_Container.replaceChildren();
    getUsers();
    }
}
function goBack(){
  document.location.href = "https://messengerapp.oliverfh.repl.co/main";
}