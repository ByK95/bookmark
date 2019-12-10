var addbookslock = false;
var config = false;

document.getElementById("addbooks").addEventListener("click", function() {
    addbookslock = true;
});

function unlock() {
    addbookslock = false;
    config = false;
}

function addElement(type, classes, payload, target) {
    // <i class="fa fa-check"></i>
    var para = document.createElement(type);
    var node = document.createTextNode(payload);
    para.classList.add(...classes);
    para.appendChild(node);
    target.appendChild(para);
}

var a = document.getElementsByClassName("b-config");
function remElement() {
    for (let index = 0; index < a.length; index++) {
        const element = a[index];
        if (element.children.length == 1) {
            element.children[0].remove();
        }
    }
}

for (let index = 0; index < a.length; index++) {
    const element = a[index];
    element.addEventListener("click", function(el) {
        config = el.target.innerText;
        remElement();
        if (el.target.children.length == 0) {
            addElement("i", ["fa", "fa-check"], "", el.target);
        }
    });
}
