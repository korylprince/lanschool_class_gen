//addes endsWith function in all browsers
String.prototype.endsWith = function(suffix) {
    return this.indexOf(suffix, this.length - suffix.length) !== -1;
};

// takes data in form of selector -> html
// replaces selector with html
function rewrite(data) {
    for (var key in data) {
        if (data.hasOwnProperty(key)) {
            $(key).replaceWith(data[key]);
        }
    }
}

function get_url(url) {
    var base = window.location.pathname;
    if ( base.endsWith("/") ) {
        return base + url;
    }
    else {
        return base + "/" + url;
    }
}

function alertWarning(target) {
    var html = 
        '<div class="alert alert-warning alert-dismissable col-md-4 col-md-offset-4"> \
          <button type="button" class="close" data-dismiss="alert">&times;</button> \
            <strong>Oops!</strong> Your session expired. Please refresh the page or click <a href="/">here</a>. \
            </div>';
    $(target).after(html);
}

function alertDanger(target) {
    var html = 
        '<div class="alert alert-danger alert-dismissable col-md-4 col-md-offset-4"> \
          <button type="button" class="close" data-dismiss="alert">&times;</button> \
            <strong>Uh oh!</strong> Something went wrong. You can try refreshing the page or click <a href="/">here</a>. \
            If that doesn\'t work try contacting your system administrator. \
            </div>';
    $(target).after(html);
}

function alertBox(target) {
    return function (jqXHR) {
        if (jqXHR.status == 400) {
            alertWarning(target);
        }
        else {
            alertDanger(target);
        }
    }
}


// Login Button
$("body").on('submit','#login-form', function(e){
    e.preventDefault();
    $(this).children("#login-button").html('<span class="glyphicon glyphicon-cog icon-spin"></span>');
    $.ajax({
        type: "POST",
        url: get_url("login"),
        data: $("#login-form").serialize(),
        success: rewrite,
        error: alertBox("#login-wrapper"),
        dataType: "json"
    });
});

// Logout Link
$("body").on('click','#logout-link', function(e){
    e.preventDefault();
    $.ajax({
        type: "POST",
        url: get_url("logout"),
        success: rewrite,
        error: alertBox("#search-wrapper"),
        dataType: "json"
    });
});

// Student Search Button
$("body").on('submit','#add-student-form', function(e){
    e.preventDefault();
    $(this).children("#add-student-button").html('<span class="glyphicon glyphicon-cog icon-spin"></span>');
    $.ajax({
        type: "POST",
        url: get_url("add"),
        data: $("#add-student-form").serialize(),
        success: rewrite,
        error: alertBox("#search-wrapper"),
        dataType: "json"
    });
});

// Student Selection Add Button
$("body").on('click','.selection-button', function(e){
    e.preventDefault();
    var orig = encodeURIComponent($("#add-student-form input[name='search']").val());
    var data = {
        "csrf_token": $("#add-student-form input[name='csrf_token']").val(),
        "search": $(this).data("username"),
        "original": $("#add-student-form input[name='search']").val()
    };
    $(this).html('<span class="glyphicon glyphicon-cog icon-spin"></span>');
    $.ajax({
        type: "POST",
        url: get_url("add"),
        data: data,
        success: rewrite,
        error: alertBox("#search-wrapper"),
        dataType: "json"
    });
});

// Student Delete Button
$("body").on('click','.student-button', function(e){
    e.preventDefault();
    var data = {
        "csrf_token": $("#student-wrapper input[name='csrf_token']").val(),
        "username": $(this).data("username")
    };
    $(this).html('<span class="glyphicon glyphicon-cog icon-spin"></span>');
    $.ajax({
        type: "POST",
        url: get_url("delete"),
        data: data,
        success: rewrite,
        error: alertBox("#search-wrapper"),
        dataType: "json"
    });
});

// Hover Danger
function setDanger(item) {
    $(item).removeClass("btn-primary");
    $(item).addClass("btn-danger");
}

function unsetDanger(item) {
    $(item).removeClass("btn-danger");
    $(item).addClass("btn-primary");
}

$("body").on('mouseenter','.student-button', function(){setDanger(this);});
$("body").on('mouseleave','.student-button', function(){unsetDanger(this);});

// Student Delete All Button
$("body").on('click','#delete-all-button', function(e){
    e.preventDefault();
    var data = {
        "csrf_token": $("#student-wrapper input[name='csrf_token']").val(),
        "username": "all"
    };
    $("#delete-all-modal").modal("hide");
    $("#student-delete-all-button").html('<span class="glyphicon glyphicon-cog icon-spin"></span>');
    $.ajax({
        type: "POST",
        url: get_url("delete"),
        data: data,
        success: rewrite,
        error: alertBox("#search-wrapper"),
        dataType: "json"
    });
});

// Help Buttons
$("body").on('click','.help', function(e){
    var name = $(this).attr("id").split("-")[1];
    $("#help-modal .modal-body div").addClass("hide");
    $("#help-text-"+name).removeClass("hide");
    $("#help-modal").modal("show");
});
