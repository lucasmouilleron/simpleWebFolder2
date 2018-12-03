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
    <title>${h.NAME} - Tracking</title>
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
    %if sharing:
        <div class="sharing" data-toggle="tooltip" title="Sharing"><a href="/shares" target="_shares"><i class="icon fas fa-link"></i></a></div>
    %endif
</div>

<div class="trackings-filter section">
    <div class="section-title">Filter</div>
    <form method="post" class="inline">
        <label>Limit</label><select name="maxItems">
        <option ${"SELECTED" if maxItems == 500 else ""}>500</option>
        <option ${"SELECTED" if maxItems == 1000 else ""}>1000</option>
        <option ${"SELECTED" if maxItems == all else ""}>all</option>
    </select>
        <label></label><input type="text" name="password" value="${password}" placeholder="Password" style="width:200px;"/>
        <label></label><input type="text" name="item" value="${item}" placeholder="Item" style="width:200px;"/>
        <label></label><input type="submit" name="filter" value="Filter" style="width:100px;"/>
    </form>
</div>

<div class="trackings section">
    <div class="section-title">Trackings</div>
    <table>
        <thead>
        <tr>
            <th data-sort="string-ins">Item</th>
            <th data-sort="string-ins" width="200">Password</th>
            <th data-sort="string-ins" width="100">Authorized</th>
            <th data-sort="string-ins" width="140">IP</th>
            <th data-sort="string-ins" width="160">Date</th>
        </tr>
        </thead>
        <tbody>
            <% i = 0%>
            % for tracking in trackings:
                <% evenClass = "even" if i % 2 == 1 else "odd" %>
                <tr class="${evenClass}">
                    <td>item</td>
                    <td>item</td>
                    <td>item</td>
                    <td>item</td>
                    <td>item</td>
                </tr>
                <% i+=1 %>
            %endfor
        </tbody>
    </table>
</div>

<div class="footer">${h.NAME} - ${h.CREDITS}</div>
</body>
</html>