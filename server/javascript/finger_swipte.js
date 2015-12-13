// http://stackoverflow.com/questions/2264072/detect-a-finger-swipe-through-javascript-on-the-iphone-and-android

var my_canvas = '<canvas id="canvas" width="' + 1024 +
                '" height="' + 768 +
                '" style="background-color:gray"></canvas>'
document.write('<style> p {text-align:center;} </style>');
document.writeln('<p>' + my_canvas + '</p>');
var canvas = document.getElementById("canvas");
var ctx = canvas.getContext("2d");

document.addEventListener('touchstart', handleTouchStart, false);
document.addEventListener('touchmove', handleTouchMove, false);

var xDown = null;
var yDown = null;
var AcceptableNoise = 1;
function handleTouchStart(evt)
{
    xDown = evt.touches[0].clientX;
    yDown = evt.touches[0].clientY;
}

function handleTouchMove(evt)
{
    if ( ! xDown || ! yDown ) { return; }
    var xUp = evt.touches[0].clientX;
    var yUp = evt.touches[0].clientY;
    var xDiff = xDown - xUp;
    var yDiff = yDown - yUp;
    if (Math.max(Math.abs(xDiff), Math.abs(yDiff)) < AcceptableNoise)
    {
        xDown = null;
        yDown = null;
        return;
    }
    if ( Math.abs(xDiff) > Math.abs(yDiff) )
    {
        if ( xDiff > 0 )
        {
            /* left swipe */
            window.alert('left swipe');
        }
        else
        {
            /* right swipe */
            window.alert('right swipe');
        }
    }
    else
    {
        if ( yDiff > 0 )
        {
            /* up swipe */
            window.alert('up swipe');
        }
        else
        {
            /* down swipe */
            window.alert('down swipe');
        }
    }
    /* reset values */
    xDown = null;
    yDown = null;
};
