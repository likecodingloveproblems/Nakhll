$("#get-code-button").prop('disabled', true);
$("#get-code-button").addClass('login-button-disabled');
$("#alert-li-system-error").hide();

//#region ChangePassword

    // Init ChangePassword Alerts
    initChangePasswordAlerts = function () {
        $(".login-alerts-section").hide();
        $("#alert-li-password").hide();
        $("#alert-li-newpassword").hide();
        $("#alert-li-password-english").hide();
        $("#alert-li-newpassword-no-match").hide();
        $("#alert-li-newpassword-english").hide();
        $("#alert-li-password-minlength").hide();

    $("#alert-li-password").html('وارد کردن رمز الزامی میباشد.');
        
    $("#alert-li-newpassword").html('وارد کردن تکرار رمز الزامی میباشد.');

    $("#alert-li-password-english").html('کیبورد خود را به انگلیسی تغییر دهید.');

    $("#alert-li-newpassword-no-match").html('تکرار رمز با رمز مطابقت ندارد.');
        
    $("#alert-li-newpassword-english").html('کیبورد خود را به انگلیسی تغییر دهید.');

    $("#alert-li-password-minlength").html('رمز عبور بایستی از 8 کاراکتر بیشتر باشد.');
    }
    //#region Initialize MobileAlerts
        // 1.MobileEmpty - خالی بودن فیلد شماره موبایل
        $("#alert-li-mobile-empty").html('شماره موبایل نمیتواند خالی باشد');

        // 2.MobileDigits - استفاده نکردن از اعداد در فیلد شماره موبایل
        $("#alert-li-mobile-digits").html('فقط از اعداد میتوانید استفاده کنید');

        // 3.MobileLength - کمتر از 11 رقم بودن شماره موبایل
        $("#alert-li-mobile-length").html('شماره موبایل باید 11 رقمی باشد');

        // 4.MobileValid - شروع شماره موبایل با غیر از 09
        $("#alert-li-mobile-valid").html('این شماره موبایل معتبر نمیباشد');

        // 5.MobileMatch - وجود داشتن شماره موبایل در سیستم به عنوان ثبت نام شده
        $("#alert-li-mobile-match").html('با این شماره ثبت نام شده است');

        // 6.MobileNotMatch - وجود نداشتن شماره موبایل در سیستم به عنوان ثبت نام شده
        $("#alert-li-mobile-not-match").html('این شماره در سیستم موجود نیست');

    //#endregion

    //#region SystemAlerts
        $("#alert-li-system-error").html('خطا! صفحه را ریلود کرده مجدد سعی نمائید');

    //#endregion

//#endregion

//#region Focusout Event - وقتی فیلد از حالت فکوس خارج شد
$("#mobilenumber").on("focusout", function () {
    var mobileLength = $(this).val().length;
    var ValidMobileNumber = false;
    if ($(this).val() === '') {
        $(this).addClass("fieldEmpty");
        $(".input-mob-forgetpassword").addClass("fieldEmpty");
        $("#alert-li-mobile-empty").show();
        booleans[0] = true;
        $("#alert-li-mobile-length").hide();
        booleans[2] = false;
        $("#alert-li-mobile-valid").hide();
        booleans[3] = false;
        $("#alert-li-mobile-not-match").hide();
        booleans[4] = false;
    }
    else if (mobileLength < 11) {
        $(this).addClass("fieldEmpty");
        $(".input-mob-forgetpassword").addClass("fieldEmpty");
        $("#alert-li-mobile-empty").hide();
        booleans[0] = false;
        $("#alert-li-mobile-length").show();
        booleans[2] = true;
        $("#alert-li-mobile-valid").hide();
        booleans[3] = false;
        $("#alert-li-mobile-not-match").hide();
        booleans[4] = false;
    }
    else if ($(this).val()[0] !== '0' || $(this).val()[1] !== '9') {
        $(this).addClass("fieldEmpty");
        $(".input-mob-forgetpassword").addClass("fieldEmpty");
        $("#alert-li-mobile-empty").hide();
        booleans[0] = false;
        $("#alert-li-mobile-length").hide();
        booleans[2] = false;
        $("#alert-li-mobile-valid").show();
        booleans[3] = true;
        $("#alert-li-mobile-not-match").hide();
        booleans[4] = false;
        $("#alert-li-mobile-match").hide();
        ValidMobileNumber = false;
    }
    else {
        $(this).removeClass("fieldEmpty");
        $(".input-mob-forgetpassword").removeClass("fieldEmpty");
        $("#alert-li-mobile-empty").hide();
        booleans[0] = false;
        $("#alert-li-mobile-length").hide();
        booleans[2] = false;
        $("#alert-li-mobile-valid").hide();
        booleans[3] = false;
        $("#alert-li-mobile-digits").hide();
        booleans[1] = false;
        ValidMobileNumber = true;
    }
    checkIsThereAlert();
})

