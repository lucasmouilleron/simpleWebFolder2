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
    <title>${h.NAME} - Admin - Share ${share["ID"]}</title>
</head>

<body>

<div class="header">
    <a href="${baseURL}/">
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

<div class="share section">
    <div class="section-title">Share ${share["ID"]}</div>
    <% shareExpires = "Never" if share.get("duration",0)==0 else h.formatTimestamp(share["duration"]+share["creation"], "YYYY/MM/DD HH:mm")%>
    <table>
        <thead>
        <tr>
            <th>ID</th>
            <th>Link</th>
            <th>File</th>
            <th>Expiration</th>
            <th>Password</th>
            <th># views</th>
        </tr>
        </thead>
        <tbody>

        <tr>
            <td>${share["ID"]}</td>
            <td></td>
            <td onclick="window.open('/${share["file"]}')"><a>${share["file"]}</a></td>
            <td>${shareExpires}</td>
            <td>${share["password"]}</td>
            <td>${len(share.get("views", []))}</td>
        </tr>
        </tbody>
    </table>
</div>

<div class="views section">
    <div class="section-title">Share ${share["ID"]} views</div>
    <table>
        <thead>
        <tr>
            <th data-sort="string-ins" width="200">IP</th>
            <th data-sort="string-ins" width="160">Date</th>
            <th data-sort="string-ins">Item</th>
        </tr>
        </thead>
        <tbody>
            <% i = 0 %>
            %for view in share.get("views",[]):
                <% evenClass = "even" if i % 2 == 1 else "odd" %>
                <tr class="${evenClass}">
                    <td>${view["ip"]}</td>
                    <td>${h.formatTimestamp(view["date"], "YYYY/MM/DD HH:mm")}</td>
                    <td>${view["item"]}</td>
                </tr>
                <% i+=1 %>
            %endfor
        </tbody>
    </table>
</div>


<div class="footer">${h.NAME} - ${h.CREDITS}</div>

<script>
    $(document).ready(function () {
        window.name = "_share_${share["ID"]}";

        $('[data-toggle="tooltip"]').tooltipster({theme: "tooltipster-borderless", animationDuration: 200, delay: 20, side: "bottom"});
        var table = $("table").stupidtable();
        table.bind("aftertablesort", function (event, data) {
            var tableElt = data.$th.parent().parent().parent();
            tableElt.find("tr:even").addClass("even");
            tableElt.find("tr:odd").removeClass("even");
        });
    });
</script>

</body>
</html>