<!DOCTYPE html>
<html>
<head>
    <script src="${baseURL}/_sf_assets/jquery.js"></script>
    <script src="${baseURL}/_sf_assets/stupidtable.js"></script>
    <script src="${baseURL}/_sf_assets/clipboard.js"></script>
    <script src="${baseURL}/_sf_assets/tooltipstr.js"></script>
    <script src="${baseURL}/_sf_assets/readmore.js"></script>
    <script src="${baseURL}/_sf_assets/cookie.js"></script>
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.3.0/css/all.css">
    <link rel="stylesheet" href="${baseURL}/_sf_assets/tooltipster.css">
    <link rel="stylesheet" href="${baseURL}/_sf_assets/tooltipster-theme.css">
    <link rel="stylesheet" href="${baseURL}/_sf_assets/style.css?ck=3">
    <title>${h.NAME} - Admin - /${path}</title>
</head>

<body>

<div class="admin-section">Admin section</div>

<div class="header">
    <a href="${baseURL}/">
        <div class="logo"></div>
    </a>
</div>

<div class="name"><a href="${baseURL}/">${h.NAME}</a></div>

<div class="navigation section">
    <div><a href="${baseURL}/noadmin"><i class="icon fas fas fa-lock-open"></i></a></div>
    %if tracking:
        <div class="tracking" data-toggle="tooltip" title="Tracking"><a href="/tracking" target="_tracking"><i class="icon fas fa-glasses"></i></a></div>
    %endif
    %if sharing:
        <div class="sharing" data-toggle="tooltip" title="Sharing"><a href="/shares" target="_shares"><i class="icon fas fa-share-alt-square"></i></a></div>
    %endif
    <div class="sep">|</div>
    <div class="parent" data-toggle="tooltip" title="Go to parent folder">
        %if path != "":
            <a href="${baseURL}/${path}/.."><i class="icon fas fa-long-arrow-alt-up"></i></a>
        %else:
            <a class="disabled"><i class="icon fas fa-long-arrow-alt-up"></i></a>
        % endif
    </div>
    <div class="page">/${path}</div>