//#endregion

//#region Input Event - هر تغییری که در فیلد شماره موبایل داده شد
$("#mobilenumber").on("input", function () {
    var mobileLength = $(this).val().length;

    $("#alert-li-mobile-empty").hide();
    booleans[0] = false;
    $(this).removeClass('fieldEmpty');
    $(".input-mob-forgetpassword").removeClass("fieldEmpty");
    
    if (mobileLength === 11) {
        $("#alert-li-mobile-length").hide();
        booleans[2] = false;
        if ($(this).val()[0] === '0' && $(this).val()[1] === '9') {
            $("#alert-li-mobile-valid").hide();
            $(this).removeClass('fieldEmpty');
            $(".input-mob-forgetpassword").removeClass("fieldEmpty");
            booleans[3] = false;
            ValidMobileNumber = true;
        }
        else if ($(this).val()[0] !== '0' || $(this).val()[1] !== '9') {
            $("#alert-li-mobile-valid").show();
            booleans[3] = true;
            $(this).addClass('fieldEmpty');
            $(".input-mob-forgetpassword").addClass("fieldEmpty");
            $("#alert-li-mobile-not-match").hide();
            booleans[4] = false;
            ValidMobileNumber = false;
        }
    }
    checkIsThereAlert();
})

//#endregion

//#region KeyPress Event - زمانی که در فیلد کلیدی از کلیدهای کیبورد فشرده شد
$("#mobilenumber").on("keypress", function (event) {
    var ew = event.which;
    if (48 <= ew && ew <= 57) {
        $("#alert-li-mobile-digits").hide();
        booleans[1] = false;
        $(this).removeClass("fieldEmpty");
        $(".input-mob-forgetpassword").removeClass("fieldEmpty");
        checkIsThereAlert();
        return true;
    }
    else if (ew === 13) {

    }
    else {
        $("#alert-li-mobile-digits").show();
        booleans[1] = true;
        $(this).addClass("fieldEmpty");
        $(".input-mob-forgetpassword").addClass("fieldEmpty");
        checkIsThereAlert();
        return false;
    }
})

//#endregion

//#region Paste Event - هنگام الحاق کردن به فیلد شماره موبایل
$("#mobilenumber").on("paste", function () {
    var evm;
    setTimeout(function () {
        var textLength = $("#mobilenumber").val().length;
        if (textLength >= 11) {
        $("#mobilenumber").val($("#mobilenumber").val().substr(0, 11));
        $("#mobilenumber").prop("maxlength", 11);
        }
        var datamobile = $("#mobilenumber").val();
        for (var i = 0; i < datamobile.length; i++) {
            evm = datamobile.charCodeAt(i);
            if (48 <= evm && evm <= 57) {
            }
            else {
                $("#mobilenumber").val('');
                $("#mobilenumber").addClass('fieldEmpty');
                $(".input-mob-forgetpassword").addClass("fieldEmpty");         
                $("#alert-li-mobile-digits").show();
                booleans[1] = true;
                return false;
            }
        }
    }, 10)
    setTimeout(function () {
        if ($("#mobilenumber").val() !== '') {
            $("#alert-li-mobile-digits").hide();
            $("#mobilenumber").removeClass('fieldEmpty');
            $(".input-mob-forgetpassword").removeClass("fieldEmpty");
            booleans[1] = false;
        }
    }, 20)
    checkIsThereAlert();
})
//#endregion

//#region KeyPress & Paste Event - هنگام الحاق کردن یا فشردن کلیدی از کیبورد در فیلد شماره موبایل
$("#mobilenumber").on("keypress", function () {
    var textLength = $(this).val().length;
    if (textLength >= 11) {
        $(this).val($(this).val().substr(0, 11));
        $(this).prop("maxlength", 11);
        return false;
    }
})

//#endregion

//#endregion

//#region HideAlerts

// 1.Hide MobileAlerts
$("#alert-li-mobile-empty").hide();
$("#alert-li-mobile-digits").hide();
$("#alert-li-mobile-length").hide();
$("#alert-li-mobile-valid").hide();
$("#alert-li-mobile-match").hide();
$("#alert-li-mobile-not-match").hide();

