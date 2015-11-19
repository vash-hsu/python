document.write('</br>');
document.write('<style>');
document.write('p    {text-align:center;}');
document.write('body {background-color:lightgrey}');
document.write('</style>');
document.write('<p>');
document.write('<h id="date" style="background-color:grey; color:white"></h>');
document.write('</br>');
document.write('<h id="timestring" style="background-color:grey; color:white"></h>');
document.write('<p>');

var myVar = setInterval(function(){ myTimer() }, 1000);

function myTimer() {
    var d = new Date();
    var day = d.toLocaleDateString();
    var ts = d.toTimeString()
    document.getElementById("date").innerHTML = day;
    document.getElementById("timestring").innerHTML = ts;
}
