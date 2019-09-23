<!DOCTYPE html>
<html>
<head>
    <script src="${baseURL}/_sf_assets/jquery.js"></script>
    <script src="${baseURL}/_sf_assets/stupidtable.js"></script>
    <script src="${baseURL}/_sf_assets/clipboard.js"></script>
    <script src="${baseURL}/_sf_assets/tooltipstr.js"></script>
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.3.0/css/all.css">
    <link rel="stylesheet" href="${baseURL}/_sf_assets/tooltipster.css">
    <link rel="stylesheet" href="${baseURL}/_sf_assets/tooltipster-theme.css">
    <link rel="stylesheet" href="${baseURL}/_sf_assets/style.css?ck=6">
    <link rel="icon" href="${baseURL}/_sf_assets/icon.png">
    <title>${h.NAME}</title>
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
    <h2>An error occured</h2>
    <p>Hint: ${e}</p>
    <p>We are sorry for this.<br/>Please send us an email @ <a href="mailto:${h.MAIL}">${h.MAIL}</a> if the problem persits.</p>

    % if h.DEBUG and le is not None and lt is not None:
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

<script>
    $(document).ready(function () {
        $('[data-toggle="tooltip"]').tooltipster({theme: "tooltipster-borderless", animationDuration: 200, delay: 20, side: "bottom"});
        $('[data-toggle="tooltip-left"]').tooltipster({theme: "tooltipster-borderless", animationDuration: 200, delay: 20, side: "left"});
    });
</script>

</body>
</html>