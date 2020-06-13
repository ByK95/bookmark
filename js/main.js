var mapperCmd = [];
var archiveLock = false;

document.getElementById("addbooks").addEventListener("click", function () {
    pushCommand("addbook", null);
});

var archiveButton = document.getElementById("archive");
archiveButton.addEventListener("click", function () {
    if (!archiveLock) {
        archiveLock = true;
        archiveButton.style.backgroundColor = "#ffb300";
        return;
    }
    archiveLock = false;
    archiveButton.style.backgroundColor = "#fbfbfb";
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

var docs = document.getElementsByTagName("A");
for (let index = 0; index < docs.length; index++) {
    const element = docs[index];
    element.addEventListener("click", function (el) {
        if (archiveLock && !el.target.classList.contains("b-config")) {
            pushCommand("finished", el.target.innerText);
            el.target.href = "";
            el.target.parentElement.remove();
            event.preventDefault();
        }
        archiveLock = false;
        archiveButton.style.backgroundColor = "#fbfbfb";
    });
}
