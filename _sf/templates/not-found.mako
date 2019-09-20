<!DOCTYPE html>
<html>
<head>
    <script src="${baseURL}/_sf_assets/jquery.js"></script>
    <script src="${baseURL}/_sf_assets/stupidtable.js"></script>
    <script src="${baseURL}/_sf_assets/tooltipstr.js"></script>
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.3.0/css/all.css">
    <link rel="stylesheet" href="${baseURL}/_sf_assets/tooltipster.css">
    <link rel="stylesheet" href="${baseURL}/_sf_assets/tooltipster-theme.css">
    <link rel="stylesheet" href="${baseURL}/_sf_assets/style.css?ck=5">
    <link rel="icon" href="${baseURL}/_sf_assets/icon.png">
    <title>${h.NAME} - /${path}</title>
</head>

<body>

<div class="tools">
    <a href="${baseURL}/admin" data-toggle="tooltip-left" title="Admin"><i class="icon fas fa-tools"></i></a>
</div>

<div class="header">
    <a href="${baseURL}/">
        <div class="logo"></div>
    </a>
</div>

<div class="name"><a href="${baseURL}/">${h.NAME}</a></div>

<div class="error section">
    <h2>Item not found</h2>
    <p>The item <i>/${path}</i> was not found.</p>

    <p>If this is not normal, please send us an email @ <a href="mailto:${h.MAIL}">${h.MAIL}</a> if the problem persits.</p>

</div>

<div class="footer">${h.NAME} - ${h.CREDITS}</div>
</body>
</html>