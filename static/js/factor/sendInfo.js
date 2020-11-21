//#region Hide Alerts

        //#region   Empty Alerts
        $("#alert-div-inputFirstName-empty").hide();
        $("#alert-div-inputLastName-empty").hide();
        $("#alert-div-inputState-empty").hide();
        $("#alert-div-inputBigCity-empty").hide();
        $("#alert-div-inputCity-empty").hide();
        $("#alert-div-inputMobileNumber-empty").hide();
        $("#alert-div-inputPhoneNumber-empty").hide();
        $("#alert-div-inputCityPerCode-empty").hide();
        $("#alert-div-inputAddress-empty").hide();
        $("#alert-div-inputZipCode-empty").hide();
    //#endregion

    //#region   Char Alerts
        $("#alert-div-inputFirstName-Persian").hide();
        $("#alert-div-inputLastName-Persian").hide();
        $("#alert-div-inputState-Persian").hide();
        $("#alert-div-inputBigCity-Persian").hide();
        $("#alert-div-inputCity-Persian").hide();
        $("#alert-div-inputMobileNumber-digits").hide();
        $("#alert-div-inputPhoneNumber-digits").hide();
        $("#alert-div-inputCityPerCode-digits").hide();
        // $("#alert-div-inputAddress-Persian").hide();
        $("#alert-div-inputZipCode-digits").hide();
    //#endregion
    
    //#region   MinLength Alert
    $("#alert-div-inputAddress-minlength").hide();
    //#endregion
    
    //#region   Length Alerts
    $("#alert-div-inputMobileNumber-Length").hide();
    $("#alert-div-inputPhoneNumber-Length").hide();
    $("#alert-div-inputCityPerCode-minlength").hide();
    $("#alert-div-inputZipCode-Length").hide();
        //#endregion
        
        //#region   Valid Alert
        $("#alert-div-inputMobileNumber-valid").hide();
        //#endregion
        
        //#endregion
        
        //#region Initialize Alerts
        
        //#region   Empty Alerts
        $("#alert-div-inputFirstName-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
        '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
        '<i class="far fa-exclamation-circle"></i>' +
        '<p>وارد کردن نام الزامی است</p>' +
        '</div></div>');
        
        $("#alert-div-inputLastName-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
        '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
        '<i class="far fa-exclamation-circle"></i>' +
        '<p>وارد کردن نام خانوادگی الزامی است</p>' +
        '</div></div>');
        
        $("#alert-div-inputState-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
            '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
            '<i class="far fa-exclamation-circle"></i>' +
            '<p>انتخاب استان الزامی است</p>' +
            '</div></div>');
            
            $("#alert-div-inputBigCity-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
            '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
            '<i class="far fa-exclamation-circle"></i>' +
            '<p>انتخاب شهرستان الزامی است</p>' +
            '</div></div>');
            
            $("#alert-div-inputCity-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
            '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
            '<i class="far fa-exclamation-circle"></i>' +
            '<p>انتخاب شهر الزامی است</p>' +
            '</div></div>');
            
            $("#alert-div-inputMobileNumber-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
            '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
            '<i class="far fa-exclamation-circle"></i>' +
            '<p>وارد کردن شماره همراه الزامی است</p>' +
            '</div></div>');
            
            $("#alert-div-inputPhoneNumber-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
            '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
            '<i class="far fa-exclamation-circle"></i>' +
            '<p>وارد کردن شماره تلفن ثابت الزامی است</p>' +
            '</div></div>');
            
            $("#alert-div-inputCityPerCode-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
            '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
            '<i class="far fa-exclamation-circle"></i>' +
            '<p>وارد کردن پیش شماره شهر الزامی است</p>' +
            '</div></div>');
            
            $("#alert-div-inputAddress-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
            '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
            '<i class="far fa-exclamation-circle"></i>' +
            '<p>وارد کردن آدرس الزامی است</p>' +
            '</div></div>');
            
            $("#alert-div-inputZipCode-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
            '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
            '<i class="far fa-exclamation-circle"></i>' +
            '<p>وارد کردن کدپستی الزامی است</p>' +
            '</div></div>');
            //#endregion
            
            //#region   Char Alerts
            $("#alert-div-inputFirstName-Persian").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
            '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
            '<i class="far fa-exclamation-circle"></i>' +
            '<p>نام فقط میتواند شامل حروف فارسی باشد</p>' +
            '</div></div>');
            
            $("#alert-div-inputLastName-Persian").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
            '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
            '<i class="far fa-exclamation-circle"></i>' +
            '<p>نام خانوادگی فقط میتواند شامل حروف فارسی باشد</p>' +
            '</div></div>');
            
            $("#alert-div-inputState-Persian").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
            '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
            '<i class="far fa-exclamation-circle"></i>' +
            '<p>استان فقط میتواند شامل حروف فارسی باشد</p>' +
            '</div></div>');
            
            $("#alert-div-inputBigCity-Persian").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
            '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
            '<i class="far fa-exclamation-circle"></i>' +
            '<p>شهرستان فقط میتواند شامل حروف فارسی باشد</p>' +
            '</div></div>');
            
        $("#alert-div-inputCity-Persian").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
        '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
        '<i class="far fa-exclamation-circle"></i>' +
        '<p>شهر فقط میتواند شامل حروف فارسی باشد</p>' +
        '</div></div>');
        
        $("#alert-div-inputMobileNumber-digits").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
        '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
        '<i class="far fa-exclamation-circle"></i>' +
        '<p>برای وارد نمودن شماره همراه تنها از اعداد میتوانید استفاده نمائید</p>' +
        '</div></div>');
        
        $("#alert-div-inputPhoneNumber-digits").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
        '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
        '<i class="far fa-exclamation-circle"></i>' +
        '<p>برای وارد نمودن شماره ثابت تنها از اعداد میتوانید استفاده نمائید</p>' +
        '</div></div>');
        
        $("#alert-div-inputCityPerCode-digits").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
        '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
        '<i class="far fa-exclamation-circle"></i>' +
        '<p>برای وارد نمودن پیش شماره شهر تنها از اعداد میتوانید استفاده نمائید</p>' +
        '</div></div>');
        
        // $("#alert-div-inputAddress-Persian").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
        //     '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
        //     '<i class="far fa-exclamation-circle"></i>' +
        //     '<p>تنها مجاز به استفاده از حروف فارسی و اعداد در آدرس هستید</p>' +
        //     '</div></div>');
        
        $("#alert-div-inputZipCode-digits").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
        '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
        '<i class="far fa-exclamation-circle"></i>' +
        '<p>برای وارد نمودن کد پستی تنها از اعداد میتوانید استفاده نمائید</p>' +
        '</div></div>');
        //#endregion
        
        //#region   MinLength Alerts
        // $("#alert-div-inputAddress-minlength").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
        // '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
        // '<i class="far fa-exclamation-circle"></i>' +
        // '<p>آدرس حداقل بایستی 10 کاراکتر باشد</p>' +
        // '</div></div>');
        //#endregion
        
        //#region   Length Alerts
        $("#alert-div-inputCityPerCode-minlength").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
        '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
        '<i class="far fa-exclamation-circle"></i>' +
        '<p>پیش شماره شهر بایستی 3 رقم باشد</p>' +
        '</div></div>');

        $("#alert-div-inputMobileNumber-Length").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
        '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
        '<i class="far fa-exclamation-circle"></i>' +
        '<p>شماره همراه بایستی 11 رقم باشد</p>' +
        '</div></div>');
        $("#alert-div-inputPhoneNumber-Length").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
        '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
            '<i class="far fa-exclamation-circle"></i>' +
            '<p>شماره ثابت بایستی 8 رقم باشد</p>' +
            '</div></div>');
            $("#alert-div-inputZipCode-Length").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
            '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
            '<i class="far fa-exclamation-circle"></i>' +
            '<p>کد پستی بایستی 10 رقم باشد</p>' +
            '</div></div>');
            //#endregion
            
            //#region   Valid Alert
            $("#alert-div-inputMobileNumber-valid").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
            '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
            '<i class="far fa-exclamation-circle"></i>' +
            '<p>این شماره همراه معتبر نمیباشد</p>' +
            '</div></div>');
            //#endregion
            
            //#endregion
            
            var ranges = [
                '\ud83c[\udf00-\udfff]', // U+1F300 to U+1F3FF
                '\ud83d[\udc00-\ude4f]', // U+1F400 to U+1F64F
                '\ud83d[\ude80-\udeff]'  // U+1F680 to U+1F6FF
];
function removeInvalidChars(specificinput) {
    var str = specificinput.val();
    str = str.replace(new RegExp(ranges.join('|'), 'g'), '');
    specificinput.val(str);
}