// 2.Hide SystemAlerts
$("#alert-li-system-error").hide();

//#endregion

initAlerts = function () {
    $("#alert-li-username").hide();
    $("#alert-li-firstname").hide();
    $("#alert-li-lastname").hide();
    $("#alert-li-name-persian").hide();
    $("#alert-li-nation").hide();
    $("#alert-li-password").hide();
    $("#alert-li-newpassword").hide();
    $("#alert-li-username-dup").hide();
    $("#alert-li-username-system-error").hide();
    $("#alert-li-nation-digits").hide();
    $("#alert-li-password-english").hide();
    $("#alert-li-newpassword-no-match").hide();
    $("#alert-li-newpassword-english").hide();
    $("#alert-li-username-english").hide();
    $("#alert-li-nationcode-dup").hide();
    $("#alert-li-nationcode-system-error").hide();
    $("#alert-li-password-minlength").hide();
    $(".login-alerts-section").hide();
    
    $("#alert-li-firstname").html('نام نمیتواند خالی باشد.');
    $("#alert-li-name-persian").html('از حروف فارسی برای نام و نام خانوادگی استفاده نمائید.');
    
    $("#alert-li-lastname").html('نام خانوادگی نمیتواند خالی باشد.');

    $("#alert-li-nation").html('وارد کردن کد ملی الزامی میباشد.');

    $("#alert-li-password").html('وارد کردن رمز الزامی میباشد.');

    $("#alert-li-newpassword").html('وارد کردن تکرار رمز الزامی میباشد.');

    $("#alert-li-username-dup").html('این نام کاربری تکراری میباشد.');

    $("#alert-li-username-system-error").html('خطا! صفحه را رفرش کرده مجددا سعی کنید.');

    $("#alert-li-nation-digits").html('فقط از اعداد میتوانید استفاده کنید.');

    $("#alert-li-username-english").html('فقط حروف انگلیسی، اعداد و "_" مجاز هستند.');

    $("#alert-li-password-english").html('کیبورد خود را به انگلیسی تغییر دهید.');

    $("#alert-li-newpassword-no-match").html('تکرار رمز با رمز مطابقت ندارد.');

    $("#alert-li-username").html('وارد کردن نام کاربری الزامی است.');

    $("#alert-li-nationcode-dup").html('با این کد ملی ثبت نام شده است.');

    $("#alert-li-nationcode-system-error").html('خطا! صفحه را رفرش کرده مجددا سعی کنید.');

    $("#alert-li-newpassword-english").html('کیبورد خود را به انگلیسی تغییر دهید.');

    $("#alert-li-password-minlength").html('رمز عبور بایستی از 8 کاراکتر بیشتر باشد.');

}
initUsernameAlert = function () {
    $("#username").on("focusout", function() {
        if ($(this).val() === '') {
            $("#alert-li-username").show();
            booleansReg[6] = true;
            $(this).addClass('fieldEmpty');
    }
        else {
            $("#alert-li-username").hide();
            booleansReg[6] = false;
            $(this).removeClass('fieldEmpty');
        }
        checkIsThereAlertReg();
    })
    
    $("#username").on("input", function() {
        if ($(this).val() !== '') {
            $("#alert-li-username").hide();
            booleansReg[6] = false;
            $("#alert-li-username-dup").hide();
            booleansReg[8] = false;
            $(this).removeClass('fieldEmpty');
        }
        checkIsThereAlertReg();
    })
    $("#username").on("paste", function() {
        setTimeout(function() {
        if ($(this).val() !== '') {
            $("#alert-li-username").hide();
            booleansReg[6] = false;
            $("#alert-li-username-dup").hide();
            booleansReg[8] = false;
            $(this).removeClass('fieldEmpty');
        }
        checkIsThereAlertReg();
        })
    })
    $("#username").on('keypress', function (event) {
        var ev = event.which;
        if (ev === 32) {
            $("#alert-li-username-english").hide();
            booleansReg[7] = false;
            checkIsThereAlertReg();
            return true;
        }
        else if (48 <= ev && ev <= 57)
        {
            $("#alert-li-username-english").hide();
            booleansReg[7] = false;
            checkIsThereAlertReg();
            return true;
        }
        else if (65 <= ev && ev <= 90)
        {
            $("#alert-li-username-english").hide();
            booleansReg[7] = false;
            checkIsThereAlertReg();
            return true;
        }
        else if (97 <= ev && ev <= 122)
        {
            $("#alert-li-username-english").hide();
            booleansReg[7] = false;
            checkIsThereAlertReg();
            return true;
        }
        else if (ev === 95)
        {
            $("#alert-li-username-english").hide();
            booleansReg[7] = false;
            checkIsThereAlertReg();
            return true;
        }
        else if (ev === 13) {
            
        }
        else {  
            $("#alert-li-username-english").show();
            booleansReg[7] = true;
            checkIsThereAlertReg();
            return false;
        }
    })
    $("#username").on("focusout", function(){
        if (($("#email").val() === '' || $("#email").val().includes('@nakhll.com')) && $(this).val() !== '') {
            $("#email").val($(this).val() + '@nakhll.com')
        }
    })
    var evu;
    $("#username").on("paste", function () {
        setTimeout(function(){
            var datausername = $("#username").val();
            for(var i=0; i<datausername.length; i++)
            {
                evu = datausername.charCodeAt(i);
                if (evu === 32)
                {
                }
                else if (48 <= evu && evu <= 57)
                {
                }
                else if (65 <= evu && evu <= 90)
                {
                }
                else if (97 <= evu && evu <= 122)
                {
                }
                else if (evu === 95)
                {
                }
                else {
                    $("#username").val('');
                    $("#username").addClass('fieldEmpty');
                    $("#alert-li-username-english").show();
                    booleansReg[7] = true;
                    checkIsThereAlertReg();
                    return false;
                }
            }
        }, 10)
        setTimeout(function () {
            if($("#username").val() !== '')
            {
                $("#alert-li-username").hide();
                booleansReg[6] = false;
                $("#alert-li-username-english").hide();
                booleansReg[7] = false;
                $("#username").removeClass('fieldEmpty');
                checkIsThereAlertReg();
            }
        }, 20)
    })
    var firstUsernameFocusIn = true;
    $("#username").click(function () {
        if (firstUsernameFocusIn)
        {
            $(this).val('');
            firstUsernameFocusIn = false;
        }
    })
}
initFirstNameAlert = function() {
    $("#firstname").on("focusout", function() {
        if ($(this).val() === '') {
            $("#alert-li-firstname").show();
            booleansReg[0] = true;
            $(this).addClass('fieldEmpty');
        }
        else {
            $("#alert-li-firstname").hide();
            booleansReg[0] = false;
            $(this).removeClass('fieldEmpty');
            $("#alert-li-name-persian").hide();
            booleansReg[16] = false;
        }
        checkIsThereAlertReg();
    })
    $("#firstname").on("input", function() {
        if ($(this).val() !== '') {
            $("#alert-li-firstname").hide();
            booleansReg[0] = false;
            $(this).removeClass('fieldEmpty');
            
            var data = $("#firstname").val();
            var ews = data.charCodeAt(data.length-1);
            if (1574 <= ews && ews <= 1594 || 1601 <= ews && ews <= 1608) {
                $("#alert-li-name-persian").hide();
                $("#firstname").removeClass("fieldEmpty");
                booleansReg[16] = false;
            }
            else if (ews === 32 || ews === 1570 || ews === 1662 || ews === 1670 || ews === 1688 || ews === 1705 || ews === 1711 || ews === 1740) {
                $("#alert-li-name-persian").hide();
                $("#firstname").removeClass("fieldEmpty");
                booleansReg[16] = false;
            }
            else if (ews === 13) {
                
            }
            else {
                $("#firstname").val($("#firstname").val().substr(0, data.length-1));
                $("#alert-li-name-persian").show();
                booleansReg[16] = true;
                $("#firstname").addClass("fieldEmpty");
            }
        }
        checkIsThereAlertReg();
    })
    $("#firstname").on("paste drop", function() {
        setTimeout(function(){
            var data = $("#firstname").val();
            for(var i=0; i<data.length; i++)
            {
                var ews = data.charCodeAt(i);
                if (1574 <= ews && ews <= 1594 || 1601 <= ews && ews <= 1608) {
                    
                }
                else if (ews === 32 || ews === 1570 || ews === 1662 || ews === 1670 || ews === 1688 || ews === 1705 || ews === 1711 || ews === 1740) {
                    
                }
                else {
                    $("#firstname").val('');
                    $("#alert-li-name-persian").show();
                    $("#firstname").addClass("fieldEmpty");
                    return false;
                }
            }
        }, 10)
        setTimeout(function () {
            if($("#firstname").val() !== '')
            {
                $("#alert-li-firstname").hide();
                booleansReg[0] = false;
                $("#alert-li-name-persian").hide();
                booleansReg[16] = false;
                $("#firstname").removeClass("fieldEmpty");	
            }
            checkIsThereAlertReg();
        }, 20)
    })
    var firstFirstNameFocusIn = true;
    $("#firstname").click(function () {
        if (firstFirstNameFocusIn)
        {
            $(this).val('');
            firstFirstNameFocusIn = false;
        }
    })
}
initLastNameAlert = function() {
    $("#lastname").on("focusout", function() {
        if ($(this).val() === '') {
            $("#alert-li-lastname").show();
            booleansReg[1] = true;
            $(this).addClass('fieldEmpty');
        }
        else {
            $("#alert-li-lastname").hide();
            booleansReg[1] = false;
            $(this).removeClass('fieldEmpty');
            $("#alert-li-name-persian").hide();
            booleansReg[16] = false;
        }
        checkIsThereAlertReg();
    })
    $("#lastname").on("input", function() {
        if ($(this).val() !== '') {
            $("#alert-li-lastname").hide();
            booleansReg[1] = false;
            $(this).removeClass('fieldEmpty');
            
            var data = $("#lastname").val();
            var ews = data.charCodeAt(data.length-1);
            if (1574 <= ews && ews <= 1594 || 1601 <= ews && ews <= 1608) {
                $("#alert-li-name-persian").hide();
                $("#lastname").removeClass("fieldEmpty");
                booleansReg[16] = false;
            }
            else if (ews === 1570 || ews === 1662 || ews === 1670 || ews === 1688 || ews === 1705 || ews === 1711 || ews === 1740) {
                $("#alert-li-name-persian").hide();
                $("#lastname").removeClass("fieldEmpty");
                booleansReg[16] = false;
            }
            else if (ews === 13) {

            }
            else {
                $("#lastname").val($("#lastname").val().substr(0, data.length-1));
                $("#alert-li-name-persian").show();
                booleansReg[16] = true;
                $("#lastname").addClass("fieldEmpty");
            }
    }
    checkIsThereAlertReg();
    })
    $("#lastname").on("paste", function() {
        setTimeout(function(){
            var data = $("#lastname").val();
            for(var i=0; i<data.length; i++)
            {
                var ews = data.charCodeAt(i);
                if (1574 <= ews && ews <= 1594 || 1601 <= ews && ews <= 1608) {
                    
                }
                else if (ews === 32 || ews === 1570 || ews === 1662 || ews === 1670 || ews === 1688 || ews === 1705 || ews === 1711 || ews === 1740) {
                    
                }
                else {
                    $("#lastname").val('');
                    $("#alert-li-name-persian").show();
                    $("#lastname").addClass("fieldEmpty");
                    return false;
                }
            }
        }, 10)
        setTimeout(function () {
            if($("#lastname").val() !== '')
            {
                $("#alert-li-lastname").hide();
                booleansReg[1] = false;
                $("#alert-li-name-persian").hide();
                booleansReg[16] = false;
                $("#lastname").removeClass("fieldEmpty");	
            }
            checkIsThereAlertReg();
        }, 20)
    })
    var firstLastNameFocusIn = true;
    $("#lastname").click(function () {
        if (firstLastNameFocusIn)
        {
            $(this).val('');
            firstLastNameFocusIn = false;
        }
    })
}
initNationAlert = function() {
    $("#nactioncode").on("focusout", function() {
        if ($(this).val() === '') {
            $("#alert-li-nation").show();
            booleansReg[2] = true;
            $(this).addClass('fieldEmpty');
    }
    else {
        $("#alert-li-nation").hide();
        booleansReg[2] = false;
        $("#alert-li-nation-digits").hide();
        booleansReg[3] = false;
        $("#alert-li-nationcode-dup").hide();
        booleansReg[4] = false;
        $(this).removeClass('fieldEmpty');
    }
    checkIsThereAlertReg();
    })
    $("#nactioncode").on("input", function() {
        if ($(this).val() !== '') {
            $("#alert-li-nation").hide();
            booleansReg[2] = false;
            $("#alert-li-nationcode-dup").hide();
            booleansReg[4] = false;
            $(this).removeClass('fieldEmpty');
    }
    checkIsThereAlertReg();
    })
    var nationCodeLength;
    $("#nactioncode").on("keypress", function() {
        nationCodeLength = $(this).val().length;
        if (nationCodeLength >= 10) {
            $(this).val($(this).val().substr(0, 10));
            $(this).prop("maxlength", 10);
            return false;
        }
    })
    $("#nactioncode").on("keypress", function(event) {
        var eve = event.which;
        if (48 <= eve && eve <= 57) {
            $("#alert-li-nation-digits").hide();
            booleansReg[3] = false;
            checkIsThereAlertReg();
            return true;
        }
        else if (eve === 13) {
        
        }
        else {
            $("#alert-li-nation-digits").show();
            booleansReg[3] = true;
            checkIsThereAlertReg();
            return false;
        }
    })
    var evn;
    $("#nactioncode").on("paste", function () {
        setTimeout(function(){
            nationCodeLength = $("#nactioncode").val().length;
            if (nationCodeLength >= 10) {
            $("#nactioncode").val($("#nactioncode").val().substr(0, 10));
            $("#nactioncode").prop("maxlength", 10);
        }
            var datanation = $("#nactioncode").val();
            for(var i=0; i<datanation.length; i++)
            {
                evn = datanation.charCodeAt(i);
                if (48 <= evn && evn <= 57)
                {
                }
                else {
                    $("#nactioncode").val('');
                    $("#nactioncode").addClass('fieldEmpty');
                    $("#alert-li-nation-digits").show();
                    booleansReg[3] = true;
                    checkIsThereAlertReg();
                    return false;
                }
            }
            checkIsThereAlertReg();
    }, 10)
        setTimeout(function () {
            if($("#nactioncode").val() !== '')
            {
                $("#alert-li-nactioncode").hide();
                booleansReg[2] = false;
                $("#alert-li-nation-digits").hide();
                booleansReg[3] = false;
                $("#nactioncode").removeClass('fieldEmpty');
            }
            checkIsThereAlertReg();
        }, 20)
    })
    var firstNationalCodeFocusIn = true;
    $("#nactioncode").click(function () {
        if (firstNationalCodeFocusIn)
        {
            $(this).val('');
            firstNationalCodeFocusIn = false;
        }
    })
}
initEmailAlert = function () {
    var firstEmailFocusIn = true;
    $("#email").click(function () {
        if (firstEmailFocusIn)
        {
            $(this).val('');
            firstEmailFocusIn = false;
        }
    })
}
var matchPasswords = false;
initPasswordAlert = function() {
    $("#password").on("focusout", function() {
        if ($(this).val() === '') {
            $("#alert-li-password").show();
            booleans[0] = true;
            booleansReg[10] = true;
            $(this).addClass('fieldEmpty');
            $(".input-password-change").addClass('fieldEmpty');
        }
        else if ($(this).val().length < 8) {
            $("#alert-li-password-minlength").show();
            booleans[5] = true;
            booleansReg[12] = true;
            $("#alert-li-password-english").hide();
            booleans[3] = false;
            booleansReg[11] = false;
            $(this).addClass('fieldEmpty');
            $(".input-password-change").addClass('fieldEmpty');
        }
        else {
            $("#alert-li-password-minlength").hide();
            booleans[5] = false;
            booleansReg[12] = false;
            $("#alert-li-password-english").hide();
            booleans[3] = false;
            booleansReg[11] = false;
            $("#alert-li-password").hide();
            booleans[0] = false;
            booleansReg[10] = false;
            $(this).removeClass('fieldEmpty');
            $(".input-password-change").removeClass('fieldEmpty');
            if ($("#newpassword").val() !== '' && $("#newpassword").val() !== $("#password").val()) {
                $("#alert-li-newpassword-no-match").show();
                booleans[4] = true;
                booleansReg[14] = true;
                $("#newpassword").addClass('fieldEmpty');
                $(".input-password-change2").addClass('fieldEmpty');
                matchPasswords = false;
            }
            else if ($("#newpassword").val() === $("#password").val())
                {
                    $("#alert-li-newpassword-no-match").hide();
                    booleans[4] = false;
                    booleansReg[14] = false;
                    $("#newpassword").removeClass('fieldEmpty');
                    $(".input-password-change2").removeClass('fieldEmpty');
                    matchPasswords = true;
                }
        }
        checkIsThereAlertp();
    })
    $("#password").on("input", function() {
        if ($(this).val() !== '') {
            $("#alert-li-password").hide();
            booleans[0] = false;
            booleansReg[10] = false;
            $(this).removeClass('fieldEmpty');
            $(".input-password-change").removeClass('fieldEmpty');
        }
        if ($(this).val().length >= 8) {
            $("#alert-li-password-minlength").hide();
            booleans[5] = false;
            booleansReg[12] = false;
            $(this).removeClass('fieldEmpty');
            $(".input-password-change").removeClass('fieldEmpty');
        }
        checkIsThereAlertp();
    })
    $("#password").on("keypress", function (event) {
        var evp = event.which;
        if (32 <= evp && evp <= 126)
        {
            $("#alert-li-password-english").hide();
            booleans[3] = false;
            booleansReg[11] = false;
            checkIsThereAlertp();
            return true;
        }
        else if (evp === 13) {
        
        }
        else {    
            $("#alert-li-password-english").show();
            booleans[3] = true;
            booleansReg[11] = true;
            checkIsThereAlertp();
            return false;
        }
    })
    var evp;
    $("#password").on("paste", function () {
        setTimeout(function(){
            var data = $("#password").val();
            for(var i=0; i<data.length; i++)
            {
                evp = data.charCodeAt(i);
                if (32 <= evp && evp <= 126)
                {
                }
                else {
                    $("#password").val('');
                    $("#password").addClass('fieldEmpty');
                    $(".input-password-change").addClass('fieldEmpty');
                    $("#alert-li-password-english").show();
                    booleans[2] = true;
                    booleansReg[11] = true;
                    checkIsThereAlert();
                    return false;
                }
            }
    }, 10)
        setTimeout(function () {
            if($("#password").val() !== '')
            {
                $("#alert-li-password").hide();
                booleans[0] = false;
                booleansReg[10] = false;
                $("#alert-li-password-english").hide();
                booleans[2] = false;
                booleansReg[11] = false;
                $("#password").removeClass('fieldEmpty');
                $(".input-password-change").removeClass('fieldEmpty');
                checkIsThereAlertp();
            }
        }, 20)
    })
    var firstPasswordSignUpFocusIn = true;
    $("#password").click(function () {
        if (firstPasswordSignUpFocusIn)
        {
            $(this).val('');
            firstPasswordSignUpFocusIn = false;
        }
    })
}
var evnp;
initNewPasswordAlert = function() {
    $("#newpassword").on("focusout", function() {
        if ($(this).val() === '') {
            $("#alert-li-newpassword").show();
            booleans[1] = true;
            booleansReg[13] = true;
            $(this).addClass('fieldEmpty');
            $(".input-password-change2").addClass('fieldEmpty');
        }
        else {
            $("#alert-li-newpassword-english").hide();
            booleans[3] = false;
            booleansReg[15] = false;
            $("#alert-li-newpassword").hide();
            booleans[1] = false;
            booleansReg[13] = false;
            $(this).removeClass('fieldEmpty');
            $(".input-password-change2").removeClass('fieldEmpty');
            if ($("#newpassword").val() !== $("#password").val())
            {
                $("#alert-li-newpassword-no-match").show();
                booleans[4] = true;
                booleansReg[14] = true;
                $("#newpassword").addClass('fieldEmpty');
                $(".input-password-change2").addClass('fieldEmpty');
                matchPasswords = false;
            }
            else if ($("#newpassword").val() === $("#password").val())
            {
                $("#alert-li-newpassword-no-match").hide();
                booleans[4] = false;
                booleansReg[14] = false;
                $("#newpassword").removeClass('fieldEmpty');
                $(".input-password-change2").removeClass('fieldEmpty');
                matchPasswords = true;
            }
        }
        checkIsThereAlertp();
    })
    $("#newpassword").on("input", function() {
        if ($(this).val() !== '') {
            $("#alert-li-newpassword").hide();
            booleans[1] = false;
            booleansReg[13] = false;
            $("#alert-li-newpassword-no-match").hide();
            booleans[4] = false;
            booleansReg[14] = false;
            $(this).removeClass('fieldEmpty');
            $(".input-password-change2").removeClass('fieldEmpty');
        }
        checkIsThereAlertp();
    })
    $("#newpassword").on("keypress", function (event) {
        var evnp = event.which;
        if (32 <= evnp && evnp <= 126)
        {
            $("#alert-li-newpassword-english").hide();
            booleans[3] = false;
            booleansReg[15] = false;
            checkIsThereAlertp();
            return true;
        }
        else if (evnp === 13) {
        
        }
        else {    
            $("#alert-li-newpassword-english").show();
            booleans[3] = true;
            booleansReg[15] = true;
            checkIsThereAlertp();
            return false;
        }
    })
    var evnp;
    $("#newpassword").on("paste", function () {
        setTimeout(function(){
            var data = $("#newpassword").val();
            for(var i=0; i<data.length; i++)
            {
                evnp = data.charCodeAt(i);
                if (32 <= evnp && evnp <= 126)
                {
                }
                else {
                    $("#newpassword").val('');
                    $("#newpassword").addClass('fieldEmpty');
                    $(".input-password-change2").addClass('fieldEmpty');
                    $("#alert-li-newpassword-english").show();
                    booleans[3] = true;
                    booleansReg[15] = true;
                    checkIsThereAlertp();
                    return false;
                }
            }
    }, 10)
        setTimeout(function () {
            if($("#newpassword").val() !== '')
            {
                $("#alert-li-newpassword").hide();
                booleans[1] = false;
                booleansReg[13] = false;
                $("#alert-li-newpassword-english").hide();
                booleans[3] = false;
                booleansReg[15] = false;
                $("#newpassword").removeClass('fieldEmpty');
                $(".input-password-change2").removeClass('fieldEmpty');
                checkIsThereAlertp();
            }
        }, 20)
    })
    var firstNewPasswordSignUpFocusIn = true;
    $("#newpassword").click(function () {
        if (firstNewPasswordSignUpFocusIn)
        {
            $(this).val('');
            firstNewPasswordSignUpFocusIn = false;
        }
    })
}
var melliCodeCheking = false;
var checkEmpty = false;
var checkNationalCode = false;
var checkUsername = false;
var checkMatchPasswords = false;
initSignUpButton = function () {
    $("#sign-up-button2").on("click", function() {
        checkEmpty = checkInputValues();
        checkNationalCode = (melliCodeCheking && nationcodechecking) ? true : false;
        checkUsername = usernamechecking;
        checkMatchPasswords = matchPasswords;
        if (checkEmpty && checkNationalCode && checkUsername && checkMatchPasswords)
        {
            return true;
        }
        else
        {
            return false;
        }
    })
}
checkInputValues = function () {
    var firstnameCheck = { name: '#alert-li-firstname', validation: $("#firstname").val() !== '', bool: 0 };
    var lastnameCheck = { name: '#alert-li-lastname', validation: $("#lastname").val() !== '', bool: 1};
    var nationCheck = { name: '#alert-li-nation', validation: $("#nactioncode").val() !== '', bool: 2 };
    var usernameCheck = { name: '#alert-li-username', validation: $("#username").val() !== '', bool: 6 };
    var passwordCheck = { name: '#alert-li-password', validation: $("#password").val() !== '', bool: 10 };
    var newpasswordCheck = { name: '#alert-li-newpassword', validation: $("#newpassword").val() !== '', bool: 13 };
    var checkList = [firstnameCheck, lastnameCheck, nationCheck, usernameCheck, passwordCheck, newpasswordCheck];
    var checkResult = true;
    for (var i = 0; i < checkList.length; i++) {
        if (!checkList[i].validation) {
            $(checkList[i].name).show();
            if (i > 3)
            {
                $(".reg-page-pass-alerts").show();
            }
            else if (i <= 3)
            {
                $(".reg-page-alerts").show();
            }
            
            checkResult = false
        }
    }
    return checkResult;
}

