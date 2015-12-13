// http://www.uiupdates.com/create-digital-clock-using-html5-canvas-and-javascript/

document.write('<style>');
document.write('div { width: 480px; height: 720px; margin: 0 auto; }');
document.write('h1 { font-size: 20px; text-align: center; }');
document.write('#clock { display: block; margin: 0 auto; background: black; border: 2px solid grey; }');
document.write('</style>');

document.write('<h1>Digital Clock using HTML5 Canvas and JavaScript</h1>');
document.write('<canvas id="clock" width="400" height="200"></canvas>');

var context;
var d;
var str;
function getClock()
  {
     //Get Current Time
     d = new Date();
     str = positionZero(d.getHours(), d.getMinutes(), d.getSeconds());
     //Get the Context 2D or 3D
     context = clock.getContext("2d");
     context.clearRect(0, 0, 500, 200);
     context.font = "80px Arial";
     context.fillStyle = "#abcdef";
     context.fillText(str, 42, 125);
  }
 
function positionZero(hour, min, sec)
  {
    var curTime;
    if(hour < 10)
       curTime = "0"+hour.toString();
    else
       curTime = hour.toString(); 
 
    if(min < 10)
       curTime += ":0"+min.toString();
    else
       curTime += ":"+min.toString(); 
 
   if(sec < 10)
       curTime += ":0"+sec.toString();
   else
       curTime += ":"+sec.toString();
       return curTime;
  }
 
setInterval(getClock, 1000)