</div>

    %for alert in alerts:
        <div class="alert">
            <h2>${alert[0]}</h2>
            <p>${alert[1]}</p>
        </div>
    %endfor

    % if readme is not None:
        <div class="block section">
            <div class="readme-content" id="readme-admin">${readme}</div>
        </div>
    % endif

    %if editAllowed:
        <div class="block section">
            <div class="section-title">Add a file</div>
            <form method="post" enctype="multipart/form-data" class="inline" action="${baseURL}/${path}">
                <input type="file" name="file">
                <label></label><input type="submit" name="add-leaf" value="Upload">
            </form>
        </div>
    %endif

    %if isProtected:
        <div class="block section">
            <div class="section-title">Add a password</div>
            % if isProtectedFromParent:
                Protected from parent folder, can't add password from this folder.
            % elif passwordEditForbidden:
                Can't edit password of this folder.
            % else:
                <form method="post" class="inline" action="${baseURL}/${path}">
                    <input type="text" name="new-password" placeholder="password to add" spellcheck="false" autocorrect="off" autocapitalize="none"/>
                    <label></label><input type="submit" name="add-password-submit" value="Add password" style="width:150px;"/>
                </form>
            %endif
        </div>
    %endif

    %if len(passwords)>1:
        <div class="block section">
            <div class="section-title">
                ${len(passwords)} passwords
            </div>
            <form method="post" class="inline" action="${baseURL}/${path}">
                <input type="text" id="search-password" placeholder="search for (partial) password" spellcheck="false" autocorrect="off" autocapitalize="none"/>
            </form>
            <div id="passwords">
                <% currentURL = h.urlEncode(h.makePath(rootURL, path))%>
                %for password in passwords:
                    <span data-password="${password}">${password} <a data-toggle="tooltip" title="Copy link + password" class="link" data-clipboard-text="${currentURL} (password: ${password})"><i class="icon fas fa-link"></i></a></span>
                %endfor
                <div id="no-found-passwords" style="display:none">No password found</div>
            </div>
        </div>
    %endif

    %if len(containers)+len(leafs)>10:
        <div class="block section">
            <div class="section-title">Filter items</div>
            <form method="post" class="inline" action="${baseURL}/${path}">
                <input type="text" id="search-item" placeholder="search for (partial) item"/>
            </form>
        </div>
    %endif


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
                    %if isTmpFolder:
                        <th data-sort="int" style="width:20%;">Expiration</th>
                    %endif
                    <th width="70">Actions</th>
                </tr>
                </thead>
                <tbody>
                <tr>
                    <% i = 0 %>
                    % for item in containers:
                        <% folderClass="fa-folder-plus" if item.editAllowed else "fa-folder"%>
                        <% evenClass = "even" if i % 2 == 1 else "odd" %>
                        <% urlEncodedPath = h.urlEncode(item.path)%>
                        <% shareURLEncoded=h.encode(item.path)%>
                        <% itemURL = h.urlEncode(h.makePath(rootURL , item.path.lstrip("/"))) %>
                        <% tooltipTitle = []%>
                        <% if item.protected: tooltipTitle.append("protected")%>
                        <% if item.forbidden: tooltipTitle.append("forbidden")%>
                        <% if item.showForbidden: tooltipTitle.append("hidden")%>
                        <% if item.listingForbidden: tooltipTitle.append("no listing")%>
                        <% if item.shareForbidden: tooltipTitle.append("no share")%>
                        <% if item.isTmpFolder: tooltipTitle.append("tmp folder")%>
                        <% if item.editAllowed: tooltipTitle.append("edit/upload allowed")%>
                        <% itemSpecial = len(tooltipTitle)>0 %>
                        <% toggleTooltip = "tooltip-left" if itemSpecial else ""%>
                        <% isAllowedClass = "disabled" if itemSpecial else ""%>
                        <tr class="item ${evenClass}" data-item="${item.name}" data-toggle="${toggleTooltip}" title="${", ".join(tooltipTitle)}">
                            <td onclick="location.href='${baseURL}/${urlEncodedPath}'"><i class="icon fas ${folderClass} ${isAllowedClass}"></i></td>
                            <td onclick="location.href='${baseURL}/${urlEncodedPath}'">${item.name}</td>
                            <td onclick="location.href='${baseURL}/${urlEncodedPath}'">${h.formatTimestamp(item.lastModified, "YYYY/MM/DD HH:mm")}</td>
                            <td onclick="location.href='${baseURL}/${urlEncodedPath}'">${item.nbItems}</td>
                            %if isTmpFolder:
                                <td onclick="location.href='$${baseURL}/{urlEncodedPath}'">${h.formatTimestamp(item.expires,"YYYY/MM/DD HH:mm")}</td>
                            %endif
                            <td class="actions">
                                % if item.protected:
                                    <a data-toggle="tooltip" title="Copy link + password" class="link" data-clipboard-text="${itemURL} (password: ${item.passwords[0]})"><i class="icon fas fa-link"></i></a>
                                %elif not item.listingForbidden:
                                    <a data-toggle="tooltip" title="Copy link" class="link" data-clipboard-text="${itemURL}"><i class="icon fas fa-link"></i></a>
                                %else:
                                    <a data-toggle="tooltip" title="Can't copy link" class="link disabled"><i class="icon fas fa-link"></i></a>
                                % endif
                                % if h.SHARING and not isTmpFolder:
                                    %if not item.shareForbidden:
                                        <a data-toggle="tooltip" title="Create share" href="${rootURL}/create-share=${shareURLEncoded}" target="_shares"><i class="icon fas fa-share-alt-square"></i></a>
                                    %else:
                                        <a data-toggle="tooltip" title="Can't share" class="link disabled"><i class="icon fas fa-share-alt-square"></i></a>
                                    % endif
                                % endif
                                % if editAllowed:
                                    <a data-toggle="tooltip" title="Remove" class="confirmation" href="${baseURL}/${urlEncodedPath}?remove"><i class="icon fas fa-trash"></i></a>
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
        <div class="leafs section">
            <div class="section-title">Files</div>
            <table class="noselect">
                <thead>
                <tr>
                    <th style="width:30px"></th>
                    <th data-sort="string-ins">Name</th>
                    <th data-sort="string-ins" style="width:20%;">Last modified</th>
                    <th data-sort="float" style="width:10%;">Size (mb)</th>
                    %if isTmpFolder:
                        <th data-sort="int" style="width:20%;">Expiration</th>
                    %endif
                    <th width="70">Actions</th>
                </tr>
                </thead>
                <tbody>
                <tr>
                    <% i = 0 %>
                    % for item in leafs:
                        <% evenClass = "even" if i % 2 == 1 else "odd"%>
                        <% sizeMB = h.floatFormat(item.size/1048576,1)%>
                        <% urlEncodedPath = h.urlEncode(item.path)%>
                        <% shareURLEncoded=h.encode(item.path)%>
                        <% itemURL = h.urlEncode(h.makePath(rootURL , item.path.lstrip("/"))) %>
                        <tr class="item ${evenClass}" data-item="${item.name}">
                            <td onclick="window.open('${baseURL}/${urlEncodedPath}')"><i class="icon ${h.EXTENSIONS_CLASSES.get(item.extension, h.EXTENSIONS_CLASSES["default"])}"></i></td>
                            <td onclick="window.open('${baseURL}/${urlEncodedPath}')">${item.name}</td>
                            <td onclick="window.open('${baseURL}/${urlEncodedPath}')">${h.formatTimestamp(item.lastModified, "YYYY/MM/DD HH:mm")}</td>
                            <td onclick="window.open('${baseURL}/${urlEncodedPath}')">${sizeMB}</td>
                            %if isTmpFolder:
                                <td onclick="location.href='${baseURL}/${urlEncodedPath}'">${h.formatTimestamp(item.expires,"YYYY/MM/DD HH:mm")}</td>
                            %endif
                            <td class="actions">
                                % if item.protected:
                                    <a data-toggle="tooltip" title="Copy link + password" class="link" data-clipboard-text="${itemURL} (password: ${item.passwords[0]})"><i class="icon fas fa-link"></i></a>
                                %else:
                                    <a data-toggle="tooltip" title="Copy link" class="link" data-clipboard-text="${itemURL}"><i class="icon fas fa-link"></i></a>
                                % endif
                                % if h.SHARING and not isTmpFolder:
                                    <a data-toggle="tooltip" title="Create share" href="${rootURL}/create-share=${shareURLEncoded}" target="_shares"><i class="icon fas fa-share-alt-square"></i></a>
                                % endif
                                % if editAllowed:
                                    <a data-toggle="tooltip" title="Remove" class="confirmation" href="$${baseURL}/{urlEncodedPath}?remove"><i class="icon fas fa-trash"></i></a>
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

        var adminViewCount = Cookies.get("admin-${path}");
        if (adminViewCount === undefined) adminViewCount = 0;
        adminViewCount++;
        Cookies.set("admin-${path}", adminViewCount);
        if (adminViewCount > 5) {$("#readme-admin").readmore({collapsedHeight: 40});}

        var clipboard = new ClipboardJS(".link");
        clipboard.on('success', function (e) {
            alert("Link " + e.text + " copied to clipboard")
        });

        $('.confirmation').on('click', function () {
            return confirm('Are you sure?');
        });

        $('[data-toggle="tooltip"]').tooltipster({theme: "tooltipster-borderless", animationDuration: 200, delay: 20, side: "bottom"});
        $('[data-toggle="tooltip-left"]').tooltipster({theme: "tooltipster-borderless", animationDuration: 200, delay: 20, side: "left"});
        var table = $("table").stupidtable();
        table.bind("aftertablesort", function (event, data) {
            var tableElt = data.$th.parent().parent().parent();
            tableElt.find("tr:even").addClass("even");
            tableElt.find("tr:odd").removeClass("even");
        });

        var readMoreOptions = {collapsedHeight: 50, moreLink: '<a href="#" class="readmore">View all</a>', lessLink: '<a href="#" class="readmore">Collapse</a>'};
        $("#passwords").readmore(readMoreOptions);
        $("#search-item").keyup(function () {
            var itemSearch = this.value.toLowerCase();
            $(".leafs").hide();
            $(".containers").hide();
            $(".leafs tr.item").hide();
            $(".containers tr.item").hide();
            $(".leafs tr.item").each(function (i, a) {
                var potentialItem = $(this).attr("data-item").toLowerCase();
                if (potentialItem.indexOf(itemSearch) !== -1) {
                    $(this).show();
                    $(".leafs").show();
                }
            });
            $(".containers tr.item").each(function (i, a) {
                var potentialItem = $(this).attr("data-item").toLowerCase();
                if (potentialItem.indexOf(itemSearch) !== -1) {
                    $(this).show();
                    $(".containers").show();
                }
            });
        });

        $("#search-password").keyup(function () {
            var passwordSearch = this.value.toLowerCase();
            $("#passwords").readmore("destroy");
            $("#passwords span").hide();
            $("#no-found-passwords").hide();
            var found = 0;
            $("#passwords span").each(function (i, a) {
                var potentialPassword = $(this).attr("data-password").toLowerCase();
                if (potentialPassword.indexOf(passwordSearch) !== -1) {
                    $(this).show();
                    found++;
                }
            });
            if (found == 0) {$("#no-found-passwords").show();}
            $("#passwords").readmore(readMoreOptions);
        });

    });
</script>

</body>
</html>