changePasswordButton = function () {
    $("#change-password-button").on("click", function(){
        if($("#password").val() !== '' && $("#newpassword").val() !== '') {
            if (($("#password").val() == $("#newpassword").val()) && $("#password").val().length >= 8)
            {
                return true;
            }
            else
            {
                $("#alert-li-newpassword-no-match").show();
                booleans[4] = true;
                $("#newpassword").addClass('fieldEmpty');
                $(".input-password-change2").addClass('fieldEmpty');
                checkIsThereAlertp();
                return false;
            }
        }
        else if ($("#password").val() === '') {
            $("#alert-li-password").show();
            booleans[0] = true;
            $("#password").addClass('fieldEmpty');
            $(".input-password-change").addClass('fieldEmpty');
            if($("#newpassword").val() === '') {
                $("#alert-li-newpassword").show();
                booleans[1] = true;
                $("#newpassword").addClass('fieldEmpty');
                $(".input-password-change2").addClass('fieldEmpty');
            }
            checkIsThereAlertp();
            return false;
        }
        else if ($("#newpassword").val() === '') {
            $("#alert-li-newpassword").show();
            booleans[1] = true;
            $("#newpassword").addClass('fieldEmpty');
            $(".input-password-change2").addClass('fieldEmpty');
            checkIsThereAlert();
            return false;
        }
    })
}