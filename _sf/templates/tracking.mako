<!DOCTYPE html>
<html>
<head>
    <script src="${baseURL}/_sf_assets/jquery.js"></script>
    <script src="${baseURL}/_sf_assets/stupidtable.js"></script>
    <script src="${baseURL}/_sf_assets/tooltipstr.js"></script>
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.3.0/css/all.css">
    <link rel="stylesheet" href="${baseURL}/_sf_assets/tooltipster.css">
    <link rel="stylesheet" href="${baseURL}/_sf_assets/tooltipster-theme.css">
    <link rel="stylesheet" href="${baseURL}/_sf_assets/style.css?ck=4">
    <link rel="icon" href="${baseURL}/_sf_assets/icon.png">
    <title>${h.NAME} - Admin - Tracking</title>
</head>

<body class="admin">

<div class="admin-section">Admin section</div>

<div class="header">
    <a href="${baseURL}/tracking">
        <div class="logo"></div>
    </a>
</div>

<div class="name"><a href="${baseURL}/">${h.NAME}</a></div>

<div class="navigation section">
    <div><a href="${baseURL}/noadmin"><i class="icon fas fas fa-lock-open"></i></a></div>
    <div class="files" data-toggle="tooltip" title="Files"><a href="/" target="_files"><i class="icon fas fa-folder-open"></i></a></div>
    %if sharing:
        <div class="sharing" data-toggle="tooltip" title="Sharing"><a href="/shares" target="_shares"><i class="icon fas fa-share-alt-square"></i></a></div>
    %endif
</div>

<div class="block section">
    <div class="section-title">Filter</div>
    <form method="post" class="inline" action="tracking">
        <label>Limit</label>
        <select name="maxItems">
            <option ${"SELECTED" if maxItems == "500" else ""}>500</option>
            <option ${"SELECTED" if maxItems == "1000" else ""}>1000</option>
            <option ${"SELECTED" if maxItems == "all" else ""}>all</option>
        </select>
        <label>Protected</label>
        <select name="protected">
            <option ${"SELECTED" if protected == "yes" else ""}>yes</option>
            <option ${"SELECTED" if protected == "no" else ""}>no</option>
            <option ${"SELECTED" if protected == "all" else ""}>all</option>
        </select>
        <label></label><input type="text" name="password" value="${password}" placeholder="Password" style="width:200px;"/>
        <label></label><input type="text" id="item" name="item" value="${item}" placeholder="Item" style="width:200px;"/>
        <label></label><input type="submit" name="filter" value="Filter" style="width:100px;"/>
    </form>
</div>

<div class="trackings section">
    <div class="section-title">${len(trackings)} trackings</div>
    <table>
        <thead>
        <tr>
            <th data-sort="string-ins">Item</th>
            <th data-sort="string-ins" width="70">Protected</th>
            <th data-sort="string-ins" width="70">Authorized</th>
            <th data-sort="string-ins" width="140">Password</th>
            <th data-sort="string-ins" width="120">IP</th>
            <th data-sort="string-ins" width="120">Location</th>
            <th data-sort="string-ins" width="140">Date</th>
        </tr>
        </thead>
        <tbody>
            <% i = 0%>
            % for tracking in trackings:
                <% evenClass = "even" if i % 2 == 1 else "odd" %>
                <tr class="${evenClass}">
                    <td style="max-width:400px;word-wrap: break-word;">${tracking.path}</td>
                    <td style="text-align: center">${tracking.protected}</td>
                    <td style="text-align: center">${tracking.authorized}</td>
                    <td>${tracking.password}</td>
                    <td>${tracking.ip}</td>
                    <td>${tracking.location}</td>
                    <td>${h.formatTimestamp(tracking.date, "YYYY/MM/DD HH:mm")}</td>
                </tr>
                <% i+=1 %>
            %endfor
        </tbody>
    </table>
</div>

<div class="footer">${h.NAME} - ${h.CREDITS}</div>

<script>
    $(document).ready(function () {
        window.name = "_tracking";

        $("#item").focus();

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