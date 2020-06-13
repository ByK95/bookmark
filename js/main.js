var mapperCmd = [];

document.getElementById("addbooks").addEventListener("click", function () {
    pushCommand("addbook", null);
});

function cleanMapper() {
    mapperCmd = [];
}

function pushCommand(command, args) {
    if (args == null) {
        mapperCmd.push(command.concat("/"));
        return;
    }
    mapperCmd.push(command.concat("/" + args));
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
    element.addEventListener("click", function (el) {
        pushCommand("config", el.target.innerText);
        remElement();
        if (el.target.children.length == 0) {
            addElement("i", ["fa", "fa-check"], "", el.target);
        }
    });
}
