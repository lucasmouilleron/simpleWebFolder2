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
    <title>${h.NAME} - admin - /${path}</title>
</head>

<body>

<div class="header">
    <a href="${baseURL}/">
        <div class="logo"></div>
    </a>
</div>

<div class="name"><a href="${baseURL}/">${h.NAME}</a></div>

<div class="navigation section">
    <div><a href="${baseURL}/noadmin"><i class="icon fas fas fa-lock-open"></i></a> |</div>
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
                    <th width="70">Actions</th>
                </tr>
                </thead>
                <tbody>
                <tr>
                    <% i = 0 %>
                    % for item in containers:
                        <% evenClass = "even" if i % 2 == 1 else "odd" %>
                        <% urlEncodedPath = h.urlEncode(item["path"])%>
                        <% isAllowedClass = "disabled" if item["protected"] else ""%>
                        <% itemURL = h.urlEncode(h.makePath(rootURL , item["path"].lstrip("/"))) %>
                        <tr class="${evenClass}">
                            <td onclick="location.href='${urlEncodedPath}'"><i class="icon fas fa-folder ${isAllowedClass}"></i></td>
                            <td onclick="location.href='${urlEncodedPath}'">${item["name"]}</td>
                            <td onclick="location.href='${urlEncodedPath}'">${h.formatTimestamp(item["lastModified"], "YYYY/MM/DD HH:mm")}</td>
                            <td onclick="location.href='${urlEncodedPath}'">${item["nbItems"]}</td>
                            <td>
                                % if item["protected"]:
                                    <a data-toggle="tooltip" title="Copy link + password" class="link" data-clipboard-text="${itemURL} (password: ${item["passwords"][0]})"><i class="icon fas fa-link"></i></a>
                                %else:
                                    <a data-toggle="tooltip" title="Copy link" class="link" data-clipboard-text="${itemURL}"><i class="icon fas fa-link"></i></a>
                                % endif
                            </td>
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
                    <th width="70">Actions</th>
                </tr>
                </thead>
                <tbody>
                <tr>
                    <% i = 0 %>
                    % for item in leafs:
                        <% evenClass = "even" if i % 2 == 1 else "odd"%>
                        <% sizeMB = h.floatFormat(item["size"]/1048576,1)%>
                        <% urlEncodedPath = h.urlEncode(item["path"])%>
                        <% itemURL = h.urlEncode(h.makePath(rootURL , item["path"].lstrip("/"))) %>
                        <tr class="${evenClass}">
                            <td onclick="window.open('${urlEncodedPath}')"><i class="icon ${h.EXTENSIONS_CLASSES.get(item["extension"], h.EXTENSIONS_CLASSES["default"])}"></i></td>
                            <td onclick="window.open('${urlEncodedPath}')">${item["name"]}</td>
                            <td onclick="window.open('${urlEncodedPath}')">${h.formatTimestamp(item["lastModified"], "YYYY/MM/DD HH:mm")}</td>
                            <td onclick="window.open('${urlEncodedPath}')">${sizeMB}</td>
                            <td>
                                % if item["protected"]:
                                    <a data-toggle="tooltip" title="Copy link + password" class="link" data-clipboard-text="${itemURL} (password: ${item["passwords"][0]})"><i class="icon fas fa-link"></i></a>
                                %else:
                                    <a data-toggle="tooltip" title="Copy link" class="link" data-clipboard-text="${itemURL}"><i class="icon fas fa-link"></i></a>
                                % endif
                            </td>
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
        window.name = "_files";

        var clipboard = new ClipboardJS(".link");
        clipboard.on('success', function (e) {
            alert("Link " + e.text + " copied to clipboard")
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

</body>
</html>