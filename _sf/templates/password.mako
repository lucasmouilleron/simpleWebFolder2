<!DOCTYPE html>
<html>
<head>
    <script src="${baseURL}/_sf_assets/jquery.js"></script>
    <script src="${baseURL}/_sf_assets/stupidtable.js"></script>
    <script src="${baseURL}/_sf_assets/tooltipstr.js"></script>
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.3.0/css/all.css">
    <link rel="stylesheet" href="${baseURL}/_sf_assets/tooltipster.css">
    <link rel="stylesheet" href="${baseURL}/_sf_assets/tooltipster-theme.css">
    <link rel="stylesheet" href="${baseURL}/_sf_assets/style.css?ck=6">
    <link rel="icon" href="${baseURL}/_sf_assets/icon.png">
    <title>${h.NAME}</title>
</head>

<body>

<div class="header">
    <a href="${baseURL}/">
        <div class="logo"></div>
    </a>
</div>

<div class="name"><a href="${baseURL}/">${h.NAME}</a></div>

<div class="navigation section">
    <div class="parent" data-toggle="tooltip" title="Go to parent folder">
        %if path != "":
            <a href="${baseURL}/${path}/.."><i class="icon fas fa-long-arrow-alt-up"></i></a>
        %else:
            <a class="disabled"><i class="icon fas fa-long-arrow-alt-up"></i></a>
        % endif
    </div>
    <div class="page">/${path}</div>
</div>


    %for alert in alerts:
        <div class="alert">
            <h2>${alert[0]}</h2>
            <p>${alert[1]}</p>
        </div>
    %endfor

<div class="block section">
    <div class="section-title">Protected area, please authenticate</div>
    <form method="post" action="${baseURL}/${path}">
        <input id="password" type="password" name="password" placeholder="Password"/>
        <input type="submit" name="password-submit" value="Login"/>
    </form>
    <center>Contact us at <a href="mailto:${h.MAIL}">${h.MAIL}</a> if you have forgotten your password or need one.</center>
</div>

<div class="footer">${h.NAME} - ${h.CREDITS}</div>

<script>
    $(document).ready(function () {
        $("#password").focus();
    });
</script>

</body>
</html>