var addbookslock = false;
var config = false;

document.getElementById("addbooks").addEventListener("click", function() {
  addbookslock = true;
});

function unlock() {
  addbookslock = false;
  config = false;
}

function addElement() {
  var para = document.createElement("button");
  var node = document.createTextNode("This is new.");
  para.appendChild(node);
  var element = document.getElementById("toolbarViewerRight");
  element.appendChild(para);
}
