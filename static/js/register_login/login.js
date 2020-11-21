//#region Initialize Login
    
    //#region HideAlerts

// 1.Hide MobileAlerts
$("#alert-li-mobile-empty").hide();
$("#alert-li-mobile-digits").hide();
$("#alert-li-mobile-length").hide();
$("#alert-li-mobile-valid").hide();
$("#alert-li-mobile-match").hide();

// 2.Hide PasswordAlerts
$("#alert-li-password-empty").hide();
$("#alert-li-password-english").hide();

// 3.Hide SystemAlerts
$("#alert-li-system-error").hide();

//#endregion
    
    //#region HideLoaderDiv
        $("#loaderDiv").hide();

    //#endregion

    //#region LoginButton

// 1.ButtonDisable - غیر فعال کردن دکمه ورود
// $("#login-button").prop('disabled', true);
// $("#login-button").addClass('login-button-disabled');

//#endregion

    //#region MobileAlerts

// 1.MobileEmpty - خالی بودن فیلد شماره موبایل
$("#alert-li-mobile-empty").html('شماره موبایل نمیتواند خالی باشد.');

// 2.MobileDigits - استفاده نکردن از اعداد در فیلد شماره موبایل
$("#alert-li-mobile-digits").html('در فیلد شماره موبایل فقط اعداد مجاز هستند.');

// 3.MobileLength - کمتر از 11 رقم بودن شماره موبایل
$("#alert-li-mobile-length").html('شماره موبایل باید 11 رقمی باشد.');

// 4.MobileValid - شروع شماره موبایل با غیر از 09
$("#alert-li-mobile-valid").html('این شماره موبایل معتبر نمیباشد.');

// 5.MobileMatch - وجود نداشتن شماره موبایل در سیستم به عنوان ثبت نام شده
$("#alert-li-mobile-match").html('این شماره در سیستم موجود نیست.');
//#endregion

    //#region PasswordAlerts

// 1.PasswordEmpty - خالی گذاشتن فیلد رمز عبور
$("#alert-li-password-empty").html('وارد کردن پسورد الزامی میباشد.');

// 2.PasswordEnglish - استفاده کردن از حروف فارسی در فیلد رمز عبور
$("#alert-li-password-english").html('برای رمز عبور از زبان انگلیسی استفاده نمائید.');

//#endregion

    //#region SystemAlerts
        $("#alert-li-system-error").html('خطا! صفحه را ریلود کرده مجدد سعی نمائید.');
    
    //#endregion

//#endregion

