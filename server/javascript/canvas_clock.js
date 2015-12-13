//http://www.w3schools.com/canvas/tryit.asp?filename=trycanvas_clock_start

var style_number = [0, 1, 2];
var style_color = [0, 1, 2, 3];

var xDown = null;
var yDown = null;
var AcceptableNoise = 0;

function change_style_number(offset)
{
    profile.number_style = (profile.number_style + offset) % style_number.length;
}

function change_style_color(offset)
{
    profile.color_style = (profile.color_style + offset) % style_color.length;
}

function update_color_in_profile()
{
    switch(profile.color_style)
    {
        case 1:
            profile.number_color = 'black';
            profile.hour_color = 'black';
            profile.minute_color = 'black';
            profile.second_color = 'black';
            profile.main_color = 'PowderBlue';
            profile.in_color = 'LightCyan';
            profile.out_color = 'DeepSkyBlue';
            break;
        case 2:
            profile.number_color = 'DarkSlateGray';
            profile.hour_color = 'DarkSlateGray';
            profile.minute_color = 'DarkSlateGray';
            profile.second_color = 'DarkSlateGray';
            profile.main_color = 'LightGreen';
            profile.in_color = 'Azure';
            profile.out_color = 'Chartreuse';
            break;
        case 3:
            profile.number_color = 'DarkSlateGray';
            profile.hour_color = 'DarkSlateGray';
            profile.minute_color = 'DarkSlateGray';
            profile.second_color = 'DarkSlateGray';
            profile.main_color = 'Orange';
            profile.in_color = 'Beige';
            profile.out_color = 'DarkOrange';
            break;
        default:
            profile.number_color = 'seagreen';
            profile.hour_color = 'seagreen';
            profile.minute_color = 'seagreen';
            profile.second_color = 'seagreen';
            profile.main_color = '#111';
            profile.in_color = '#333';
            profile.out_color = '#222';
            break;
    }
}

var profile =
{
    previousOrientation: '',
    width: 0, height: 0, radius: 0,
    x: 0, y: 0,
    background: 'black',
    number_style: 0,
    color_style: 0,
    number_color: '',
    hour_color: '', minute_color: '', second_color: '',
    main_color: '', in_color: '', out_color: '',
};

var roman = ['', 'I', 'II', 'III', 'IV', 'V', 'VI',
             'VII', 'VIII', 'IX', 'X', 'XI', 'XII'];
var binary = ['', '1', '10', '11', '100', '101', '110',
              '0111', ' 1000', ' 1001', ' 1010', ' 1011', '1100'];

var my_canvas = '<canvas id="canvas" width="' + profile.width +
                '" height="' + profile.height +
                '" style="background-color:'+ profile.background +
                '"></canvas>';
document.writeln(my_canvas);
//
var canvas = document.getElementById("canvas");
var ctx = canvas.getContext("2d");
//
document.addEventListener('touchstart', handleTouchStart, false);
document.addEventListener('touchmove', handleTouchMove, false);

setTimeout(dynamic_adjust, 300);
setInterval(drawClock, 1000);
//

//document.onclick = function()
document.ondblclick = function()
{
	dynamic_adjust();
    change_style_number(1);
    change_style_color(1);
    update_color_in_profile();
};

window.onload = function()
{
    dynamic_adjust();
    update_color_in_profile();
};

window.onresize = function()
{
    dynamic_adjust();
};

window.orientationchange = function()
{	
	checkOrientation();
};


function checkOrientation()
{
  if (window.orientation != profile.previousOrientation)
  {
  	profile.previousOrientation = window.orientation;
  	dynamic_adjust();
  	drawClock();
  }
};

