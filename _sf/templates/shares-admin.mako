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
    <link rel="stylesheet" href="${baseURL}/_sf_assets/style.css?ck=2">
    <title>${h.NAME} - Admin - Shares</title>
</head>

<body>

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
            <th data-sort="string-ins" width="160">Expiration</th>
            <th data-sort="string-ins">Password</th>
            <th data-sort="int" width="50"># views</th>
            <th data-sort="string-ins" width="160">Latest</th>
            <th width="70">Actions</th>
        </tr>
        </thead>
        <tbody>
            <% i = 0%>
            %for share in shares:
                <% shareURL = "ok"%>
                <% evenClass = "even" if i % 2 == 1 else "odd"%>
                <% shareExpires = "Never" if share.duration==0 else h.formatTimestamp(share.duration+share.creation, "YYYY/MM/DD HH:mm")%>
                <tr class="${evenClass}">
                    <td>${share.ID}</td>
                    <td onclick="window.open('/${share.file}')"><a>${share.file}</a></td>
                    <td>${shareExpires}</td>
                    <td>${share.password}</td>
                    <td>${len(share.views)}</td>
                    <td>
                        %if len(share.views)>0:
                        ${h.formatTimestamp(share.views[-1]["date"], "YYYY/MM/DD HH:mm")}
                        %endif
                    </td>
                    <td class="actions">
                        <% shareIDEncoded = h.urlEncode(share.ID)%>
                        % if share.password!="":
                            <a class="link" data-clipboard-text="${rootURL}/share=${shareIDEncoded} (password: ${share.password})" data-toggle="tooltip" title="Copy link"><i class="icon fas fa-link"></i></a>
                        %else:
                            <a class="link" data-clipboard-text="${rootURL}/share=${shareIDEncoded}" data-toggle="tooltip" title="Copy link"><i class="icon fas fa-link"></i></a>
                        % endif

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

        var clipboard = new ClipboardJS(".link");
        clipboard.on('success', function (e) {
            alert("Link " + e.text + " copied to clipboard")
        });

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
    });
</script>


<div class="footer">${h.NAME} - ${h.CREDITS}</div>
</body>
</html>