//#region Show Alerts By Event

    //#region MobileAlerts

        //#region Focusout Event - وقتی فیلد از حالت فکوس خارج شد
            $("#mobilenumber").on("focusout", function () {
                var mobileLength = $(this).val().length;
                var ValidMobileNumber = false;
                if ($(this).val() === '') {
                    $(this).addClass("fieldEmpty");
                    $(".input-mob-login").addClass("fieldEmpty");
                    $("#alert-li-mobile-empty").show();
                    booleans[0] = true;
                    $("#alert-li-mobile-length").hide();
                    booleans[2] = false;
                    $("#alert-li-mobile-valid").hide();
                    booleans[3] = false;
                }
                else if (mobileLength < 11) {
                    $(this).addClass("fieldEmpty");
                    $(".input-mob-login").addClass("fieldEmpty");
                    $("#alert-li-mobile-empty").hide();
                    booleans[0] = false;
                    $("#alert-li-mobile-length").show();
                    booleans[2] = true;
                    $("#alert-li-mobile-valid").hide();
                    booleans[3] = false;
                }
                else if ($(this).val()[0] !== '0' || $(this).val()[1] !== '9') {
                    $(this).addClass("fieldEmpty");
                    $(".input-mob-login").addClass("fieldEmpty");
                    $("#alert-li-mobile-empty").hide();
                    booleans[0] = false;
                    $("#alert-li-mobile-length").hide();
                    booleans[2] = false;
                    $("#alert-li-mobile-valid").show();
                    booleans[3] = true;
                    ValidMobileNumber = false;
                }
                else {
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
                $(".input-mob-login").removeClass("fieldEmpty");

                if (mobileLength === 11) {
                    $("#alert-li-mobile-length").hide();
                    booleans[2] = false;
                    if ($(this).val()[0] === '0' && $(this).val()[1] === '9') {
                        $("#alert-li-mobile-valid").hide();
                        booleans[3] = false;
                        ValidMobileNumber = true;
                    }
                    else if ($(this).val()[0] !== '0' || $(this).val()[1] !== '9') {
                        $("#alert-li-mobile-valid").show();
                        booleans[3] = true;
                        $("#alert-li-mobile-match").hide();
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
                    checkIsThereAlert();
                    return true;
                }
                else if (ew === 13)
                {
                    
                }
                else {
                    $("#alert-li-mobile-digits").show();
                    booleans[1] = true;
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
                            $(".input-mob-login").addClass("fieldEmpty");    
                            $("#alert-li-mobile-digits").show();
                            booleans[1] = true;
                            return false;
                        }
                    }
                }, 10)
                setTimeout(function () {
                    if ($("#mobilenumber").val() !== '') {
                        $("#alert-div-mobile-digits").hide();
                        $("#mobilenumber").removeClass('fieldEmpty');
                        $(".input-mob-login").removeClass("fieldEmpty");
                    }
                }, 20)
                checkIsThereAlert();
            })
        //#endregion
        
        //#region KeyPress Event - هنگام فشردن کلیدی از کیبورد در فیلد شماره موبایل
            $("#mobilenumber").on("keypress", function () {
                var textLength = $(this).val().length;
                if (textLength >= 11) {
                    $(this).val($(this).val().substr(0, 11));
                    $(this).prop("maxlength", 11);
                    return false;
                }
            })

        //#endregion
        
        //#region Focusin Event - اولین بار کلیک روی فیلد موبایل منجر به پاک شدن متن از پیش پر شده
            var firstMobFocusIn = true;
            $("#mobilenumber").click(function () {
                if (firstMobFocusIn)
                {
                    $(this).val('');
                    if (firstPassFocusIn) {
                        $("#password").val('');
                    }
                    firstMobFocusIn = false;
                }
            })
        //#endregion

    //#endregion

    //#region PasswordAlerts

            //#region Focusout Event
                $("#password").on("focusout", function () {
                    if ($(this).val() === '') {
                        $(this).addClass("fieldEmpty");
                        $(".input-password-login").addClass("fieldEmpty");
                        $("#alert-li-password-empty").show();
                        booleans[5] = true;
                    }
                    else {
                        $(this).removeClass("fieldEmpty");
                        $(".input-password-login").removeClass("fieldEmpty");
                        $("#alert-li-password-empty").hide();
                        booleans[5] = false;
                        $("#alert-li-password-english").hide();
                        booleans[6] = false;
                        // if (RegisteredMobileNumber)
                        // {
                        //     $("#login-button").prop("disabled", false);
                        //     $("#login-button").removeClass("login-button-disabled");
                        // }
                    }
                    checkIsThereAlert();
                })

            //#endregion

            //#region Input Event
                $("#password").on("input", function () {
                    if ($(this).val() !== '') {
                        $(this).removeClass("fieldEmpty");
                        $(".input-password-login").removeClass("fieldEmpty");
                        $("#alert-li-password-empty").hide();
                        booleans[5] = false;
                        // if (RegisteredMobileNumber)
                        // {
                        //     $("#login-button").prop("disabled", false);
                        //     $("#login-button").removeClass("login-button-disabled");
                        // }
                    }
                    // else {
                    //     $("#login-button").prop("disabled", true);
                    //     $("#login-button").addClass("login-button-disabled");
                    // }
                    checkIsThereAlert();
                })

            //#endregion

            //#region Keypress Event
                $("#password").on("keypress", function (event) {
                    var ev = event.which;
                    if (32 <= ev && ev <= 126)
                    {
                        $("#alert-li-password-english").hide();
                        booleans[6] = false;
                        checkIsThereAlert();
                        return true;
                    }
                    else if (ev === 13)
                    {

                    }
                    else {
                        $("#alert-li-password-english").show();
                        booleans[6] = true;
                        checkIsThereAlert();
                        return false;
                    }
                })

            //#endregion

            //#region Paste Event
                
                $("#password").on("paste", function () {
                    var evp;
                    setTimeout(function () {
                        var datamobile = $("#password").val();
                        for (var i = 0; i < datamobile.length; i++) {
                            evp = datamobile.charCodeAt(i);
                            if (32 <= evp && evp <= 126) {
                            }
                            else {
                                $("#password").val('');
                                $("#password").addClass('fieldEmpty');
                                $(".input-password-login").addClass("fieldEmpty");
                                $("#alert-li-password-english").show();
                                booleans[6] = true;
                                return false;
                            }
                        }
                    }, 10)
                    setTimeout(function () {
                        if ($("#password").val() !== '') {
                            $("#alert-li-password-english").hide();
                            booleans[6] = false;
                            $("#password").removeClass('fieldEmpty');
                            $(".input-password-login").removeClass("fieldEmpty");
                        }
                    }, 20)
                    checkIsThereAlert();
                })

            //#endregion

            //#region Focusin Event
                var firstPassFocusIn = true;
                $("#password").click(function () {
                    if (firstPassFocusIn)
                    {
                        $(this).val('');
                        firstPassFocusIn = false;
                    }
                })
            //#endregion

    //#endregion

    //#region ButtonAlerts
        // $("#login-form").on('submit', function() {
            // if (!RegisteredMobileNumber || $("#password").val() === '')
        checkFormValidation = function () {
            var checks = true;

            //Mobile
            var datamob = $("#mobilenumber").val();
            var charcheck;
            var mobileDigitsCheck = true;
            for (var i=0; i<datamob.length; i++)
            {
                charcheck = datamob.charCodeAt(i);
                if (48 <= charcheck && charcheck <= 57) {
                }
                else if (charcheck === 13)
                {
                }
                else {
                    mobileDigitsCheck = false;
                    break;
                }
            }
            if ($("#mobilenumber").val().length == 0)
            {
                $("#alert-li-mobile-empty").show();
                booleans[0] = true;
                $("#mobilenumber").addClass("fieldEmpty");
                $(".input-mob-login").addClass("fieldEmpty");
                checks = false;
            }
            else if (!mobileDigitsCheck) {
                $("#alert-li-mobile-digits").show();
                booleans[1] = true;
                $("#mobilenumber").addClass("fieldEmpty");
                $(".input-mob-login").addClass("fieldEmpty");
                checks = false;
            }
            else if ($("#mobilenumber").val().length != 11)
            {
                $("#alert-li-mobile-length").show();
                booleans[2] = true;
                $("#mobilenumber").addClass("fieldEmpty");
                $(".input-mob-login").addClass("fieldEmpty");
                checks = false;
            }
            else if ($("#mobilenumber").val()[0] !== '0' || $("#mobilenumber").val()[1] !== '9')
            {
                $("#alert-li-mobile-valid").show();
                booleans[3] = true;
                $("#mobilenumber").addClass("fieldEmpty");
                $(".input-mob-login").addClass("fieldEmpty");
                checks = false;
            }
            
            //Password
            var datapass = $("#password").val();
            var charcheckpass;
            var passwordEnglishCheck = true;
            for (var i=0; i<datapass.length; i++)
            {
                charcheckpass = datapass.charCodeAt(i);
                if (32 <= charcheckpass && charcheckpass <= 126) {
                }
                else {
                    passwordEnglishCheck = false;
                    break;
                }
            }
            if ($("#password").val().length == 0) {
                $("#alert-li-password-empty").show();
                booleans[5] = true;
                $("#password").addClass("fieldEmpty");
                $(".input-password-login").addClass("fieldEmpty");
                checks = false;
            }
            else if (!passwordEnglishCheck) {
                $("#alert-li-password-english").show();
                booleans[6] = true;
                $("#password").addClass("fieldEmpty");
                $(".input-password-login").addClass("fieldEmpty");
                checks = false;
            }
            checkIsThereAlert();
            return checks;
        }
        // )
    //#endregion

//#endregion