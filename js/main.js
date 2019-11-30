var addbookslock = false;
document.getElementById('addbooks').addEventListener('click',function(){
    addbookslock = true;
})

function unlock(){
    addbookslock = false;
}

function addElement(){
    var para = document.createElement("button");
    var node = document.createTextNode("This is new.");
    para.appendChild(node);
    var element = document.getElementById("toolbarViewerRight");
    element.appendChild(para);
}