function dynamic_adjust()
{
    //profile.width = window.innerWidth;
    //profile.height = window.innerHeight;
    //if (screen.availWidth != null)      { profile.width = screen.availWidth; }
    //else 
    if (window.innerWidth != null) { profile.width = window.innerWidth; }
    //else if (window.screen != null)     { profile.width = window.screen.availWidth; } 
    //else if (document.body != null)     { profile.width = document.body.clientWidth; }
    
    //if (screen.availHeight != null)     { profile.height = screen.availHeight; }
    //else 
    if(window.innerHeight != null) { profile.height = window.innerHeight; }
    //else if(window.screen != null)      { profile.height = window.screen.availHeight; }
    //else if(document.body != null)      { profile.height = document.body.clientHeight; }
    
    profile.width = profile.width * 0.98;
    profile.height = profile.height * 0.98;
    
    profile.radius = 0.9 * Math.min(profile.height, profile.width) / 2;
    canvas.width = profile.width;
    canvas.height = profile.height;
    profile.x = profile.width / 2;
    profile.y = profile.height / 2;
    ctx.translate(profile.x, profile.y);
}

function hour2string(number, style)
{
    switch(style)
    {
        case 1:
            result = roman[number];
            break;
        case 2:
            result = binary[number];
            break;
        default:
            result = number.toString();
            break;
    }
    return result;
}

function drawClock()
{
    drawFace(ctx, profile.radius,
             profile.main_color, profile.in_color, profile.out_color);
    drawNumbers(ctx, profile.radius, profile.number_color);
    drawTime(ctx, profile.radius,
             profile.hour_color, profile.minute_color, profile.second_color);
}

function drawFace(ctx, radius, main_color, in_color, out_color)
{
    var grad;
    ctx.beginPath();
    ctx.arc(0, 0, radius, 0, 2 * Math.PI);
    ctx.fillStyle = main_color;
    ctx.fill();
    //
    grad = ctx.createRadialGradient(0, 0, radius * 0.95, 0, 0, radius * 1.05);
    grad.addColorStop(0, out_color);
    grad.addColorStop(0.5, in_color);
    grad.addColorStop(1, out_color);
    ctx.strokeStyle = grad;
    ctx.lineWidth = radius * 0.1;
    ctx.stroke();
    //
    ctx.beginPath();
    ctx.arc(0, 0, radius * 0.1, 0, 2 * Math.PI);
    ctx.fillStyle = in_color;
    ctx.fill();
}

function drawNumbers(ctx, radius, color)
{
    var ang;
    var num;
    ctx.fillStyle = color;
    ctx.font = radius * 0.15 + "px arial";
    ctx.textBaseline = "middle";
    ctx.textAlign="center";
    for(num = 1; num < 13; num++)
    {
        ang = num * Math.PI / 6;
        ctx.rotate(ang);
        ctx.translate(0, -radius * 0.85);
        ctx.rotate(-ang);
        ctx.fillText(hour2string(num, profile.number_style), 0, 0);
        ctx.rotate(ang);
        ctx.translate(0, radius * 0.85);
        ctx.rotate(-ang);
    }
}

function drawTime(ctx, radius, hour_color, minute_color, second_color)
{
    var now = new Date();
    var hour = now.getHours();
    var minute = now.getMinutes();
    var second = now.getSeconds();
    hour = hour % 12;
    hour = (hour * Math.PI / 6) +
           (minute * Math.PI / (6 * 60)) +
           (second * Math.PI / (360*60));
    drawHand(ctx, hour, radius * 0.5, radius * 0.07, hour_color);
    minute = (minute * Math.PI / 30) + (second * Math.PI / (30*60));
    drawHand(ctx, minute, radius * 0.7, radius * 0.07, minute_color);
    second = (second * Math.PI / 30);
    drawHand(ctx, second, radius * 0.75, radius * 0.02, second_color);
}

function drawHand(ctx, pos, length, width, color)
{
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.lineCap = "round";
    ctx.moveTo(0, 0);
    ctx.rotate(pos);
    ctx.lineTo(0, -length);
    ctx.stroke();
    ctx.rotate(-pos);
}

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
            change_style_number(1);
        }
        else
        {
            /* right swipe */
            change_style_number(style_number.length - 1);
        }
    }
    else
    {
        if ( yDiff > 0 )
        {
            /* up swipe */
            change_style_color(1);
            update_color_in_profile();
        }
        else
        {
            /* down swipe */
            change_style_color(style_color.length - 1);
            update_color_in_profile();
        }
    }
    /* reset values */
    xDown = null;
    yDown = null;
};
