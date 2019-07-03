<!DOCTYPE html>
<html>
<head>
    <script src="${baseURL}/_sf_assets/jquery.js"></script>
    <script src="${baseURL}/_sf_assets/stupidtable.js"></script>
    <script src="${baseURL}/_sf_assets/tooltipstr.js"></script>
    <script src="${baseURL}/_sf_assets/helpers.js"></script>
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.3.0/css/all.css">
    <link rel="stylesheet" href="${baseURL}/_sf_assets/tooltipster.css">
    <link rel="stylesheet" href="${baseURL}/_sf_assets/tooltipster-theme.css">
    <link rel="stylesheet" href="${baseURL}/_sf_assets/style.css?ck=4">
    <link rel="icon" href="${baseURL}/_sf_assets/icon.png">
    <title>${h.NAME} - Admin - Shares</title>
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

    %if shareAdded is not None:
        <div class="alert">
            <h2>Share created</h2>
            <p>The share <i>${shareAdded.ID}</i> has been created for <i>${shareAdded.file}</i>.<br/>
                <a class="link copy-link" data-url="${rootURL}/share=${h.urlEncode(shareAdded.ID)}" data-password="${shareAdded.password}">Copy link</a>
            </p>
        </div>
    %endif

<div class="block section">
    <div class="section-title">Share lookup</div>
    <form method="post" action="/shares" class="inline">
        <input type="text" id="filterShareID" name="filterShareID" value="${filterShareID}" placeholder="share (partial) ID or share url"/>
        <label></label><input type="submit" name="filter-share-submit" value="Filter" style="width:100px;"/>
    </form>
</div>

<div class="shares section">
    %if filterShareID !="":
        <div class="section-title">Shares found</div>
    %else:
        <div class="section-title">Latest ${min(maxShares, len(shares))} shares</div>
    %endif

    <table>
        <thead>
        <tr>
            <th data-sort="string-ins">ID</th>
            <th data-sort="string-ins">File</th>
            <th data-sort="string-ins" width="130">Expiration</th>
            <th data-sort="string-ins">Password</th>
            <th data-sort="int" width="50"># views</th>
            <th data-sort="string-ins" width="130">Latest</th>
            <th width="70">Actions</th>
        </tr>
        </thead>
        <tbody>
            <% i = 0%>
            %for share in shares:
                <% shareURL = "ok"%>
                <% evenClass = "even" if i % 2 == 1 else "odd"%>
                <% shareExpires = "Never" if share.duration==0 else h.formatTimestamp(share.duration+share.creation, "YYYY/MM/DD HH:mm")%>
                <% shareIDEncoded = h.urlEncode(share.ID)%>
                <tr class="${evenClass}">
                    <td onclick="window.open('${rootURL}/share=${shareIDEncoded}')">${share.ID}</td>
                    <td onclick="window.open('${rootURL}/share=${shareIDEncoded}')">${share.file}</td>
                    <td onclick="window.open('${rootURL}/share=${shareIDEncoded}')">${shareExpires}</td>
                    <td onclick="window.open('${rootURL}/share=${shareIDEncoded}')">${share.password}</td>
                    <td onclick="window.open('${rootURL}/share=${shareIDEncoded}')">${len(share.views)}</td>
                    <td>
                        %if len(share.views)>0:
                        ${h.formatTimestamp(share.views[0]["date"], "YYYY/MM/DD HH:mm")}
                        %endif
                    </td>
                    <td class="actions">
                        <a class="link copy-link" data-url="${rootURL}/share=${shareIDEncoded}" data-password="${share.password}" data-toggle="tooltip" title="Copy link"><i class="icon fas fa-link"></i></a>
                        <a data-toggle="tooltip" title="Details" href="${rootURL}/share=${shareIDEncoded}" target="_share_${shareIDEncoded}"><i class="icon fas fa-search"></i></a>
                        <a data-toggle="tooltip" title="Remove" class="confirmation" href="${rootURL}/remove-share=${shareIDEncoded}"><i class="icon fas fa-trash"></i></a>
                    </td>
                </tr>
                <% i +=1%>
            %endfor
        </tbody>
    </table>

</div>


<script>
    $(document).ready(function () {
        window.name = "_shares";

        $("#filterShareID").focus();

        $('.confirmation').on('click', function () {
            return confirm('Are you sure?');
        });

        $('[data-toggle="tooltip"]').tooltipster({theme: "tooltipster-borderless", animationDuration: 200, delay: 20, side: "bottom"});
        var table = $("table").stupidtable();
        table.bind("aftertablesort", function (event, data) {
            var tableElt = data.$th.parent().parent().parent();
            tableElt.find("tr:even").addClass("even");
            tableElt.find("tr:odd").removeClass("even");
        });

        $(".copy-link").on("click", function () {
            var url = $(this).attr("data-url");
            var password = $(this).attr("data-password");
            var hasPassword = password !== "";
            var copied = hasPassword ? url + " (password: " + password + ")" : url;
            copyStringToClipboard(copied);
            var result = window.prompt("Link " + copied + " to clipboard.\n\nWant to add a tag ?");
            if (result == null || result === "") return;
            url = url + "?t=" + cleanStringForURL(result);
            copied = hasPassword ? url + " (password: " + password + ")" : url;
            copyStringToClipboard(copied);
            window.alert("Link " + copied + " to clipboard");
        });
    });
</script>


<div class="footer">${h.NAME} - ${h.CREDITS}</div>
</body>
</html>