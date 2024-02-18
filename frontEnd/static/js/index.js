var circle = document.getElementById("circle");
var upbtn = document.getElementById("upbtn");
var dwnbtn = document.getElementById("dwnbtn");

var rotateValue = circle.style.transform;
var rotateSum;

upbtn.onclick = function(){
    rotateSum = rotateValue + "rotate(-90deg)";
    circle.style.transform = rotateSum;
    rotateValue = rotateSum;
}

dwnbtn.onclick = function(){
    rotateSum = rotateValue + "rotate(90deg)";
    circle.style.transform = rotateSum;
    rotateValue = rotateSum;
}