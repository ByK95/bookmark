var addbookslock = false;
document.getElementById('addbooks').addEventListener('click',function(){
    addbookslock = true;
})

function unlock(){
    addbookslock = false;
}