//#region Handle Alerts By Events
//Variables
var ValidMobileNumber = false;
var ValidPhoneNumber = false;
var ValidZipCode = false;
//#region FocusOut
    $("#inputFirstName").on("focusout", function () {
        if ($(this).val() === '') {
            $(this).addClass("inputshopempty");
            $("#alert-div-inputFirstName-empty").show();
        }
        else {
            $(this).removeClass("inputshopempty");
            $("#alert-div-inputFirstName-empty").hide();
            $("#alert-div-inputFirstName-Persian").hide();
        }
    })
    $("#inputLastName").on("focusout", function () {
        if ($(this).val() === '') {
            $(this).addClass("inputshopempty");
            $("#alert-div-inputLastName-empty").show();
        }
        else {
            $(this).removeClass("inputshopempty");
            $("#alert-div-inputLastName-empty").hide();
            $("#alert-div-inputLastName-Persian").hide();
        }
    })
    $("#inputState").on("focusout", function () {
        if ($(this).val() === '') {
            $(this).addClass("inputshopempty");
            $("#alert-div-inputState-empty").show();
        }
        else {
            $(this).removeClass("inputshopempty");
            $("#alert-div-inputState-empty").hide();
            $("#alert-div-inputState-Persian").hide();
        }
    })
    $("#inputBigCity").on("focusout", function () {
        if ($(this).val() === '') {
            $(this).addClass("inputshopempty");
            $("#alert-div-inputBigCity-empty").show();
        }
        else {
            $(this).removeClass("inputshopempty");
            $("#alert-div-inputBigCity-empty").hide();
            $("#alert-div-inputBigCity-Persian").hide();
        }
    })
    $("#inputCity").on("focusout", function () {
        if ($(this).val() === '') {
            $(this).addClass("inputshopempty");
            $("#alert-div-inputCity-empty").show();
        }
        else {
            $(this).removeClass("inputshopempty");
            $("#alert-div-inputCity-empty").hide();
            $("#alert-div-inputCity-Persian").hide();
        }
    })
    $("#inputMobileNumber").on("focusout", function () {
        var mobileLength = $(this).val().length;
        if ($(this).val() === '') {
            $(this).addClass("inputshopempty");
            $("#alert-div-inputMobileNumber-empty").show();
            $("#alert-div-inputMobileNumber-valid").hide();
            $("#alert-div-inputMobileNumber-Length").hide();
        }
        else if (mobileLength < 11) {
            $(this).addClass("inputshopempty");
            $("#alert-div-inputMobileNumber-empty").hide();
            $("#alert-div-inputMobileNumber-Length").show();
            $("#alert-div-inputMobileNumber-valid").hide();
        }
        else if ($(this).val()[0] !== '0' || $(this).val()[1] !== '9') {
            $(this).addClass("inputshopempty");
            $("#alert-div-inputMobileNumber-empty").hide();
            $("#alert-div-inputMobileNumber-Length").hide();
            $("#alert-div-inputMobileNumber-valid").show();
            ValidMobileNumber = false;
        }
        else {
            $(this).removeClass("inputshopempty");
            $("#alert-div-inputMobileNumber-empty").hide();
            $("#alert-div-inputMobileNumber-Length").hide();
            $("#alert-div-inputMobileNumber-valid").hide();
            $("#alert-div-inputMobileNumber-digits").hide();
            ValidMobileNumber = true;
        }
    })
    $("#inputPhoneNumber").on("focusout", function () {
        var PhoneLength = $(this).val().length;
        if ($(this).val() === '') {
            $(this).addClass("inputshopempty");
            $("#alert-div-inputPhoneNumber-empty").show();
            $("#alert-div-inputPhoneNumber-Length").hide();
        }
        else if (PhoneLength < 8) {
            $(this).addClass("inputshopempty");
            $("#alert-div-inputPhoneNumber-empty").hide();
            $("#alert-div-inputPhoneNumber-Length").show();
        }
        else {
            $(this).removeClass("inputshopempty");
            $("#alert-div-inputPhoneNumber-empty").hide();
            $("#alert-div-inputPhoneNumber-Length").hide();
            $("#alert-div-inputPhoneNumber-digits").hide();
        }
    })
    $("#inputCityPerCode").on("focusout", function () {
        var inputCodeLength = $(this).val().length;
        if ($(this).val() === '') {
            $(this).addClass("inputshopempty");
            $("#alert-div-inputCityPerCode-empty").show();
            $("#alert-div-inputCityPerCode-minlength").hide();
        }
        else if (inputCodeLength !== 3) {
            $(this).addClass("inputshopempty");
            $("#alert-div-inputCityPerCode-minlength").show();
            $("#alert-div-inputCityPerCode-empty").hide();
            $(this).prop("minLength", 3);
        }
        else {
            $(this).removeClass("inputshopempty");
            $("#alert-div-inputCityPerCode-minlength").hide();
            $("#alert-div-inputCityPerCode-empty").hide();
        }
    })
    $("#inputAddress").on("focusout", function () {
        if ($(this).val() === '') {
            $(this).addClass("inputshopempty");
            $("#alert-div-inputAddress-empty").show();
        }
        else {
            $(this).removeClass("inputshopempty");
            $("#alert-div-inputAddress-empty").hide();
            $("#alert-div-inputAddress-Persian").hide();
        }
    })
    $("#inputZipCode").on("focusout", function () {
        var ZipCodeLength = $(this).val().length;
        if ($(this).val() === '') {
            $(this).addClass("inputshopempty");
            $("#alert-div-inputZipCode-empty").show();
            $("#alert-div-inputZipCode-Length").hide();
        }
        else if (ZipCodeLength < 10) {
            $(this).addClass("inputshopempty");
            $("#alert-div-inputZipCode-empty").hide();
            $("#alert-div-inputZipCode-Length").show();
        }
        else {
            $(this).removeClass("inputshopempty");
            $("#alert-div-inputZipCode-empty").hide();
            $("#alert-div-inputZipCode-Length").hide();
            $("#alert-div-inputZipCode-digits").hide();
        }
    })
            //#endregion
            
            //#region Input
            $("#inputFirstName").on("input", function () {
                if ($(this).val() !== '') {
                    $(this).removeClass("inputshopempty");
                    $("#alert-div-inputFirstName-empty").hide();
                }
                removeInvalidChars($(this));
            })
            
            $("#inputLastName").on("input", function () {
                if ($(this).val() !== '') {
                    $(this).removeClass("inputshopempty");
                    $("#alert-div-inputLastName-empty").hide();
                }
                removeInvalidChars($(this));
            })
            MobileNumberCheck = function () {
            if ($("#inputMobileNumber").val() !== '') {
				$("#inputMobileNumber").removeClass("inputshopempty");
				$("#alert-div-inputMobileNumber-empty").hide();
            }
            var mobileLength = $("#inputMobileNumber").val().length;
            ValidMobileNumber = false;
            if (mobileLength === 11) {
                $("#alert-div-inputMobileNumber-Length").hide();
                if ($("#inputMobileNumber").val()[0] === '0' && $("#inputMobileNumber").val()[1] === '9') {
                    $("#alert-div-inputMobileNumber-valid").hide();
                    ValidMobileNumber = true;
                }
                else if ($("#inputMobileNumber").val()[0] !== '0' || $("#inputMobileNumber").val()[1] !== '9') {
                    $("#alert-div-inputMobileNumber-valid").show();
                    ValidMobileNumber = false;
                }
            }
        }

        $("#inputMobileNumber").on("input", function () {
			MobileNumberCheck();
        })

        PhoneNumberCheck = function () {
            if ($("#inputPhoneNumber").val() !== '') {
				$("#inputPhoneNumber").removeClass("inputshopempty");
                $("#alert-div-inputPhoneNumber-empty").hide();
            }
            if ($("#inputPhoneNumber").val().length == 8)
            {
                $("#alert-div-inputPhoneNumber-Length").hide();
                ValidPhoneNumber = true;
            }
            else {
                ValidPhoneNumber = false;
            }
        }

        $("#inputPhoneNumber").on("input", function () {
			PhoneNumberCheck();
        })

        $("#inputCityPerCode").on("input", function () {
			if ($(this).val() !== '') {
				$(this).removeClass("inputshopempty");
				$("#alert-div-inputCityPerCode-empty").hide();
            }
            if ($(this).val().length >= 3)
            {
                $("#alert-div-inputCityPerCode-minlength").hide();
            }
        })
        $("#inputAddress").on("input", function () {
			if ($(this).val() !== '') {
				$(this).removeClass("inputshopempty");
				$("#alert-div-inputAddress-empty").hide();
            }
            removeInvalidChars($(this));
        })
        ZipCodeCheck = function () {
            if ($("#inputZipCode").val() !== '') {
				$("#inputZipCode").removeClass("inputshopempty");
				$("#alert-div-inputZipCode-empty").hide();
            }
            if ($("#inputZipCode").val().length === 10)
            {
                $("#alert-div-inputZipCode-Length").hide();
                ValidZipCode = true;
            }
            else {
                ValidZipCode = false;
            }
        }

        $("#inputZipCode").on("input", function () {
			ZipCodeCheck();
        })
        //#endregion

        //#region KeyPress
        $("#inputFirstName").on("keypress", function (event) {
            var ew = event.which;
			if (ew === 32) {
				$("#alert-div-inputFirstName-Persian").hide();
				return true;
			}
			else if (1578 <= ew && ew <= 1594 || 1604 <= ew && ew <= 1608 || 1611 <= ew && ew <= 1616) {
				$("#alert-div-inputFirstName-Persian").hide();
				return true;
			}
			else if (ew === 1570 || ew === 1575 || ew === 1576 || ew === 1662 || ew === 1670 || ew === 1688 || ew === 1601 || ew === 1602 || ew === 1705 || ew === 1711 || ew === 1740 || ew === 1574) {
				$("#alert-div-inputFirstName-Persian").hide();
				return true;
            }
            else if (ew === 13) {
        
            }
			else {
				$("#alert-div-inputFirstName-Persian").show();
				$(this).addClass("inputshopempty");
				return false;
			}
        })
        $("#inputLastName").on("keypress", function (event) {
            var ew = event.which;
			if (ew === 32) {
				$("#alert-div-inputLastName-Persian").hide();
				return true;
			}
			else if (1578 <= ew && ew <= 1594 || 1604 <= ew && ew <= 1608 || 1611 <= ew && ew <= 1616) {
				$("#alert-div-inputLastName-Persian").hide();
				return true;
			}
			else if (ew === 1570 || ew === 1575 || ew === 1576 || ew === 1662 || ew === 1670 || ew === 1688 || ew === 1601 || ew === 1602 || ew === 1705 || ew === 1711 || ew === 1740 || ew === 1574) {
				$("#alert-div-inputLastName-Persian").hide();
				return true;
            }
            else if (ew === 13) {
        
            }
			else {
				$("#alert-div-inputLastName-Persian").show();
				$(this).addClass("inputshopempty");
				return false;
			}
        })
        
        $("#inputMobileNumber").on("keypress", function (event) {
            var ew = event.which;
            if (48 <= ew && ew <= 57) {
                $("#alert-div-inputMobileNumber-digits").hide();
                return true;
            }
            else if (ew === 13) {
        
            }
            else {
                $("#alert-div-inputMobileNumber-digits").show();
                $(this).addClass("inputshopempty");
                return false;
            }
        })
        $("#inputPhoneNumber").on("keypress", function (event) {
            var ew = event.which;
            if (48 <= ew && ew <= 57) {
                $("#alert-div-inputPhoneNumber-digits").hide();
                return true;
            }
            else if (ew === 13) {
        
            }
            else {
                $("#alert-div-inputPhoneNumber-digits").show();
                $(this).addClass("inputshopempty");
                return false;
            }
        })
        $("#inputCityPerCode").on("keypress", function (event) {
            var ew = event.which;
            if (48 <= ew && ew <= 57) {
                $("#alert-div-inputCityPerCode-digits").hide();
                return true;
            }
            else if (ew === 13) {
        
            }
            else {
                $("#alert-div-inputCityPerCode-digits").show();
                $(this).addClass("inputshopempty");
                return false;
            }
        })
        // $("#inputAddress").on("keypress", function (event) {
		// 	var ew = event.which;
		// 	if (ew === 32) {
		// 		$("#alert-div-inputAddress-Persian").hide();
		// 		return true;
        //     }
        //     else if (48 <= ew && ew <= 57) {
        //         $("#alert-div-inputAddress-Persian").hide();
		// 		return true;
        //     }
		// 	else if (1578 <= ew && ew <= 1594 || 1604 <= ew && ew <= 1608) {
		// 		$("#alert-div-inputAddress-Persian").hide();
		// 		return true;
		// 	}
		// 	else if (ew === 1570 || ew === 1575 || ew === 1576 || ew === 1662 || ew === 1670 || ew === 1688 || ew === 1601 || ew === 1602 || ew === 1705 || ew === 1711 || ew === 1740 || ew === 1574 || ew === 40 || ew === 41 || ew === 45 || ew === 95) {
		// 		$("#alert-div-inputAddress-Persian").hide();
		// 		return true;
        // 	}
        //  else if (ew === 13) {
        //
        //  }
		// 	else {
		// 		$("#alert-div-inputAddress-Persian").show();
		// 		$(this).addClass("inputshopempty");
		// 		return false;
		// 	}
		// })
        $("#inputZipCode").on("keypress", function (event) {
            var ew = event.which;
            if (48 <= ew && ew <= 57) {
                $("#alert-div-inputZipCode-digits").hide();
                return true;
            }
            else if (ew === 13) {
        
            }
            else {
                $("#alert-div-inputZipCode-digits").show();
                $(this).addClass("inputshopempty");
                return false;
            }
        })
        //#endregion

        //#region Paste
        $("#inputFirstName").on("paste", function () {
			setTimeout(function(){
				var data = $("#inputFirstName").val();
				for(var i=0; i<data.length; i++)
				{
					var ewt = data.charCodeAt(i);
					if (ewt === 32) {
						
					}
					else if (1578 <= ewt && ewt <= 1594 || 1604 <= ewt && ewt <= 1608 || 1611 <= ewt && ewt <= 1616) {
						
					}
					else if (ewt === 1570 || ewt === 1575 || ewt === 1576 || ewt === 1662 || ewt === 1670 || ewt === 1688 || ewt === 1601 || ewt === 1602 || ewt === 1705 || ewt === 1711 || ewt === 1740 || ewt === 1574) {
						
					}
					else {
						$("#inputFirstName").val('');
						$("#alert-div-inputFirstName-Persian").show();
						$("#inputFirstName").addClass("inputshopempty");
						return false;
					}
				}
		}, 10)
			setTimeout(function () {
				if($("#inputFirstName").val() !== '')
				{
					$("#alert-div-inputFirstName-empty").hide();
					$("#alert-div-inputFirstName-Persian").hide();
					$("#inputFirstName").removeClass("inputshopempty");
				}
			}, 20)
        })
        $("#inputLastName").on("paste", function () {
			setTimeout(function(){
				var data = $("#inputLastName").val();
				for(var i=0; i<data.length; i++)
				{
					var ewt = data.charCodeAt(i);
					if (ewt === 32) {
						
					}
					else if (1578 <= ewt && ewt <= 1594 || 1604 <= ewt && ewt <= 1608 || 1611 <= ewt && ewt <= 1616) {
						
					}
					else if (ewt === 1570 || ewt === 1575 || ewt === 1576 || ewt === 1662 || ewt === 1670 || ewt === 1688 || ewt === 1601 || ewt === 1602 || ewt === 1705 || ewt === 1711 || ewt === 1740 || ewt === 1574) {
						
					}
					else {
						$("#inputLastName").val('');
						$("#alert-div-inputLastName-Persian").show();
						$("#inputLastName").addClass("inputshopempty");
						return false;
					}
				}
		}, 10)
			setTimeout(function () {
				if($("#inputLastName").val() !== '')
				{
					$("#alert-div-inputLastName-empty").hide();
					$("#alert-div-inputLastName-Persian").hide();
					$("#inputLastName").removeClass("inputshopempty");
				}
			}, 20)
        })
        var stateprofValid = false;
		var bigcityprofValid = false;
		var cityprofValid = false;
		checkDestination = function(e) {
			if(e.val() !== '0')
			{
				return true;
			}
			else {
				return false;
			}
		}
		$(document).ready(function() {
			stateprofValid = checkDestination($("#inputprofState"));
			bigcityprofValid = checkDestination($("#inputprofBigCity"));
			cityprofValid = checkDestination($("#inputprofCity"));

			$("#inputprofState").chosen().change(function() {
				stateprofValid = checkDestination($(this));
				if (stateprofValid == false)
				{
					bigcityprofValid = false;
					cityprofValid = false;
                }
                else {
                    $("#alert-div-inputState-empty").hide();
                    $("#inputprofState_chosen .chosen-single").removeClass("inputshopempty_Cat");
                }
			})
			$("#inputprofBigCity").chosen().change(function() {
                bigcityprofValid = checkDestination($(this));
				if (bigcityprofValid == false)
				{
                    cityprofValid = false;
                }
                else {
                    $("#alert-div-inputBigCity-empty").hide();
                    $("#inputprofBigCity_chosen .chosen-single").removeClass("inputshopempty_Cat");
                }
			})
			$("#inputprofCity").chosen().change(function() {
                cityprofValid = checkDestination($(this));
                if (cityprofValid)
                {
                    $("#alert-div-inputCity-empty").hide();
                    $("#inputprofCity_chosen .chosen-single").removeClass("inputshopempty_Cat");
                }
            })
		})
        $("#inputMobileNumber").on("paste", function () {
            var evm;
            setTimeout(function () {
                var textLength = $("#inputMobileNumber").val().length;
                if (textLength >= 11) {
                    $("#inputMobileNumber").val($("#inputMobileNumber").val().substr(0, 11));
                    $("#inputMobileNumber").prop("maxlength", 11);
                }
                var datamobile = $("#inputMobileNumber").val();
                for (var i = 0; i < datamobile.length; i++) {
                    evm = datamobile.charCodeAt(i);
                    if (48 <= evm && evm <= 57) {
                    }
                    else {
                        $("#inputMobileNumber").val('');
                        $("#inputMobileNumber").addClass('inputshopempty');            
                        $("#alert-div-inputMobileNumber-digits").show();
                        return false;
                    }
                }
            }, 10)
            setTimeout(function () {
                if ($("#inputMobileNumber").val() !== '') {
                    $("#alert-div-inputMobileNumber-digits").hide();
                    $("#inputMobileNumber").removeClass('inputshopempty');
                }
            }, 20)
        })
        $("#inputPhoneNumber").on("paste", function () {
            var evm;
            setTimeout(function () {
                var textLength = $("#inputPhoneNumber").val().length;
                if (textLength >= 8) {
                    $("#inputPhoneNumber").val($("#inputPhoneNumber").val().substr(0, 8));
                    $("#inputPhoneNumber").prop("maxlength", 8);
                }
                var datamobile = $("#inputPhoneNumber").val();
                for (var i = 0; i < datamobile.length; i++) {
                    evm = datamobile.charCodeAt(i);
                    if (48 <= evm && evm <= 57) {
                    }
                    else {
                        $("#inputPhoneNumber").val('');
                        $("#inputPhoneNumber").addClass('inputshopempty');            
                        $("#alert-div-inputPhoneNumber-digits").show();
                        return false;
                    }
                }
            }, 10)
            setTimeout(function () {
                if ($("#inputPhoneNumber").val() !== '') {
                    $("#alert-div-inputPhoneNumber-digits").hide();
                    $("#inputPhoneNumber").removeClass('inputshopempty');
                    PhoneNumberCheck();
                }
            }, 20)
        })
        $("#inputCityPerCode").on("paste", function () {
            var evm;
            setTimeout(function () {
                var textLength = $("#inputCityPerCode").val().length;
                if (textLength >= 6) {
                    $("#inputCityPerCode").val($("#inputCityPerCode").val().substr(0, 6));
                    $("#inputCityPerCode").prop("maxlength", 6);
                }
                var datamobile = $("#inputCityPerCode").val();
                for (var i = 0; i < datamobile.length; i++) {
                    evm = datamobile.charCodeAt(i);
                    if (48 <= evm && evm <= 57) {
                    }
                    else {
                        $("#inputCityPerCode").val('');
                        $("#inputCityPerCode").addClass('inputshopempty');            
                        $("#alert-div-inputCityPerCode-digits").show();
                        return false;
                    }
                }
            }, 10)
            setTimeout(function () {
                if ($("#inputCityPerCode").val() !== '') {
                    $("#alert-div-inputCityPerCode-digits").hide();
                    $("#inputCityPerCode").removeClass('inputshopempty');
                }
            }, 20)
        })
        // $("#inputAddress").on("paste", function () {
		// 	setTimeout(function(){
		// 		var data = $("#inputAddress").val();
		// 		for(var i=0; i<data.length; i++)
		// 		{
		// 			var ewt = data.charCodeAt(i);
		// 			if (ewt === 32) {
						
		// 			}
		// 			else if (48 <= ewt && ewt <= 57) {
						
		// 			}
		// 			else if (1578 <= ewt && ewt <= 1594 || 1604 <= ewt && ewt <= 1608) {
						
		// 			}
		// 			else if (ewt === 1570 || ewt === 1575 || ewt === 1576 || ewt === 1662 || ewt === 1670 || ewt === 1688 || ewt === 1601 || ewt === 1602 || ewt === 1705 || ewt === 1711 || ewt === 1740 || ewt === 1574) {
						
		// 			}
		// 			else {
		// 				$("#inputAddress").val('');
		// 				$("#alert-div-inputAddress-Persian").show();
		// 				$(this).addClass("inputshopempty");
		// 				return false;
		// 			}
		// 		}
		// }, 10)
		// 	setTimeout(function () {
		// 		if($("#inputAddress").val() !== '')
		// 		{
		// 			$("#alert-div-inputAddress-empty").hide();
		// 			$("#alert-div-inputAddress-Persian").hide();
		// 			$("#inputAddress").removeClass("inputshopempty");
		// 		}
		// 	}, 20)
        // })
        $("#inputZipCode").on("paste", function () {
            var evm;
            setTimeout(function () {
                var textLength = $("#inputZipCode").val().length;
                if (textLength >= 10) {
                    $("#inputZipCode").val($("#inputZipCode").val().substr(0, 10));
                    $("#inputZipCode").prop("maxlength", 10);
                }
                var datamobile = $("#inputZipCode").val();
                for (var i = 0; i < datamobile.length; i++) {
                    evm = datamobile.charCodeAt(i);
                    if (48 <= evm && evm <= 57) {
                    }
                    else {
                        $("#inputZipCode").val('');
                        $("#inputZipCode").addClass('inputshopempty');            
                        $("#alert-div-inputZipCode-digits").show();
                        return false;
                    }
                }
            }, 10)
            setTimeout(function () {
                if ($("#inputZipCode").val() !== '') {
                    $("#alert-div-inputZipCode-digits").hide();
                    $("#inputZipCode").removeClass('inputshopempty');
                    ZipCodeCheck();
                }
            }, 20)
        })
        //#endregion

        //#region KeyPress & Paste
            $("#inputMobileNumber").on("keypress", function () {
                var textLength = $(this).val().length;
                if (textLength >= 11) {
                    $(this).val($(this).val().substr(0, 11));
                    $(this).prop("maxlength", 11);
                    return false;
                }
            })
            $("#inputPhoneNumber").on("keypress", function () {
                var textLength = $(this).val().length;
                if (textLength >= 8) {
                    $(this).val($(this).val().substr(0, 8));
                    $(this).prop("maxlength", 8);
                    return false;
                }
            })
            $("#inputCityPerCode").on("keypress", function () {
                var textLength = $(this).val().length;
                if (textLength >= 6) {
                    $(this).val($(this).val().substr(0, 6));
                    $(this).prop("maxlength", 6);
                    return false;
                }
            })
            $("#inputZipCode").on("keypress", function () {
                var textLength = $(this).val().length;
                if (textLength >= 10) {
                    $(this).val($(this).val().substr(0, 10));
                    $(this).prop("maxlength", 10);
                    return false;
                }
            })
        //#endregion

    //#endregion

    //#region Handle Valid Values
        $(document).ready(function () {
            // MobileNumberCheck();
            PhoneNumberCheck();
            ZipCodeCheck();
        })
    //#endregion

