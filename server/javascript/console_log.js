console.log('\n');
for(var i=1; i<=9; i++)
{
    var str = "|"
    for(var j=1; j<=9; j++)
    {
        str_result = ' '+j+'*'+i+'='+j*i
        space2add = 9 - str_result.length
        str += str_result + Array(space2add).join(" ") + '|'
    }
    console.log(str);
}
console.log('\n');
/*
Activate debugging in your browser (Chrome, IE, Firefox) with F12,
and select "Console" in the debugger menu. 
*/
