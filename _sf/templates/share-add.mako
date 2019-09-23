<% pathsDisplay = ", ".join(paths)%>
<% containersDisplay = ", ".join(containers)%>

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
    <title>${h.NAME} - Admin - Add share - ${paths}</title>
</head>

<body class="admin">

<div class="admin-section">Admin section</div>

<div class="header">
    <a href="${baseURL}/shares">
        <div class="logo"></div>
    </a>
</div>

<div class="name"><a href="${baseURL}/">${h.NAME}</a></div>

<div class="navigation section">
    <div><a href="${baseURL}/noadmin"><i class="icon fas fas fa-lock-open"></i></a></div>
    <div class="files" data-toggle="tooltip" title="Files"><a href="/" target="_files"><i class="icon fas fa-folder-open"></i></a></div>
    %if tracking:
        <div class="tracking" data-toggle="tooltip" title="Tracking"><a href="/tracking" target="_tracking"><i class="icon fas fa-glasses"></i></a></div>
    %endif
</div>

    %for alert in alerts:
        <div class="alert">
            <h2>${alert[0]}</h2>
            <p>${alert[1]}</p>
        </div>
    %endfor



<div class="block section">
    <div class="section-title">Create share</div>
    %if len(containers)>0:
        <div class="warning">Warning: You share contains one or more folder. <br/>All sub files and folders of <i>${containersDisplay}</i> will be accessible from this share.</div>
    %endif


    <form method="post">
        <input readonly type="text" placeholder="${pathsDisplay}"/>
        <input type="text" id="shareID" name="shareID" placeholder="Share ID* (default: ${defaultShareID})" value="${shareID}" spellcheck="false" autocorrect="off" autocapitalize="none"/>
        <input type="hidden" name="defaultShareID" value="${defaultShareID}"/>
        <input type="text" name="duration" placeholder="Duration in days" value="${duration}" spellcheck="false" autocorrect="off" autocapitalize="none"/>
        <input type="password" name="password-share-add" placeholder="Password" value="" autocomplete="new-password"/>
        % if needForce:
            <input type="submit" name="create-share-force-submit" value="Override share"/>
        %else:
            <input type="submit" name="create-share-submit" value="Create share"/>
        % endif
        <input type="submit" name="create-share-cancel" class="cancel" value="Abort"/>
    </form>
</div>

<div class="footer">${h.NAME} - ${h.CREDITS}</div>

<script>
    $(document).ready(function () {
        $("#shareID").focus();
        $('input[name="create-share-cancel"]').on("click", function (e) {
            e.preventDefault();
            console.log(window.history);
            if (window.history.length === 1) window.close();
            else window.history.back();
        })
    });
</script>

</body>
</html>