checkFieldsSendInfo = function () {
    var checks = true;
    if ($("#inputFirstName").val() === '') {
        $("#inputFirstName").addClass("inputshopempty");
        $("#alert-div-inputFirstName-empty").show();
        checks = false;
    }
    else {
    var FirstNameCheck = $("#inputFirstName").val();
	for (var i = 0; i < FirstNameCheck.length; i++)
	{
		var FirstNameChar = FirstNameCheck.charCodeAt(i);
		if (FirstNameChar === 32) {
						
		}
		else if (1578 <= FirstNameChar && FirstNameChar <= 1594 || 1604 <= FirstNameChar && FirstNameChar <= 1608 || 1611 <= FirstNameChar && FirstNameChar <= 1616) {
			
		}
		else if (FirstNameChar === 1570 || FirstNameChar === 1575 || FirstNameChar === 1576 || FirstNameChar === 1662 || FirstNameChar === 1670 || FirstNameChar === 1688 || FirstNameChar === 1601 || FirstNameChar === 1602 || FirstNameChar === 1705 || FirstNameChar === 1711 || FirstNameChar === 1740 || FirstNameChar === 1574) {
			
		}
		else {
			$("#inputFirstName").val('');
			$("#alert-div-inputFirstName-Persian").show();
			$(this).addClass("inputshopempty");
			checks = false;
		}
	}
    }
    if ($("#inputLastName").val() === '') {
        $("#inputLastName").addClass("inputshopempty");
        $("#alert-div-inputLastName-empty").show();
        checks = false;
    }
    var LastNameCheck = $("#inputLastName").val();
	for (var i = 0; i < LastNameCheck.length; i++)
	{
		var LastNameChar = LastNameCheck.charCodeAt(i);
		if (LastNameChar === 32) {
						
		}
		else if (1578 <= LastNameChar && LastNameChar <= 1594 || 1604 <= LastNameChar && LastNameChar <= 1608 || 1611 <= LastNameChar && LastNameChar <= 1616) {
			
		}
		else if (LastNameChar === 1570 || LastNameChar === 1575 || LastNameChar === 1576 || LastNameChar === 1662 || LastNameChar === 1670 || LastNameChar === 1688 || LastNameChar === 1601 || LastNameChar === 1602 || LastNameChar === 1705 || LastNameChar === 1711 || LastNameChar === 1740 || LastNameChar === 1574) {
			
		}
		else {
			$("#inputLastName").val('');
			$("#alert-div-inputLastName-Persian").show();
			$(this).addClass("inputshopempty");
			checks = false;
		}
	}
    if ($("#inputMobileNumber").val() === '') {
        $("#inputMobileNumber").addClass("inputshopempty");
        $("#alert-div-inputMobileNumber-empty").show();
        checks = false;
    }
    else if ($("#inputMobileNumber").val().length !== 11)
    {
        $("#inputMobileNumber").addClass("inputshopempty");
        $("#alert-div-inputMobileNumber-Length").show();
        checks = false;
    }
    else if ($("#inputMobileNumber").val()[0] !== '0' || $("#inputMobileNumber").val()[1] !== '9')
    {
        $("#inputMobileNumber").addClass("inputshopempty");
        $("#alert-div-inputMobileNumber-valid").show();
        checks = false;
    }
    var MobileCheckNumbers = $("#inputMobileNumber").val();
    for (var i = 0; i < MobileCheckNumbers.length; i++)
	{
		var MobileNumberCheckChar = MobileCheckNumbers.charCodeAt(i)
		if (48 <= MobileNumberCheckChar && MobileNumberCheckChar <= 57) {
						
		}
		else {
			$("#inputMobileNumber").val('');
			$("#alert-div-inputMobileNumber-digits").show();
			$(this).addClass("inputshopempty");
			checks = false;
		}
    }
    // if (!ValidMobileNumber)
    // {
    //     checks = false;
    // }
    checks = checkLeftPart();
    return checks;
}

