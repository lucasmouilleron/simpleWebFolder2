<!DOCTYPE html>
<html>
<head>
    <script src="${baseURL}/_sf_assets/jquery.js"></script>
    <script src="${baseURL}/_sf_assets/stupidtable.js"></script>
    <script src="${baseURL}/_sf_assets/tooltipstr.js"></script>
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.3.0/css/all.css">
    <link rel="stylesheet" href="${baseURL}/_sf_assets/tooltipster.css">
    <link rel="stylesheet" href="${baseURL}/_sf_assets/tooltipster-theme.css">
    <link rel="stylesheet" href="${baseURL}/_sf_assets/style.css?ck=3">
    <link rel="icon" href="${baseURL}/_sf_assets/icon.png">
    <title>${h.NAME} - Admin</title>
</head>

<body>

<div class="header">
    <a href="${baseURL}/">
        <div class="logo"></div>
    </a>
</div>

<div class="name"><a href="${baseURL}/">${h.NAME}</a></div>

<div class="block section">
    <div class="section-title">Admin area, please authenticate</div>
    <form method="post" action="${baseURL}/admin">
        <input id="password-admin" type="password" name="password-admin" placeholder="Password"/>
        <input type="submit" name="password-submit" value="Login"/>
    </form>
</div>

<div class="footer">${h.NAME} - ${h.CREDITS}</div>

<script>
    $(document).ready(function () {
        $("#password-admin").focus();
    });
</script>

</body>
</html>