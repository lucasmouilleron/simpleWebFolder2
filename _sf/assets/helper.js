///////////////////////////////////////////////////////////////////////////////////
function copyStringToClipboard(str) {
    var el = document.createElement('textarea');
    el.value = str;
    el.setAttribute('readonly', '');
    el.style = {position: 'absolute', left: '-9999px'};
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
}

///////////////////////////////////////////////////////////////////////////////////
function cleanStringForURL(string) {
    return string.replace(/[^a-zA-Z0-9-_]/g, '');
}