//Moein
//Send Factor User Sender
$("#alert-div-inputPost_UserSend-empty").hide();
//User Sender Just Input Persian
$("#alert-div-inputPost_UserSend-just_persian").hide();


//AmIR
//Product To Send
$("#alert-div-inputpost-product-to-send-empty").hide();
$("#alert-div-inputpost-product-to-send-limit").hide();

//Barcode
$("#alert-div-inputpost-barcode-empty").hide();
$("#alert-div-inputpost-barcode-24char").hide();

//SendPrice
$("#alert-div-inputpost-sendprice-minlength").hide();
$("#alert-div-inputpost-sendprice-empty").hide();

//SendDate
$("#alert-div-inputpost-senddate-empty").hide();

//Moein
//Send Factor User Sender
$("#alert-div-inputPost_UserSend-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
	'<i class="far fa-exclamation-circle"></i>' +
	'<p>نام ارسال کننده مرسوله نمی تواند خالی باشد.</p>' +
    '</div></div>');
    
//User Sender Just Input Persian
$("#alert-div-inputPost_UserSend-just_persian").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
	'<i class="far fa-exclamation-circle"></i>' +
	'<p>نام ارسال کننده مرسوله فقط باید فارسی باشد.</p>' +
    '</div></div>');


//AmIR
$("#alert-div-inputpost-product-to-send-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>انتخاب محصولات ارسال شده الزامی است.</p>' +
    '</div></div>');

$("#alert-div-inputpost-product-to-send-limit").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>بیش از 999 محصول نمیتواند برای ارسال انتخاب شود!</p>' +
    '</div></div>');


$("#alert-div-inputpost-barcode-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>بارکد پستی مرسوله حتما باید وارد شود.</p>' +
    '</div></div>');

$("#alert-div-inputpost-barcode-24char").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
	'<i class="far fa-exclamation-circle"></i>' +
	'<p>بارکد پستی مرسوله حتما باید 24 رقم باشد.</p>' +
    '</div></div>');
    
$("#alert-div-inputpost-sendprice-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>هزینه ارسال مرسوله نمیتواند خالی باشد.</p>' +
    '</div></div>');

$("#alert-div-inputpost-sendprice-minlength").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>هزینه ارسال مرسوله باید از 5رقم بیشتر باشد.</p>' +
    '</div></div>');

$("#alert-div-inputpost-senddate-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>تاریخ ارسال مرسوله نمیتواند خالی باشد.</p>' +
    '</div></div>');



$(function () {
    $('[data-toggle="tooltip"]').tooltip();
  })

$(window).on( "load", function() {
    var e = document.getElementById('inputprod_sellprice');
    e.onfocusout  = myHandler;
    e.onpropertychange = e.onfocusout ; // for IE8
    function myHandler() {
        var intprice = parseInt(e.value / 10);
        if (intprice != 0) {
            document.getElementById('sellprice-toman').innerHTML = intprice.toPersianLetter() + ' تومان';
        }
        else {
            document.getElementById('sellprice-toman').innerHTML = '';
        }
    }
})

$('#inputPost_UserSend').on('focusout', function() {
    if($(this).val().length === 0) {
        $("#alert-div-inputPost_UserSend-empty").show();
        $(this).addClass("inputshopempty");
    }
    else {
        $("#alert-div-inputPost_UserSend-empty").hide();
        $("#alert-div-inputPost_UserSend-just_persian").hide();
        $(this).removeClass("inputshopempty");
    }
})

