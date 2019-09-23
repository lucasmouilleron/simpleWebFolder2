<!DOCTYPE html>
<html>
<head>
    <script src="${baseURL}/_sf_assets/jquery.js"></script>
    <script src="${baseURL}/_sf_assets/stupidtable.js"></script>
    <script src="${baseURL}/_sf_assets/tooltipstr.js"></script>
    <script src="${baseURL}/_sf_assets/helpers.js?ck=5"></script>
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.3.0/css/all.css">
    <link rel="stylesheet" href="${baseURL}/_sf_assets/tooltipster.css">
    <link rel="stylesheet" href="${baseURL}/_sf_assets/tooltipster-theme.css">
    <link rel="stylesheet" href="${baseURL}/_sf_assets/style.css?ck=6">
    <link rel="icon" href="${baseURL}/_sf_assets/icon.png">
    <title>${h.NAME} - Admin - Share ${share.ID}</title>
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

<div class="share section">
    <div class="section-title">Share ${share.ID}</div>
    <% shareExpires = "Never" if share.duration==0 else h.formatTimestamp(share.duration+share.creation, "YYYY/MM/DD HH:mm")%>
    <% shareIDEncoded = h.urlEncode(share.ID)%>
    <% files = ", ".join(share.files)%>
    <table>
        <thead>
        <tr>
            <th>ID</th>
            <th>Files</th>
            <th>Expiration</th>
            <th>Password</th>
            <th># views</th>
            <th width="70">Actions</th>
        </tr>
        </thead>
        <tbody>

        <tr>
            <td>${share.ID}</td>
            <td>
                <ul>
                    %for file in share.files:
                        <li><a href="${file}" target="${file}">${file}</a></li>
                    %endfor
                </ul>
            </td>
            <td>${shareExpires}</td>
            <td>${share.password}</td>
            <td>${len(share.views)}</td>
            <td>
                <a class="link copy-link" data-url="${rootURL}/share=${shareIDEncoded}" data-password="${share.password}" data-toggle="tooltip" title="Copy link"><i class="icon fas fa-link"></i></a>
                <a data-toggle="tooltip" title="Remove" class="confirmation" href="${rootURL}/remove-share=${shareIDEncoded}"><i class="icon fas fa-trash"></i></a>
            </td>
        </tr>
        </tbody>
    </table>
</div>

<div class="views section">
    <div class="section-title">Share ${share.ID} views</div>
    <table>
        <thead>
        <tr>
            <th data-sort="string-ins" width="120">IP</th>
            <th data-sort="string-ins" width="120">Location</th>
            <th data-sort="string-ins" width="120">Tag</th>
            <th data-sort="string-ins" width="150">Date</th>
            <th data-sort="string-ins">Item</th>
        </tr>
        </thead>
        <tbody>
            <% i = 0 %>
            %for view in share.views:
                <% evenClass = "even" if i % 2 == 1 else "odd" %>
                <tr class="${evenClass}">
                    <td>${view["ip"]}</td>
                    <td>${view["location"]}</td>
                    <td>${view.get("tag","")}</td>
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
        window.name = "_share_${share.ID}";

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

</body>
</html>