checkLeftPart = function () {
    var checkPart = true;
    stateprofValid = checkDestination($("#inputprofState"));
	bigcityprofValid = checkDestination($("#inputprofBigCity"));
	cityprofValid = checkDestination($("#inputprofCity"));
	if(stateprofValid == false)
	{
        $("#inputprofState_chosen .chosen-single").addClass("inputshopempty_Cat");
        $("#alert-div-inputState-empty").show();
		checkPart = false;
	}
	if(bigcityprofValid == false)
	{
        $("#alert-div-inputBigCity-empty").show();
        $("#inputprofBigCity_chosen .chosen-single").addClass("inputshopempty_Cat");
		checkPart = false;
	}
	if(cityprofValid == false)
	{
        $("#alert-div-inputCity-empty").show();
        $("#inputprofCity_chosen .chosen-single").addClass("inputshopempty_Cat");
		checkPart = false;
	}
    if ($("#inputPhoneNumber").val() === '') {
        $("#inputPhoneNumber").addClass("inputshopempty");
        $("#alert-div-inputPhoneNumber-empty").show();
        checkPart = false;
    }
    else if ($("#inputPhoneNumber").val().length !== 8)
    {
        $("#inputPhoneNumber").addClass("inputshopempty");
        $("#alert-div-inputPhoneNumber-Length").show();
        checkPart = false;
    }
    var PhoneCheckNumbers = $("#inputPhoneNumber").val();
    for (var i = 0; i < PhoneCheckNumbers.length; i++)
	{
		var PhoneNumberCheckChar = PhoneCheckNumbers.charCodeAt(i)
		if (48 <= PhoneNumberCheckChar && PhoneNumberCheckChar <= 57) {
						
		}
		else {
			$("#inputPhoneNumber").val('');
			$("#alert-div-inputPhoneNumber-digits").show();
			$(this).addClass("inputshopempty");
			checkPart = false;
		}
    }
	if ($("#inputCityPerCode").val() === '') {
        $("#inputCityPerCode").addClass("inputshopempty");
        $("#alert-div-inputCityPerCode-empty").show();
        checkPart = false;
    }
    else if ($("#inputCityPerCode").val().length < 3)
    {
        $("#inputCityPerCode").addClass("inputshopempty");
        $("#alert-div-inputCityPerCode-minlength").show();
        checkPart = false;
    }
    var CityPerCodeCheckNumbers = $("#inputCityPerCode").val();
    for (var i = 0; i < CityPerCodeCheckNumbers.length; i++)
	{
		var CityPerCodeCheckChar = CityPerCodeCheckNumbers.charCodeAt(i)
		if (48 <= CityPerCodeCheckChar && CityPerCodeCheckChar <= 57) {
						
		}
		else {
			$("#inputCityPerCode").val('');
			$("#alert-div-inputCityPerCode-digits").show();
			$(this).addClass("inputshopempty");
			checkPart = false;
		}
    }
    if ($("#inputAddress").val() === '') {
        $("#inputAddress").addClass("inputshopempty");
        $("#alert-div-inputAddress-empty").show();
        checkPart = false;
    }
    if ($("#inputZipCode").val() === '') {
        $("#inputZipCode").addClass("inputshopempty");
        $("#alert-div-inputZipCode-empty").show();
        checkPart = false;
    }
    else if ($("#inputZipCode").val().length !== 10)
    {
        $("#inputZipCode").addClass("inputshopempty");
        $("#alert-div-inputZipCode-Length").show();
        checkPart = false;
    }
    var ZipCodeCheckNumbers = $("#inputZipCode").val();
    for (var i = 0; i < ZipCodeCheckNumbers.length; i++)
	{
		var ZipCodeCheckChar = ZipCodeCheckNumbers.charCodeAt(i)
		if (48 <= ZipCodeCheckChar && ZipCodeCheckChar <= 57) {
						
		}
		else {
			$("#inputZipCode").val('');
			$("#alert-div-inputZipCode-digits").show();
			$(this).addClass("inputshopempty");
			checkPart = false;
		}
    }
    // if (!ValidPhoneNumber)
    // {
    //     checkPart = false;
    // }
    // if (!ValidZipCode)
    // {
    //     checkPart = false;
    // }
    return checkPart;
}