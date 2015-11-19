document.write('<table border=0>');
for(var i=1; i<=9; i++)
{
    document.write('<tr>');
    for(var j=1; j<=9; j++)
    {
        document.write('<td>' + j + '*' + i + '=' +
        j*i + '&nbsp;&nbsp;&nbsp;' + '</td>');
    }
    document.write('</tr>');
}
document.write('</table>');
