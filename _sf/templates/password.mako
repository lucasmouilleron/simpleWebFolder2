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
    <link rel="stylesheet" href="${baseURL}/_sf_assets/style.css">
    <link rel="stylesheet" href="${baseURL}/_sf_overrides/style.css">
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
            .
        % endif
    </div>
    <div class="page">${path}</div>
</div>

<div class="authenticate section">
    <div class="section-title">Protected area, please authenticate</div>
    <form method="post">
        <input type="password" name="password" placeholder="Password"/>
        <input type="submit" name="password-submit" value="Login"/>
    </form>
</div>

<div class="footer">${h.NAME} - ${h.CREDITS}</div>
</body>
</html>