$('#inputPost_UserSend').on('input', function() {
    if($(this).val().length !== 0) {
        $("#alert-div-inputPost_UserSend-empty").hide();
        $(this).removeClass("inputshopempty");
        var data = $("#inputPost_UserSend").val();
        var ew = data.charCodeAt(data.length-1);
        if (ew === 32) {
            $("#alert-div-inputPost_UserSend-just_persian").hide();
            $(this).removeClass("inputshopempty");
        }
        else if (1578 <= ew && ew <= 1594 || 1604 <= ew && ew <= 1608) {
            $("#alert-div-inputPost_UserSend-just_persian").hide();
            $(this).removeClass("inputshopempty");
        }
        else if (ew === 1570 || ew === 1575 || ew === 1576 || ew === 1662 || ew === 1670 || ew === 1688 || ew === 1601 || ew === 1602 || ew === 1705 || ew === 1711 || ew === 1740 || ew === 1574) {
            $("#alert-div-inputPost_UserSend-just_persian").hide();
            $(this).removeClass("inputshopempty");
        }
        else {
            $("#inputPost_UserSend").val($("#inputPost_UserSend").val().substr(0, data.length-1));
            $("#alert-div-inputPost_UserSend-just_persian").show();
            $(this).addClass("inputshopempty");
        }
    }
})
$("#inputPost_Barcode").on("focusout", function () {
    var thisLength = $(this).val().length;
    if (thisLength == 0)
    {
        $("#alert-div-inputpost-barcode-empty").show();
        $("#alert-div-inputpost-barcode-digits").hide();
        $("#alert-div-inputpost-barcode-24char").hide();
        $(this).addClass('inputshopempty');
    }
    else if (thisLength !== 24)
    {
        $("#alert-div-inputpost-barcode-empty").hide();
        $("#alert-div-inputpost-barcode-24char").show();
        $("#alert-div-inputpost-barcode-digits").hide();
        $(this).addClass('inputshopempty');
    }
    else {
        $("#alert-div-inputpost-barcode-empty").hide();
        $("#alert-div-inputpost-barcode-24char").hide();
        $("#alert-div-inputpost-barcode-digits").hide();
        $(this).removeClass('inputshopempty');
    }
})
$("#inputPost_Barcode").on("input", function () {
    if ($(this).val().length !== 0)
    {
        $("#alert-div-inputpost-barcode-empty").hide();
        $(this).removeClass('inputshopempty');
    }
    if ($(this).val().length == 24)
    {
        $("#alert-div-inputpost-barcode-24char").hide();
    }
    var textLength = $(this).val().length;
    if (textLength >= 24) {
        $(this).val($(this).val().substr(0, 24));
        $(this).prop("maxlength", 24);
    }
})
$("#inputprod_sellprice").on("focusout", function () {
    var thisLength = $(this).val().length;
    if (thisLength == 0)
    {
        $("#alert-div-inputpost-sendprice-minlength").hide();
        $("#alert-div-inputpost-sendprice-empty").show();
        $(this).addClass('inputshopempty');
    }
    else if (thisLength < 5)
    {
        $("#alert-div-inputpost-sendprice-empty").hide();
        $("#alert-div-inputpost-sendprice-minlength").show();
        $(this).addClass('inputshopempty');
    }
    else {
        $("#alert-div-inputpost-sendprice-empty").hide();
        $("#alert-div-inputpost-sendprice-minlength").hide();
        $(this).removeClass('inputshopempty');
    }
})
$("#inputprod_sellprice").on("input", function () {
    var textLength = $(this).val().length;
    if (textLength >= 15) {
        $(this).val($(this).val().substr(0, 15));
        $(this).prop("maxlength", 15);
    }
})

checkFields = function () {
    var checks = true;
    $("#alert-div-inputpost-product-to-send-empty").hide();
    $("#alert-div-inputpost-product-to-send-limit").hide();
    $(".product-to-send-list .chosen-choices").removeClass("inputshopempty_Cat");
    $("#alert-div-inputpost-senddate-empty").hide();
    $("#inputPost_SendDate").removeClass('inputshopempty');

    if($(".product-to-send :selected").length === 0)
    {
        $("#alert-div-inputpost-product-to-send-empty").show();
        $(".product-to-send-list .chosen-choices").addClass("inputshopempty_Cat");
        checks = false;
    }
    else if ($(".product-to-send :selected").length > 999)
    {
        $("#alert-div-inputpost-product-to-send-limit").show();
        $(".product-to-send-list .chosen-choices").addClass("inputshopempty_Cat");
        checks = false;
    }
    
    if($("#inputPost_UserSend").val().length === 0) {
        $("#alert-div-inputPost_UserSend-empty").show();
        $("#inputPost_UserSend").addClass("inputshopempty");
        checks = false;
    }
    if($("#inputPost_Barcode").val().length == 0)
    {
        $("#alert-div-inputpost-barcode-empty").show();
        $("#inputPost_Barcode").addClass("inputshopempty");
        checks = false;
    }
    else if($("#inputPost_Barcode").val().length !== 24)
    {
        $("#alert-div-inputpost-barcode-24char").show();
        $("#inputPost_Barcode").addClass("inputshopempty");
        checks = false;
    }
    
    if($("#inputprod_sellprice").val().length == 0)
    {
        $("#alert-div-inputpost-sendprice-empty").show();
        $("#inputprod_sellprice").addClass('inputshopempty');
        checks = false;
    }
    else if ($("#inputprod_sellprice").val().length < 5)
    {
        $("#alert-div-inputpost-sendprice-minlength").show();
        $("#inputprod_sellprice").addClass('inputshopempty');
        checks = false;
    }
    
    if($("#inputPost_SendDate").val().length == 0)
    {
        $("#alert-div-inputpost-senddate-empty").show();
        $("#inputPost_SendDate").addClass('inputshopempty');
        checks = false;
    }
    return checks;
}

$("#send-left").on('click', function () {
    var check = checkFields();
    return check;
})