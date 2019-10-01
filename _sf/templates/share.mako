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
    <title>${h.NAME} - Share ${share.ID}</title>
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
        %if subPath != "":
            <% url = h.makeURL("/share=%s/%s/.."%(share.ID,subPath), query)%>
            <a href="${url}"><i class="icon fas fa-long-arrow-alt-up"></i></a>
        %else:
            <a class="disabled"><i class="icon fas fa-long-arrow-alt-up"></i></a>
        % endif
    </div>
    <div class="page">/${displayPath}</div>
</div>

    %for alert in alerts:
        <div class="alert">
            <h2>${alert[0]}</h2>
            <p>${alert[1]}</p>
        </div>
    %endfor

    % if readme is not None:
        <div class="block section">
            <div class="readme-content">${readme}</div>
        </div>
    % endif


    % if len(containers)>0:
        <div class="containers section">
            <div class="section-title">Folders</div>
            <table class="noselect">
                <thead>
                <tr>
                    <th style="width:30px"></th>
                    <th data-sort="string-ins">Name</th>
                    <th data-sort="string-ins" style="width:20%;">Last modified</th>
                    <th data-sort="int" style="width:10%;"># items</th>
                </tr>
                </thead>
                <tbody>
                <tr>
                    <% i = 0 %>
                    % for item in containers:
                        <% evenClass = "even" if i % 2 == 1 else "odd" %>
                        <% urlEncodedURL = h.makeURL(h.urlEncode(h.cleanURL(item.path.replace(shareBasePath,"")).lstrip("/")), query)%>
                        <tr onclick="location.href='/share=${share.ID}/${urlEncodedURL}'" class="${evenClass}">
                            <td><i class="icon fas fa-folder"></i></td>
                            <td>${item.name}</td>
                            <td>${h.formatTimestamp(item.lastModified, "YYYY/MM/DD HH:mm")}</td>
                            <td>${item.nbItems}</td>
                        </tr>
                        <% i+=1 %>
                    % endfor
                </tbody>
            </table>
        </div>
    % endif

    % if len(leafs)>0:
        <div class="leafs section">
            <div class="section-title">Files</div>
            <table class="noselect">
                <thead>
                <tr>
                    <th style="width:30px"></th>
                    <th data-sort="string-ins">Name</th>
                    <th data-sort="string-ins" style="width:20%;">Last modified</th>
                    <th data-sort="float" style="width:10%;">Size (mb)</th>
                </tr>
                </thead>
                <tbody>
                <tr>
                    <% i = 0 %>
                    % for item in leafs:
                        <% evenClass = "even" if i % 2 == 1 else "odd"%>
                        <% sizeMB = h.floatFormat(item.size/1048576,1)%>
                        <% urlEncodedURL = h.makeURL(h.urlEncode(h.cleanURL(item.path.replace(shareBasePath,"")).lstrip("/")), query)%>
                        <tr onclick="window.open('/share=${share.ID}/${urlEncodedURL}')" class="${evenClass}">
                            <td><i class="icon ${h.EXTENSIONS_CLASSES.get(item.extension, h.EXTENSIONS_CLASSES["default"])}"></i></td>
                            <td>${item.name}</td>
                            <td>${h.formatTimestamp(item.lastModified, "YYYY/MM/DD HH:mm")}</td>
                            <td>${sizeMB}</td>
                        </tr>
                        <% i+=1 %>
                    % endfor
                </tbody>
            </table>
        </div>
    % endif

<div class="footer">${h.NAME} - ${h.CREDITS}</div>

<script>
    $(document).ready(function () {
        window.name = "_share_${share.ID}";

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