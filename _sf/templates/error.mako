<!DOCTYPE html>
<html>
<head>
    <script src="${baseURL}/_sf_assets/jquery.js"></script>
    <script src="${baseURL}/_sf_assets/stupidtable.js"></script>
    <script src="${baseURL}/_sf_assets/clipboard.js"></script>
    <script src="${baseURL}/_sf_assets/tooltipstr.js"></script>
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.0.13/css/all.css">
    <link rel="stylesheet" href="${baseURL}/_sf_assets/tooltipster.css">
    <link rel="stylesheet" href="${baseURL}/_sf_assets/tooltipster-theme.css">
    <link rel="stylesheet" href="${baseURL}/_sf_assets/style.css?ck=2">
    <title>${h.NAME}</title>
</head>

<body>

<div class="header">
    <a href="${baseURL}/">
        <div class="logo"></div>
    </a>
</div>

<div class="name"><a href="${baseURL}/">${h.NAME}</a></div>

<div class="error section">
    <h2>An error occured</h2>
    <p>Hint: ${e}</p>
    <p>We are sorry for this.<br/>Please send us an email @ <a href="mailto:${h.MAIL}">${h.MAIL}</a> if the problem persits.</p>

    % if h.DEBUG:
        <div class="block">
            <p>${le}</p>
            <p>
                % for lto in lt:
                ${lto}<br/>
                % endfor
            </p>
        </div>
    % endif

</div>

<div class="footer">${h.NAME} - ${h.CREDITS}</div>
</body>
</html>