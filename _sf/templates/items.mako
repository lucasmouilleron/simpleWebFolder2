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
    <title>${h.NAME} - /${path}</title>
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
    %if downloadAllowed:
        <div id="download" data-toggle="tooltip" title="Download folder"><a href="${path}?download"><i class="icon fas fa-download"></i></a></div>
    %endif
    <div class="page">${path}</div>
</div>

    %for alert in alerts:
        <div class="alert">
            <h2>${alert[0]}</h2>
            <p>${alert[1]}</p>
        </div>
    %endfor

    % if readme is not None:
        <div class="readme section">
            <div class="readme-content">${readme}</div>
        </div>
    % endif


    % if len(containers)>0:
        <div class="folders section">
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
                        <% urlEncodedURL = h.urlEncode(item["path"])%>
                        <% isAllowedClass = "disabled" if not item["isAuthorized"] else ""%>
                        <tr onclick="location.href='${urlEncodedURL}'" class="${evenClass}">
                            <td><i class="icon fas fa-folder ${isAllowedClass}"></i></td>
                            <td>${item["name"]}</td>
                            <td>${h.formatTimestamp(item["lastModified"], "YYYY/MM/DD HH:mm")}</td>
                            <td>${item["nbItems"]}</td>
                        </tr>
                        <% i+=1 %>
                    % endfor
                </tbody>
            </table>
        </div>
    % endif

    % if len(leafs)>0:
        <div class="files section">
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
                        <% sizeMB = h.floatFormat(item["size"]/1048576,1)%>
                        <% urlEncodedURL = h.urlEncode(item["path"])%>
                        <tr onclick="window.open('${urlEncodedURL}')" class="${evenClass}">
                            <td><i class="icon ${h.EXTENSIONS_CLASSES.get(item["extension"], h.EXTENSIONS_CLASSES["default"])}"></i></td>
                            <td>${item["name"]}</td>
                            <td>${h.formatTimestamp(item["lastModified"], "YYYY/MM/DD HH:mm")}</td>
                            <td>${sizeMB}</td>
                        </tr>
                        <% i+=1 %>
                    % endfor
                </tbody>
            </table>
        </div>
    % endif

<div class="footer">${h.NAME} - ${h.CREDITS}</div>
</body>
</html>