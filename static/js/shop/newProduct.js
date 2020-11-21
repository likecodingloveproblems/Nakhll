//Img
$("#alert-div-inputproduct-img-empty").hide();

//Title
$("#alert-div-inputproduct-title-empty").hide();
$("#alert-div-inputproduct-title-minlength").hide();
$("#alert-div-inputproduct-title-maxlength").hide();
// $("#alert-div-inputproduct-title-valid-chars").hide();
// $("#alert-div-inputproduct-title-persian").hide();

//Slug
$("#alert-div-inputproduct-slug-empty").hide();
$("#alert-div-inputproduct-slug-english").hide();
$("#alert-div-inputproduct-slug-dup").hide();

//Shop
$("#alert-div-inputproduct-shop-empty").hide();

//About
// $("#alert-div-inputproduct-about-empty").hide();
// $("#alert-div-inputproduct-about-valid-chars").hide();
// $("#alert-div-inputproduct-about-persian").hide();

//Category
$("#alert-div-inputproduct-category-empty").hide();
$("#alert-div-inputproduct-category-count-limit").hide();

//Submarket
$("#alert-div-inputproduct-submarket-empty").hide();

//Introduction
$("#alert-div-inputproduct-bio-empty").hide();
// $("#alert-div-inputproduct-intro-valid-chars").hide();
// $("#alert-div-inputproduct-introduction-persian").hide();
$("#alert-div-inputproduct-bio-maxlength").hide();


//Story
// $("#alert-div-inputproduct-story-valid-chars").hide();
// $("#alert-div-inputproduct-story-persian").hide();

//Real & Sell Price
$("#alert-div-inputproduct-price-digits").hide();
$("#alert-div-inputproduct-price-comparison").hide();

//Sell Price
$("#alert-div-inputproduct-sell-price-empty").hide();
$("#alert-div-inputproduct-sell-price-minlength").hide();

//Off
$("#alert-div-inputproduct-off-empty").hide();
$("#alert-div-inputproduct-off-length").hide();

// // Real Price
// $("#alert-div-inputproduct-real-price-minlength").hide();

//Pure Weight
$("#alert-div-inputproduct-pure-weight-empty").hide();

//Packing Weight
$("#alert-div-inputproduct-packing-weight-empty").hide();

$("#alert-div-inputproduct-weight-digits").hide();
$("#alert-div-inputproduct-weight-comparison").hide();

//Product Dimension

//Product Length
$("#alert-div-inputproduct-length-dimension-empty").hide();

//Product Width
$("#alert-div-inputproduct-width-dimension-empty").hide();

//Product Height
$("#alert-div-inputproduct-height-dimension-empty").hide();


$("#alert-div-inputproduct-dimension-digits").hide();

//Product Send Area
$("#alert-div-inputproduct-send-area-limit").hide();

//Product Send Area Exception
$("#alert-div-inputproduct-send-area-exception-limit").hide();

//Product Available Count
$("#alert-div-inputproduct-available-count-empty").hide();
$("#alert-div-inputproduct-available-count-digits").hide();
$("#alert-div-inputproduct-available-count-zero-value").hide();

//System Error
$("#alert-div-system-error").hide();


//Img
$("#alert-div-inputproduct-img-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
	'<i class="far fa-exclamation-circle"></i>' +
	'<p>یک عکس برای محصول باید انتخاب شود.</p>' +
	'</div></div>');

//Title
$("#alert-div-inputproduct-title-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
	'<i class="far fa-exclamation-circle"></i>' +
	'<p>وارد کردن عنوان محصول الزامی است.</p>' +
    '</div></div>');
    
$("#alert-div-inputproduct-title-minlength").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
	'<i class="far fa-exclamation-circle"></i>' +
	'<p>عنوان محصول باید از 2 کارکتر بیشتر باشد.</p>' +
	'</div></div>');

$("#alert-div-inputproduct-title-maxlength").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>عنوان محصول نمیتواند بیشتر از 170 کاراکتر باشد.</p>' +
    '</div></div>');

// $("#alert-div-inputproduct-title-valid-chars").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
//     '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
//     '<i class="far fa-exclamation-circle"></i>' +
//     '<p>در عنوان محصول از کاراکترهای غیر مجاز استفاده شده است.</p>' +
//     '</div></div>');
// $("#alert-div-inputproduct-title-persian").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
// 	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
// 	'<i class="far fa-exclamation-circle"></i>' +
// 	'<p>برای عنوان فقط از حروف فارسی، خط تیره ("-")، پرانتز و اعداد میتوانید استفاده کنید.</p>' +
// 	'</div></div>');

//Slug
$("#alert-div-inputproduct-slug-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
	'<i class="far fa-exclamation-circle"></i>' +
	'<p>وارد کردن شناسه محصول الزامی است.</p>' +
	'</div></div>');

$("#alert-div-inputproduct-slug-english").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
	'<i class="far fa-exclamation-circle"></i>' +
	'<p>شناسه محصول باید شامل حروف انگلیسی کوچک،، اعداد، خط تیره ("-") و بدون فاصله باشد.</p>' +
	'</div></div>');

$("#alert-div-inputproduct-slug-dup").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
	'<i class="far fa-exclamation-circle"></i>' +
	'<p>این شناسه محصول تکراری میباشد.</p>' +
    '</div></div>');
    
//Shop
$("#alert-div-inputproduct-shop-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>حجره محصول خود را باید مشخص کنید.</p>' +
    '</div></div>');

//About
// $("#alert-div-inputproduct-about-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
//     '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
//     '<i class="far fa-exclamation-circle"></i>' +
//     '<p>درباره محصول نمیتواند خالی باشد.</p>' +
//     '</div></div>');
    
// $("#alert-div-inputproduct-about-valid-chars").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
//     '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
//     '<i class="far fa-exclamation-circle"></i>' +
//     '<p>در درباره محصول از کاراکترهای غیر مجاز استفاده شده است.</p>' +
//     '</div></div>');


// $("#alert-div-inputproduct-about-persian").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
// 	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
// 	'<i class="far fa-exclamation-circle"></i>' +
// 	'<p>درباره محصول باید فارسی باشد</p>' +
// 	'</div></div>');

//Category
$("#alert-div-inputproduct-category-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>دسته بندی محصول خود را باید مشخص کنید.</p>' +
    '</div></div>');

$("#alert-div-inputproduct-category-count-limit").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>محصول نمیتواند در بیش از 10 دسته بندی قرار بگیرد.</p>' +
    '</div></div>');

//ُSubmarket
$("#alert-div-inputproduct-submarket-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>راسته محصول خود را باید مشخص کنید.</p>' +
    '</div></div>');

//Introduction
$("#alert-div-inputproduct-bio-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>معرفی محصول نمیتواند خالی باشد.</p>' +
    '</div></div>');
// $("#alert-div-inputproduct-intro-valid-chars").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
//     '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
//     '<i class="far fa-exclamation-circle"></i>' +
//     '<p>در معرفی محصول از کاراکترهای غیر مجاز استفاده شده است.</p>' +
//     '</div></div>');
$("#alert-div-inputproduct-bio-maxlength").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>معرفی محصول نمیتواند بیش از 200 کاراکتر باشد.</p>' +
    '</div></div>');

//Story
// $("#alert-div-inputproduct-story-valid-chars").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
//     '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
//     '<i class="far fa-exclamation-circle"></i>' +
//     '<p>در داستان محصول از کاراکترهای غیر مجاز استفاده شده است.</p>' +
//     '</div></div>');

// //Real & Sell Price
$("#alert-div-inputproduct-price-digits").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>برای قیمت فقط از اعداد باید استفاده کنید.</p>' +
    '</div></div>');

// $("#alert-div-inputproduct-price-comparison").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
//     '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
//     '<i class="far fa-exclamation-circle"></i>' +
//     '<p>قیمت فروش باید کمتر از قیمت واقعی باشد.</p>' +
//     '</div></div>');

//Sell Price
$("#alert-div-inputproduct-sell-price-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>مشخص کردن قیمت فروش محصول الزامی است.</p>' +
    '</div></div>');

$("#alert-div-inputproduct-sell-price-minlength").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>قیمت فروش باید از 2 رقم بیشتر باشد.</p>' +
    '</div></div>');

// //Real Price
// $("#alert-div-inputproduct-real-price-minlength").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
//     '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
//     '<i class="far fa-exclamation-circle"></i>' +
//     '<p>قیمت واقعی باید از 5 رقم بیشتر باشد.</p>' +
//     '</div></div>');

//Off
$("#alert-div-inputproduct-off-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>تخفیف روی محصول اعمال شده اما مقداری برای آن مقرر نگردیده است. در صورتی که محصول شامل تخفیف نمیشود گزینه "حذف تخفیف" را انتخاب کنید.</p>' +
    '</div></div>');

$("#alert-div-inputproduct-off-length").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>میزان تخفیف بایستی از 1 تومان به بالا باشد.</p>' +
    '</div></div>')

//Pure Weight
$("#alert-div-inputproduct-pure-weight-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>مشخص کردن وزن خالص محصول الزامی است.</p>' +
    '</div></div>');

//Packing Weight
$("#alert-div-inputproduct-packing-weight-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>مشخص کردن وزن بسته بندی محصول الزامی است.</p>' +
    '</div></div>');


$("#alert-div-inputproduct-weight-digits").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>فقط از اعداد برای مشخص کردن وزن استفاده نمائید.</p>' +
    '</div></div>');

$("#alert-div-inputproduct-weight-comparison").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>وزن خالص محصول باید کمتر از وزن محصول با بسته بندی باشد.</p>' +
    '</div></div>');


//Product Dimension
//Product Length
$("#alert-div-inputproduct-length-dimension-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>مشخص کردن طول بسته بندی محصول الزامی است.</p>' +
    '</div></div>');
//Product Width
$("#alert-div-inputproduct-width-dimension-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>مشخص کردن عرض بسته بندی محصول الزامی است.</p>' +
    '</div></div>');
//Product Height
$("#alert-div-inputproduct-height-dimension-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>مشخص کردن ارتفاع بسته بندی محصول الزامی است.</p>' +
    '</div></div>');


$("#alert-div-inputproduct-dimension-digits").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>فقط از اعداد برای مشخص کردن ابعاد استفاده نمائید.</p>' +
    '</div></div>');

//Product Send Area
$("#alert-div-inputproduct-send-area-limit").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>تعداد موارد منتخب در "انتخاب محدوده ارسال محصول" بیش از حد مجاز است.</p>' +
    '</div></div>');

//Product Send Area Exception
$("#alert-div-inputproduct-send-area-exception-limit").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>تعداد موارد منتخب در "انتخاب استثناء محدوده ارسال محصول" بیش از حد مجاز است.</p>' +
    '</div></div>');

//Product Available Count
$("#alert-div-inputproduct-available-count-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>"تعداد موجودی" نمیتواند خالی باشد.</p>' +
    '</div></div>');

$("#alert-div-inputproduct-available-count-digits").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>فقط از اعداد برای وارد کردن موجودی استفاده نمائید.</p>' +
    '</div></div>');

$("#alert-div-inputproduct-available-count-zero-value").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>تعداد موجودی نمیتواند صفر باشد. در صورتی که محصول مورد نظر موجود نمیباشد "وضعیت محصول" را "موجود نیست" انتخاب نمائید.</p>' +
    '</div></div>');

//System Error
$("#alert-div-system-error").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>خطا! صفحه را رفرش کرده مجددا سعی کنید.</p>' +
    '</div></div>');

    //Img Event

    //Title Event
    $("#inputprod_title").on("focusout", function () {
        var inputshopTitleLength = $(this).val().length;
        if ($(this).val() === '') {
            $(this).addClass("inputshopempty");
            $("#alert-div-inputproduct-title-empty").show();
        }
        else if (inputshopTitleLength < 2) {
            $(this).addClass("inputshopempty");
            $("#alert-div-inputproduct-title-minlength").show();
            $(this).prop("minLength", 2);
            $("html, body").animate({ 
                scrollTop: 220 
            }, "slow");
        }
        else {
            $("#alert-div-inputproduct-title-minlength").hide();
            $("#alert-div-inputproduct-title-empty").hide();
        }
    })
    $("#inputprod_title").on("input", function () {
        var InpShopTitleLength = $(this).val().length;
        if ($(this).val() !== '') {
            $(this).removeClass("inputshopempty");
            $("#alert-div-inputproduct-title-empty").hide();
        }
        if (InpShopTitleLength >= 2) {
            $(this).removeClass("inputshopempty");
            $("#alert-div-inputproduct-title-minlength").hide();
        }
    })
    $("#inputprod_title").on("keypress paste", function () {
        var textLength = $(this).val().length;
        if (textLength >= 170) {
            $(this).val($(this).val().substr(0, 170));
            $(this).prop("maxlength", 170);
        }
    })

    // Slug Events
		$("#inputslugProd").on("focusout", function () {
			if ($(this).val() === '') {
				$(this).addClass("inputshopempty");
				$("#alert-div-inputproduct-slug-empty").show();
			}
			else {
                $("#alert-div-inputproduct-slug-empty").hide();
            }
		})
		$("#inputslugProd").on("input", function () {
			if ($(this).val() !== '') {
				$(this).removeClass("inputshopempty");
                $("#alert-div-inputproduct-slug-empty").hide();

                var data = $("#inputslugProd").val();
                var ews = data.charCodeAt(data.length-1);
                if (97 <= ews && ews <= 122 || 48 <= ews && ews <= 57) {
                    $("#alert-div-inputproduct-slug-english").hide();
                    $("#inputslugProd").removeClass("inputshopempty");
                }
                else if (ews === 45) {
                    $("#alert-div-inputproduct-slug-english").hide();
                    $("#inputslugProd").removeClass("inputshopempty");
                }
                else if (ews === 13) {

                }
                else {
                    $("#inputslugProd").val($("#inputslugProd").val().substr(0, data.length-1));
                    $("#alert-div-inputproduct-slug-english").show();
                    $("#inputslugProd").addClass("inputshopempty");
                    $("html, body").animate({ 
                        scrollTop: 220 
                    }, "slow");
                }
            }
		})
		$("#inputslugProd").on("keypress", function(event) {
			var es = event.which;
			if (97 <= es && es <= 122 || 48 <= es && es <= 57)
			{
				$("#alert-div-inputproduct-slug-english").hide();
				return true;
			}
			else if (es === 45)
			{
				$("#alert-div-inputproduct-slug-english").hide();
				return true;
            }
            else if (es === 13) {

            }
			else {
				$(this).addClass("inputshopempty");
				$("#alert-div-inputproduct-slug-english").show();
				$("html, body").animate({ 
					scrollTop: 220 
				}, "slow");
				return false;
			}
		})
		$("#inputslugProd").on("paste drop", function () {
			setTimeout(function(){
				var data = $("#inputslugProd").val();
				for(var i=0; i<data.length; i++)
				{
					var ews = data.charCodeAt(i);
					if (97 <= ews && ews <= 122 || 48 <= ews && ews <= 57) {
						
					}
					else if (ews === 45) {
						
                    }
					else {
						$("#inputslugProd").val('');
						$("#alert-div-inputproduct-slug-english").show();
						$("#inputslugProd").addClass("inputshopempty");
						$("html, body").animate({ 
							scrollTop: 220 
						}, "slow");
						return false;
					}
				}
		}, 10)
			setTimeout(function () {
				if($("#inputslugProd").val() !== '')
				{
					$("#alert-div-inputproduct-slug-empty").hide();
					$("#alert-div-inputproduct-slug-english").hide();
					$("#inputslugProd").removeClass("inputshopempty");	
				}
			}, 20)
        })
        
        //Shop
        

        //About
        // $("#inputProdDes").on("focusout", function () {
        //     if ($(this).val() === '') {
        //         $(this).addClass("inputshopempty");
        //         $("#alert-div-inputproduct-about-empty").show();
        //     }
        //     else {
        //         $("#alert-div-inputproduct-about-empty").hide();
        //     }
        // })
        // $("#inputProdDes").on("input", function () {
        //     if ($(this).val() !== '') {
        //         $(this).removeClass("inputshopempty");
        //         $("#alert-div-inputproduct-about-empty").hide();
        //     }
        // })
        // $("#inputProdDes").on("keypress paste", function () {
        //     var textLength = $(this).val().length;
        //     if (textLength >= 200) {
        //         $(this).val($(this).val().substr(0, 200));
        //         $(this).prop("maxlength", 200);
        //     }
        // })
                
        //Category
        
        //Submarket
                        
        // Introduction
        $("#inputProdBio").on("focusout", function () {
            if ($(this).val() === '') {
                $(this).addClass("inputshopempty");
                $("#alert-div-inputproduct-bio-empty").show();
            }
            else {
                $("#alert-div-inputproduct-bio-empty").hide();
            }
        })
        $("#inputProdBio").on("keypress paste", function () {
            var textLength = $(this).val().length;
            if (textLength >= 200) {
                $(this).val($(this).val().substr(0, 200));
                $(this).prop("maxlength", 200);
            }
        })
        $("#inputProdBio").on("input", function () {
            if ($(this).val() !== '') {
                $(this).removeClass("inputshopempty");
                $("#alert-div-inputproduct-bio-maxlength").hide();
            }
        })

        if ($("#inputprod_offamount").val().length == 0) {
            $(".offamount-formgroup").hide();
            $(".remove-off-formgroup").hide();
        }
        else {
            $(".off-question-form-group").hide();
        }

        var offornot = false;

        $("#off-yes-clk").click(function () {
            $(".off-question-form-group").hide();
            $(".offamount-formgroup").show();
            $(".remove-off-formgroup").show();
            offornot = true;
        })

        $("#remove-off").click(function () {
            $(".off-question-form-group").show();
            $("#inputprod_offamount").val('');
            $("#offamount-toman").html('');
            $(".offamount-formgroup").hide();
            $(".remove-off-formgroup").hide();
            $("#alert-div-inputproduct-off-empty").hide();
            $("#alert-div-inputproduct-off-length").hide();
            $("#inputprod_offamount").removeClass("inputshopempty");
            offornot = false;
        })



        //Real & Sell Price


        $(".inputprod_sellprice").on("keypress", function (event) {
            var ew = event.which;
            if (48 <= ew && ew <= 57) {
                $("#alert-div-inputproduct-price-digits").hide()
                return true;
            }
            else if (ew === 13) {

            }
            else {
                $("#alert-div-inputproduct-price-digits").show();
                $(this).addClass("inputshopempty");
                $("html, body").animate({ 
                    scrollTop: 220 
                }, "slow");
                return false;
            }
        })

        $("#inputprod_offamount").on('focusout', function() {
            if($(this).val().length == 0) {
                $("#alert-div-inputproduct-off-length").hide();
                $("#alert-div-inputproduct-off-empty").show();
                $(this).addClass("inputshopempty");
            }
            else if ($(this).val().length < 2) {
                $("#alert-div-inputproduct-off-empty").hide();
                $("#alert-div-inputproduct-off-length").show();
                $(this).addClass("inputshopempty");
                $("html, body").animate({ 
                    scrollTop: 220 
                }, "slow");
            }
            else {
                $("#alert-div-inputproduct-off-length").hide();
                $("#alert-div-inputproduct-off-empty").hide();
                $(this).removeClass("inputshopempty");
            }
        })

        // $(".inputprod_realprice").on("keypress", function (event) {
        //     var ew = event.which;
        //     if (48 <= ew && ew <= 57) {
        //         $("#alert-div-inputproduct-price-digits").hide()
        //         return true;
        //     }
        //     else if (ew === 13) {
        
        //     }
        //     else {
        //         $("#alert-div-inputproduct-price-digits").show();
        //         $(this).addClass("inputshopempty");
        //         $("html, body").animate({ 
        //             scrollTop: 220 
        //         }, "slow");
        //         return false;
        //     }
        // })
        $(".inputprod_sellprice").on("paste drop", function () {
            setTimeout(function(){
                var textLength = $(".inputprod_sellprice").val().length;
                if (textLength >= 15) {
                    $(".inputprod_sellprice").val($(".inputprod_sellprice").val().substr(0, 15));
                    $(".inputprod_sellprice").prop("maxlength", 15);
                }
                var data = $(".inputprod_sellprice").val();
                for(var i=0; i<data.length; i++)
                {
                    var ewt = data.charCodeAt(i);
                    if (48 <= ewt && ewt <= 57) {
                        
                    }
                    else {
                        $(".inputprod_sellprice").val('');
                        $("#alert-div-inputproduct-price-digits").show();
                        $(".inputprod_sellprice").addClass("inputshopempty");	
                        $("html, body").animate({ 
                            scrollTop: 220 
                        }, "slow");
                        return false;
                    }
                }
        }, 10)
            setTimeout(function () {
                if($(".inputprod_sellprice").val() !== '')
                {
                    $("#alert-div-inputproduct-sell-price-empty").hide();
                    $("#alert-div-inputproduct-price-digits").hide();
                    $(".inputprod_sellprice").removeClass("inputshopempty");
                }
            }, 20)
        })
        // $(".inputprod_realprice").on("paste drop", function () {
        //     setTimeout(function(){
        //         var textLength = $(".inputprod_realprice").val().length;
        //         if (textLength >= 15) {
        //             $(".inputprod_realprice").val($(".inputprod_realprice").val().substr(0, 15));
        //             $(".inputprod_realprice").prop("maxlength", 15);
        //         }
        //         var data = $(".inputprod_realprice").val();
        //         for(var i=0; i<data.length; i++)
        //         {
        //             var ewt = data.charCodeAt(i);
        //             if (48 <= ewt && ewt <= 57) {
                        
        //             }
        //             else {
        //                 $(".inputprod_realprice").val('');
        //                 $("#alert-div-inputproduct-price-digits").show();
        //                 $(".inputprod_realprice").addClass("inputshopempty");	
        //                 $("html, body").animate({ 
        //                     scrollTop: 220 
        //                 }, "slow");
        //                 return false;
        //             }
        //         }
        // }, 10)
        //     setTimeout(function () {
        //         if($(".inputprod_realprice").val() !== '')
        //         {
        //             $("#alert-div-inputproduct-price-digits").hide();
        //             $(".inputprod_realprice").removeClass("inputshopempty");
        //         }
        //     }, 20)
        // })
        // var validPrices = false;
        // $(".inputprod_sellprice").on('focusout', function() {
        //     if($(this).val() === '')
        //     {
        //         $("#alert-div-inputproduct-sell-price-empty").show();
        //         $(this).addClass("inputshopempty");
        //     }
        //     else if ($(this).val().length < 5)
        //     {
        //         $(this).addClass("inputshopempty");
        //         $("#alert-div-inputproduct-sell-price-minlength").show();
        //         $("#alert-div-inputproduct-price-digits").hide();
        //         $("html, body").animate({ 
        //             scrollTop: 220 
        //         }, "slow");
        //     }
        //     else if ($(".inputprod_realprice").val() !== '' && (parseInt($(".inputprod_realprice").val()) <= parseInt($(".inputprod_sellprice").val()))) {
        //         $(".inputprod_realprice").addClass("inputshopempty");
        //         $("#alert-div-inputproduct-sell-price-minlength").hide();
        //         $("#alert-div-inputproduct-price-digits").hide();
        //         $("#alert-div-inputproduct-price-comparison").show();
        //         $("html, body").animate({ 
        //             scrollTop: 220 
        //         }, "slow");
        //     }
        //     else {
        //         $(this).removeClass("inputshopempty");
        //         $(".inputprod_realprice").removeClass("inputshopempty");
        //         $("#alert-div-inputproduct-sell-price-minlength").hide();
        //         $("#alert-div-inputproduct-sell-price-empty").hide();
        //         $("#alert-div-inputproduct-price-digits").hide();
        //         $("#alert-div-inputproduct-price-comparison").hide();
        //         validPrices = true;
        //     }
        // })
        // $(".inputprod_realprice").on('focusout', function() {
        //     if($(this).val() === '') {
        //         $(this).removeClass("inputshopempty");
        //         $("#alert-div-inputproduct-real-price-minlength").hide();
        //         $("#alert-div-inputproduct-price-comparison").hide();
        //     }
        //     else if ($(this).val().length < 5)
        //     {
        //         $(this).addClass("inputshopempty");
        //         $("#alert-div-inputproduct-real-price-minlength").show();
        //         $("#alert-div-inputproduct-price-comparison").hide();
        //         $("#alert-div-inputproduct-price-digits").hide();
        //         $("html, body").animate({ 
        //             scrollTop: 220 
        //         }, "slow");
        //     }
        //     else if ($(".inputprod_sellprice").val() !== '' && (parseInt($(".inputprod_realprice").val()) <= parseInt($(".inputprod_sellprice").val()))) {
        //         $(this).addClass("inputshopempty");
        //         $("#alert-div-inputproduct-real-price-minlength").hide();
        //         $("#alert-div-inputproduct-price-digits").hide();
        //         $("#alert-div-inputproduct-price-comparison").show();
        //         $("html, body").animate({ 
        //             scrollTop: 220 
        //         }, "slow");
        //     }
        //     else {
        //         $(this).removeClass("inputshopempty");
        //         $("#alert-div-inputproduct-real-price-minlength").hide();
        //         $("#alert-div-inputproduct-price-digits").hide();
        //         $("#alert-div-inputproduct-price-comparison").hide();
        //         validPrices = true;
        //     }
        // })
        $(".inputprod_sellprice").on("keypress", function () {
            var textLength = $(this).val().length;
            if (textLength >= 15) {
                $(this).val($(this).val().substr(0, 15));
                $(this).prop("maxlength", 15);
                return false;
            }
        })
        // $(".inputprod_realprice").on("keypress", function () {
        //     var textLength = $(this).val().length;
        //     if (textLength >= 15) {
        //         $(this).val($(this).val().substr(0, 15));
        //         $(this).prop("maxlength", 15);
        //         return false;
        //     }
        // })
        $(".inputprod_sellprice").on("input", function () {
            // validPrices = false;
            var InpShopSellPriceLength = $(this).val().length;
            if ($(this).val() !== '') {
                $(this).removeClass("inputshopempty");
                $("#alert-div-inputproduct-sell-price-empty").hide();

                var data = $(".inputprod_sellprice").val();
                var ew = data.charCodeAt(data.length-1);
                if (48 <= ew && ew <= 57) {
                    $("#alert-div-inputproduct-price-digits").hide();
                    $(".inputprod_sellprice").removeClass("inputshopempty");
                }
                else if (ew === 13) {
                
                }
                else {
                    $(".inputprod_sellprice").val($(".inputprod_sellprice").val().substr(0, data.length-1));
                    $("#alert-div-inputproduct-price-digits").show();
                    $(".inputprod_sellprice").addClass("inputshopempty");
                    $("html, body").animate({ 
                        scrollTop: 220 
                    }, "slow");
                }
            }
            if (InpShopSellPriceLength >= 2) {
                $(this).removeClass("inputshopempty");
                $("#alert-div-inputproduct-sell-price-minlength").hide();
            }
        })
        // $(".inputprod_realprice").on("input", function () {
        //     // validPrices = false;
        //     var InpShopRealLength = $(this).val().length;
        //     if ($(this).val() !== '') {
        //         $(this).removeClass("inputshopempty");
                
        //         var data = $(".inputprod_realprice").val();
        //         var ew = data.charCodeAt(data.length-1);
        //         if (48 <= ew && ew <= 57) {
        //             $("#alert-div-inputproduct-price-digits").hide();
        //             $(".inputprod_realprice").removeClass("inputshopempty");
        //         }
        //         else if (ew === 13) {
                
        //         }
        //         else {
        //             $(".inputprod_realprice").val($(".inputprod_realprice").val().substr(0, data.length-1));
        //             $("#alert-div-inputproduct-price-digits").show();
        //             $(".inputprod_realprice").addClass("inputshopempty");
        //             $("html, body").animate({ 
        //                 scrollTop: 220 
        //             }, "slow");
        //         }
        //     }
        //     if (InpShopRealLength >= 5) {
        //         $(this).removeClass("inputshopempty");
        //         $("#alert-div-inputproduct-real-price-minlength").hide();
        //     }
        // })

        //Product Weight
        var validWeight = false;
        $("#input_netweight").on('focusout', function () {
            if ($(this).val() === '') {
                $(this).addClass("inputshopempty");
                $("#alert-div-inputproduct-pure-weight-empty").show();
                $("#alert-div-inputproduct-weight-comparison").hide();
            }
            else if ($("#input_packingweight").val() !== '' && (parseInt($("#input_netweight").val()) >= parseInt($("#input_packingweight").val()))) {
                $("#alert-div-inputproduct-weight-comparison").show();
                $(this).addClass("inputshopempty");
                $("html, body").animate({ 
                    scrollTop: 220 
                }, "slow");
            }
            else {
                $(this).removeClass("inputshopempty");
                $("#alert-div-inputproduct-pure-weight-empty").hide();
                $("#alert-div-inputproduct-weight-digits").hide();
                $("#alert-div-inputproduct-weight-comparison").hide();
                validWeight = true;
            }

        })
        $("#input_netweight").on("keypress", function (event) {
            var ew = event.which;
            if (48 <= ew && ew <= 57) {
                $("#alert-div-inputproduct-weight-digits").hide()
                return true;
            }
            else if (ew === 13) {
        
            }
            else {
                $("#alert-div-inputproduct-weight-digits").show();
                $(this).addClass("inputshopempty");
                $("html, body").animate({ 
                    scrollTop: 220 
                }, "slow");
                return false;
            }
        })
        $("#input_netweight").on("paste", function () {
            setTimeout(function(){
                var textLength = $("#input_netweight").val().length;
                if (textLength >= 6) {
                    $("#input_netweight").val($("#input_netweight").val().substr(0, 6));
                    $("#input_netweight").prop("maxlength", 6);
                    return false;
                }
                var data = $("#input_netweight").val();
                for(var i=0; i<data.length; i++)
                {
                    var ewt = data.charCodeAt(i);
                    if (48 <= ewt && ewt <= 57) {
                        
                    }
                    else {
                        $("#input_netweight").val('');
                        $("#alert-div-inputproduct-weight-digits").show();
                        $("#input_netweight").addClass("inputshopempty");	
                        $("html, body").animate({ 
                            scrollTop: 220 
                        }, "slow");
                        return false;
                    }
                }
        }, 10)
            setTimeout(function () {
                if($("#input_netweight").val() !== '')
                {
                    $("#alert-div-inputproduct-pure-weight-empty").hide();
                    $("#alert-div-inputproduct-weight-digits").hide();
                    $("#input_netweight").removeClass("inputshopempty");
                }
            }, 20)
        })
        $("#input_netweight").on('focusout', function () {
            if ($(this).val() === '') {
                $(this).addClass("inputshopempty");
                $("#alert-div-inputproduct-pure-weight-empty").show();
            }
            else {
                $(this).removeClass("inputshopempty");
                $("#alert-div-inputproduct-pure-weight-empty").hide();
                $("#alert-div-inputproduct-weight-digits").hide();
            }

        })
        $("#input_netweight").on("keypress", function () {
            var textLength = $(this).val().length;
            if (textLength >= 6) {
                $(this).val($(this).val().substr(0, 6));
                $(this).prop("maxlength", 6);
                return false;
            }
        })
        $("#input_netweight").on("input", function () {
            validWeight = false;
            if ($(this).val() !== '') {
                $(this).removeClass("inputshopempty");
                $("#alert-div-inputproduct-pure-weight-empty").hide();
                
                var data = $("#input_netweight").val();
                var ew = data.charCodeAt(data.length-1);
                if (48 <= ew && ew <= 57) {
                    $("#alert-div-inputproduct-weight-digits").hide();
                    $("#input_netweight").removeClass("inputshopempty");
                }
                else if (ew === 13) {
                
                }
                else {
                    $("#input_netweight").val($("#input_netweight").val().substr(0, data.length-1));
                    $("#alert-div-inputproduct-weight-digits").show();
                    $("#input_netweight").addClass("inputshopempty");
                    $("html, body").animate({ 
                        scrollTop: 220 
                    }, "slow");
                }
            }
        })

        //Packing Weight
        $("#input_packingweight").on('focusout', function () {
            if ($(this).val() === '') {
                $(this).addClass("inputshopempty");
                $("#alert-div-inputproduct-packing-weight-empty").show();
                $("#alert-div-inputproduct-weight-comparison").hide();
            }
            else if ($("#input_netweight").val() !== '' && (parseInt($("#input_netweight").val()) >= parseInt($("#input_packingweight").val()))) {
                $("#alert-div-inputproduct-weight-comparison").show();
                $(this).addClass("inputshopempty");
                $("html, body").animate({ 
                    scrollTop: 220 
                }, "slow");
            }
            else {
                $(this).removeClass("inputshopempty");
                $("#alert-div-inputproduct-packing-weight-empty").hide();
                $("#alert-div-inputproduct-weight-digits").hide();
                $("#alert-div-inputproduct-weight-comparison").hide();
                validWeight = true;
            }

        })
        $("#input_packingweight").on("keypress", function (event) {
            var ew = event.which;
            if (48 <= ew && ew <= 57) {
                $("#alert-div-inputproduct-weight-digits").hide()
                return true;
            }
            else if (ew === 13) {
        
            }
            else {
                $("#alert-div-inputproduct-weight-digits").show();
                $(this).addClass("inputshopempty");
                $("html, body").animate({ 
                    scrollTop: 220 
                }, "slow");
                return false;
            }
        })
        $("#input_packingweight").on("paste", function () {
            setTimeout(function(){
                var textLength = $("#input_packingweight").val().length;
                if (textLength >= 6) {
                    $("#input_packingweight").val($("#input_packingweight").val().substr(0, 6));
                    $("#input_packingweight").prop("maxlength", 6);
                }
                var data = $("#input_packingweight").val();
                for(var i=0; i<data.length; i++)
                {
                    var ewt = data.charCodeAt(i);
                    if (48 <= ewt && ewt <= 57) {
                        
                    }
                    else {
                        $("#input_packingweight").val('');
                        $("#alert-div-inputproduct-weight-digits").show();
                        $("#input_packingweight").addClass("inputshopempty");	
                        $("html, body").animate({ 
                            scrollTop: 220 
                        }, "slow");
                        return false;
                    }
                }
        }, 10)
            setTimeout(function () {
                if($("#input_packingweight").val() !== '')
                {
                    $("#alert-div-inputproduct-packing-weight-empty").hide();
                    $("#alert-div-inputproduct-weight-digits").hide();
                    $("#input_packingweight").removeClass("inputshopempty");
                }
            }, 20)
        })
        $("#input_packingweight").on("keypress", function () {
            var textLength = $(this).val().length;
            if (textLength >= 6) {
                $(this).val($(this).val().substr(0, 6));
                $(this).prop("maxlength", 6);
                return false;
            }
        })
        $("#input_packingweight").on("input", function () {
            validWeight = false;
            if ($(this).val() !== '') {
                $(this).removeClass("inputshopempty");
                $("#alert-div-inputproduct-packing-weight-empty").hide();

                var data = $("#input_packingweight").val();
                var ew = data.charCodeAt(data.length-1);
                if (48 <= ew && ew <= 57) {
                    $("#alert-div-inputproduct-weight-digits").hide();
                    $("#input_packingweight").removeClass("inputshopempty");
                }
                else {
                    $("#input_packingweight").val($("#input_packingweight").val().substr(0, data.length-1));
                    $("#alert-div-inputproduct-weight-digits").show();
                    $("#input_packingweight").addClass("inputshopempty");
                    $("html, body").animate({ 
                        scrollTop: 220 
                    }, "slow");
                }
            }
        })

        //Product Dimension
        $("#input_lengthwithpackaging").on('focusout', function () {
            if ($(this).val() === '') {
                $(this).addClass("inputshopempty");
                $("#alert-div-inputproduct-length-dimension-empty").show();
            }
            else {
                $(this).removeClass("inputshopempty");
                $("#alert-div-inputproduct-length-dimension-empty").hide();
                $("#alert-div-inputproduct-dimension-digits").hide();
            }

        })
        $("#input_lengthwithpackaging").on("keypress", function (event) {
            var ew = event.which;
            if (48 <= ew && ew <= 57) {
                $("#alert-div-inputproduct-dimension-digits").hide()
                return true;
            }
            else if (ew === 13) {
        
            }
            else {
                $("#alert-div-inputproduct-dimension-digits").show();
                $(this).addClass("inputshopempty");
                $("html, body").animate({ 
                    scrollTop: 220 
                }, "slow");
                return false;
            }
        })
        $("#input_lengthwithpackaging").on("paste", function () {
            setTimeout(function(){
                var textLength = $("#input_lengthwithpackaging").val().length;
                if (textLength >= 4) {
                    $("#input_lengthwithpackaging").val($("#input_lengthwithpackaging").val().substr(0, 4));
                    $("#input_lengthwithpackaging").prop("maxlength", 4);
                }
                var data = $("#input_lengthwithpackaging").val();
                for(var i=0; i<data.length; i++)
                {
                    var ewt = data.charCodeAt(i);
                    if (48 <= ewt && ewt <= 57) {
                        
                    }
                    else {
                        $("#input_lengthwithpackaging").val('');
                        $("#alert-div-inputproduct-dimension-digits").show();
                        $("#input_lengthwithpackaging").addClass("inputshopempty");	
                        $("html, body").animate({ 
                            scrollTop: 220 
                        }, "slow");
                        return false;
                    }
                }
        }, 10)
            setTimeout(function () {
                if($("#input_lengthwithpackaging").val() !== '')
                {
                    $("#alert-div-inputproduct-length-dimension-empty").hide();
                    $("#alert-div-inputproduct-dimension-digits").hide();
                    $("#input_lengthwithpackaging").removeClass("inputshopempty");
                }
            }, 20)
        })
        $("#input_lengthwithpackaging").on("keypress", function () {
            var textLength = $(this).val().length;
            if (textLength >= 4) {
                $(this).val($(this).val().substr(0, 4));
                $(this).prop("maxlength", 4);
                return false;
            }
        })
        $("#input_lengthwithpackaging").on("input", function () {
            if ($(this).val() !== '') {
                $(this).removeClass("inputshopempty");
                $("#alert-div-inputproduct-length-dimension-empty").hide();
                
                var data = $("#input_lengthwithpackaging").val();
                var ew = data.charCodeAt(data.length-1);
                if (48 <= ew && ew <= 57) {
                    $("#alert-div-inputproduct-dimension-digits").hide();
                    $("#input_lengthwithpackaging").removeClass("inputshopempty");
                }
                else if (ew === 13) {
                
                }
                else {
                    $("#input_lengthwithpackaging").val($("#input_lengthwithpackaging").val().substr(0, data.length-1));
                    $("#alert-div-inputproduct-dimension-digits").show();
                    $("#input_lengthwithpackaging").addClass("inputshopempty");
                    $("html, body").animate({ 
                        scrollTop: 220 
                    }, "slow");
                }
            }
        })


        $("#input_widthwithpackaging").on('focusout', function () {
            if ($(this).val() === '') {
                $(this).addClass("inputshopempty");
                $("#alert-div-inputproduct-width-dimension-empty").show();
            }
            else {
                $(this).removeClass("inputshopempty");
                $("#alert-div-inputproduct-width-dimension-empty").hide();
                $("#alert-div-inputproduct-dimension-digits").hide();
            }

        })
        $("#input_widthwithpackaging").on("keypress", function (event) {
            var ew = event.which;
            if (48 <= ew && ew <= 57) {
                $("#alert-div-inputproduct-dimension-digits").hide()
                return true;
            }
            else if (ew === 13) {
        
            }
            else {
                $("#alert-div-inputproduct-dimension-digits").show();
                $(this).addClass("inputshopempty");
                $("html, body").animate({ 
                    scrollTop: 220 
                }, "slow");
                return false;
            }
        })
        $("#input_widthwithpackaging").on("paste", function () {
            setTimeout(function(){
                var textLength = $("#input_widthwithpackaging").val().length;
                if (textLength >= 4) {
                    $("#input_widthwithpackaging").val($("#input_widthwithpackaging").val().substr(0, 4));
                    $("#input_widthwithpackaging").prop("maxlength", 4);
                }
                var data = $("#input_widthwithpackaging").val();
                for(var i=0; i<data.length; i++)
                {
                    var ewt = data.charCodeAt(i);
                    if (48 <= ewt && ewt <= 57) {
                        
                    }
                    else {
                        $("#input_widthwithpackaging").val('');
                        $("#alert-div-inputproduct-dimension-digits").show();
                        $("#input_widthwithpackaging").addClass("inputshopempty");	
                        $("html, body").animate({ 
                            scrollTop: 220 
                        }, "slow");
                        return false;
                    }
                }
        }, 10)
            setTimeout(function () {
                if($("#input_widthwithpackaging").val() !== '')
                {
                    $("#alert-div-inputproduct-width-dimension-empty").hide();
                    $("#alert-div-inputproduct-dimension-digits").hide();
                    $("#input_widthwithpackaging").removeClass("inputshopempty");
                }
            }, 20)
        })
        $("#input_widthwithpackaging").on("keypress", function () {
            var textLength = $(this).val().length;
            if (textLength >= 4) {
                $(this).val($(this).val().substr(0, 4));
                $(this).prop("maxlength", 4);
                return false;
            }
        })
        $("#input_widthwithpackaging").on("input", function () {
            if ($(this).val() !== '') {
                $(this).removeClass("inputshopempty");
                $("#alert-div-inputproduct-width-dimension-empty").hide();
                
                var data = $("#input_widthwithpackaging").val();
                var ew = data.charCodeAt(data.length-1);
                if (48 <= ew && ew <= 57) {
                    $("#alert-div-inputproduct-dimension-digits").hide();
                    $("#input_widthwithpackaging").removeClass("inputshopempty");
                }
                else if (ew === 13) {
                
                }
                else {
                    $("#input_widthwithpackaging").val($("#input_widthwithpackaging").val().substr(0, data.length-1));
                    $("#alert-div-inputproduct-dimension-digits").show();
                    $("#input_widthwithpackaging").addClass("inputshopempty");
                    $("html, body").animate({ 
                        scrollTop: 220 
                    }, "slow");
                }
            }
        })

        
        $("#input_heightwithpackaging").on('focusout', function () {
            if ($(this).val() === '') {
                $(this).addClass("inputshopempty");
                $("#alert-div-inputproduct-height-dimension-empty").show();
            }
            else {
                $(this).removeClass("inputshopempty");
                $("#alert-div-inputproduct-height-dimension-empty").hide();
                $("#alert-div-inputproduct-dimension-digits").hide();
            }

        })
        $("#input_heightwithpackaging").on("keypress", function (event) {
            var ew = event.which;
            if (48 <= ew && ew <= 57) {
                $("#alert-div-inputproduct-dimension-digits").hide()
                return true;
            }
            else if (ew === 13) {
        
            }
            else {
                $("#alert-div-inputproduct-dimension-digits").show();
                $(this).addClass("inputshopempty");
                $("html, body").animate({ 
                    scrollTop: 220 
                }, "slow");
                return false;
            }
        })
        $("#input_heightwithpackaging").on("paste", function () {
            setTimeout(function(){
                var textLength = $("#input_heightwithpackaging").val().length;
                if (textLength >= 4) {
                    $("#input_heightwithpackaging").val($("#input_heightwithpackaging").val().substr(0, 4));
                    $("#input_heightwithpackaging").prop("maxlength", 4);
                }
                var data = $("#input_heightwithpackaging").val();
                for(var i=0; i<data.length; i++)
                {
                    var ewt = data.charCodeAt(i);
                    if (48 <= ewt && ewt <= 57) {
                        
                    }
                    else {
                        $("#input_heightwithpackaging").val('');
                        $("#alert-div-inputproduct-dimension-digits").show();
                        $("#input_heightwithpackaging").addClass("inputshopempty");
                        $("html, body").animate({ 
                            scrollTop: 220 
                        }, "slow");
                        return false;
                    }
                }
        }, 10)
            setTimeout(function () {
                if($("#input_heightwithpackaging").val() !== '')
                {
                    $("#alert-div-inputproduct-height-dimension-empty").hide();
                    $("#alert-div-inputproduct-dimension-digits").hide();
                    $("#input_heightwithpackaging").removeClass("inputshopempty");
                }
            }, 20)
        })
        $("#input_heightwithpackaging").on("keypress", function () {
            var textLength = $(this).val().length;
            if (textLength >= 4) {
                $(this).val($(this).val().substr(0, 4));
                $(this).prop("maxlength", 4);
                return false;
            }
        })
        $("#input_heightwithpackaging").on("input", function () {
            if ($(this).val() !== '') {
                $(this).removeClass("inputshopempty");
                $("#alert-div-inputproduct-height-dimension-empty").hide();
                
                var data = $("#input_heightwithpackaging").val();
                var ew = data.charCodeAt(data.length-1);
                if (48 <= ew && ew <= 57) {
                    $("#alert-div-inputproduct-dimension-digits").hide();
                    $("#input_heightwithpackaging").removeClass("inputshopempty");
                }
                else if (ew === 13) {
                
                }
                else {
                    $("#input_heightwithpackaging").val($("#input_heightwithpackaging").val().substr(0, data.length-1));
                    $("#alert-div-inputproduct-dimension-digits").show();
                    $("#input_heightwithpackaging").addClass("inputshopempty");
                    $("html, body").animate({ 
                        scrollTop: 220 
                    }, "slow");
                }
            }
        })
        $("#prod_num_in_store").on('focusout', function () {
            if ($(this).val() == '') 
            {
                $("#alert-div-inputproduct-available-count-empty").show();
                $("#alert-div-inputproduct-available-count-zero-value").hide();
                $(this).addClass("inputshopempty");
            }
            else if ($(this).val() == '0')
            {
                $("#alert-div-inputproduct-available-count-zero-value").show();
                $("#alert-div-inputproduct-available-count-empty").hide();
                $("#alert-div-inputproduct-available-count-digits").hide();
                $(this).addClass("inputshopempty");
                $("html, body").animate({ 
                    scrollTop: 220 
                }, "slow");
            }
            else {
                $("#alert-div-inputproduct-available-count-zero-value").hide();
                $("#alert-div-inputproduct-available-count-empty").hide();
                $("#alert-div-inputproduct-available-count-digits").hide();
                $(this).removeClass("inputshopempty");
            }
        })
        $("#prod_num_in_store").on("input", function () {
            if ($(this).val() !== '') {
                $(this).removeClass("inputshopempty");
                $("#alert-div-inputproduct-available-count-empty").hide();
                $("#alert-div-inputproduct-available-count-zero-value").hide();
                
                var data = $("#prod_num_in_store").val();
                var ew = data.charCodeAt(data.length-1);
                if (48 <= ew && ew <= 57) {
                    $("#alert-div-inputproduct-available-count-digits").hide();
                    $("#prod_num_in_store").removeClass("inputshopempty");
                }
                else if (ew === 13) {
                
                }
                else {
                    $("#prod_num_in_store").val($("#prod_num_in_store").val().substr(0, data.length-1));
                    $("#alert-div-inputproduct-available-count-digits").show();
                    $("#prod_num_in_store").addClass("inputshopempty");
                    $("html, body").animate({ 
                        scrollTop: 220 
                    }, "slow");
                }
            }
        })
        $("#prod_num_in_store").on("keypress", function(event) {
            var ew = event.which;
            if (48 <= ew && ew <= 57) {
                $("#alert-div-inputproduct-available-count-digits").hide();
                return true;
            }
            else if (ew === 13) {
        
            }
            else {
                $("#alert-div-inputproduct-available-count-digits").show();
                $(this).addClass("inputshopempty");
                $("html, body").animate({ 
                    scrollTop: 220 
                }, "slow");
                return false;
            }
        })
        $("#prod_num_in_store").on("paste", function () {
            setTimeout(function(){
                var textLength = $("#prod_num_in_store").val().length;
                if (textLength >= 2) {
                    $("#prod_num_in_store").val($("#prod_num_in_store").val().substr(0, 2));
                    $("#prod_num_in_store").prop("maxlength", 2);
                }
                var data = $("#prod_num_in_store").val();
                for(var i=0; i<data.length; i++)
                {
                    var ewt = data.charCodeAt(i);
                    if (48 <= ewt && ewt <= 57) {
                        
                    }
                    else {
                        $("#prod_num_in_store").val('');
                        $("#alert-div-inputproduct-available-count-digits").show();
                        $("#prod_num_in_store").addClass("inputshopempty");
                        $("html, body").animate({ 
                            scrollTop: 220 
                        }, "slow");
                        return false;
                    }
                }
        }, 10)
            setTimeout(function () {
                if($("#prod_num_in_store").val() !== '')
                {
                    $("#alert-div-inputproduct-available-count-empty").hide();
                    $("#alert-div-inputproduct-available-count-digits").hide();
                    $("#prod_num_in_store").removeClass("inputshopempty");
                }
            }, 20)
        })
        $("#prod_num_in_store").on("keypress", function () {
            var textLength = $(this).val().length;
            if (textLength >= 2) {
                $(this).val($(this).val().substr(0, 2));
                $(this).prop("maxlength", 2);
                return false;
            }
        })
        
        $(function () {
            $('[data-toggle="tooltip"]').tooltip();
          })
        $(function () {
            $('.show-price-status').popover({
              container: 'body'
            })
          })
          $('body').on('click', function (e) {
            $('[data-toggle=popover]').each(function () {
                // hide any open popovers when the anywhere else in the body is clicked
                if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
                    $(this).popover('hide');
                }
            });
        });
        // $('.show-price-status').on('click', function() {
        //     var PriceStatusHtml;
        //     var SellPrice;
        //     var SellPriceInt;
        //     var RealPrice;
        //     var RealPriceInt;
        //     if($(".inputprod_sellprice").val().length === 0 && $(".inputprod_realprice").val().length === 0) {
        //         PriceStatusHtml = '<div class="product-price-status"><p class="off-price-status"> 0 </p> <p class="sell-price-status"> 0 ریال</p> <p class="off-slider-darsad"> تخفیف : 0% </p></div>';
        //     }
        //     else if ($(".inputprod_realprice").val().length === 0 && $(".inputprod_sellprice").val().length !== 0){
        //         SellPrice = $(".inputprod_sellprice").val();
        //         SellPriceInt = parseInt(SellPrice);
        //         PriceStatusHtml = '<div class="product-price-status"><p class="off-price-status"> 0 </p> <p class="sell-price-status"> ' + SellPrice + ' ریال</p> <p class="off-slider-darsad"> تخفیف : 0% </p></div>';
        //     }
        //     else if ($(".inputprod_realprice").val().length !== 0 && $(".inputprod_sellprice").val().length === 0){
        //         PriceStatusHtml = '<div class="product-price-status"><p class="sell-price-status"> قیمت فروش حتما باید وارد شود!</p></div>';
        //     }
        //     else if (parseInt($(".inputprod_realprice").val()) <= parseInt($(".inputprod_sellprice").val())) {
        //         PriceStatusHtml = '<div class="product-price-status"><p class="sell-price-status"> قیمت فروش نمیتواند بیشتر یا مساوی قیمت واقعی باشد! </p></div>';
        //     }
        //     else{
        //         SellPrice = $(".inputprod_sellprice").val();
        //         SellPriceInt = parseInt(SellPrice);

        //         RealPrice = $(".inputprod_realprice").val();
        //         RealPriceInt = parseInt(RealPrice);
                
        //         var OffPercentInt = parseInt((RealPriceInt - SellPriceInt) / RealPriceInt * 100);
        //         PriceStatusHtml = '<div class="product-price-status"><p class="off-price-status">' + RealPrice + '</p> <p class="sell-price-status"> ' + SellPrice + ' ریال</p> <p class="off-slider-darsad"> تخفیف : ' + OffPercentInt + '% </p></div>';
        //     }
        //     $(this).attr('data-content', PriceStatusHtml);
        //   })

          $(window).on("load", function() {
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
            // var e2 = document.getElementById('inputprod_realprice');
            // e2.onfocusout  = myHandler2;
            // e2.onpropertychange = e2.onfocusout ; // for IE8
            // function myHandler2() {
            //     var intprice2 = parseInt(e2.value / 10);
            //     if (intprice2 != 0) {
            //         document.getElementById('realprice-toman').innerHTML = intprice2.toPersianLetter() + ' تومان';
            //     }
            //     else {
            //         document.getElementById('realprice-toman').innerHTML = '';
            //     }
            // }
            var e2 = document.getElementById('inputprod_offamount');
            e2.onfocusout = myHandler2;
            e2.onpropertychange = e2.onfocusout ; // for IE8
            function myHandler2() {
                var intprice2 = parseInt(e2.value / 10);
                if (intprice2 != 0) {
                    document.getElementById('offamount-toman').innerHTML = intprice2.toPersianLetter() + ' تومان';
                }
                else {
                    document.getElementById('offamount-toman').innerHTML = '';
                }
            }
            var e3 = document.getElementById('input_netweight');
            e3.onfocusout  = myHandler3;
            e3.onpropertychange = e3.onfocusout ; // for IE8
            function myHandler3() {
                var thevalue = e3.value;
                var intweight3 = parseInt(e3.value / 1000);
                var kilocount = 0;
                var endkilo = true;
                if (e3.value == '')
                {
                    document.getElementById('pure-weight').innerHTML = '';
                }
                else {
                    if (intweight3 == 0) {
                        document.getElementById('pure-weight').innerHTML = e3.value.toPersianLetter() + ' گرم';
                    }
                    else if (intweight3 != 0) {
                        while (endkilo) {
                            thevalue = thevalue - 1000;
                            kilocount ++;
                            if (parseInt(thevalue / 1000) == 0)
                            {
                                endkilo = false;
                            }
                        }
                        document.getElementById('pure-weight').innerHTML = kilocount.toPersianLetter() + ' کیلو';
                        if (thevalue == 0)
                        {
                            document.getElementById('pure-weight').innerHTML = document.getElementById('pure-weight').innerHTML + 'گرم';
                        }
                        else {
                            document.getElementById('pure-weight').innerHTML = document.getElementById('pure-weight').innerHTML + ' و ' + thevalue.toPersianLetter() + ' گرم';
                        }
                    }
                }
            }
            var e4 = document.getElementById('input_packingweight');
            e4.onfocusout  = myHandler4;
            e4.onpropertychange = e4.onfocusout ; // for IE8
            function myHandler4() {
                var thevalue = e4.value;
                var intweight4 = parseInt(e4.value / 1000);
                var kilocount = 0;
                var endkilo = true;
                if (e4.value == '')
                {
                    document.getElementById('packing-weight').innerHTML = '';
                }
                else {
                    if (intweight4 == 0) {
                        document.getElementById('packing-weight').innerHTML = e4.value.toPersianLetter() + ' گرم';
                    }
                    else {
                        while (endkilo) {
                            thevalue = thevalue - 1000;
                            kilocount ++;
                            if (parseInt(thevalue / 1000) == 0)
                            {
                                endkilo = false;
                            }
                        }
                        document.getElementById('packing-weight').innerHTML = kilocount.toPersianLetter() + ' کیلو';
                        if (thevalue == 0)
                        {
                            document.getElementById('packing-weight').innerHTML = document.getElementById('packing-weight').innerHTML + 'گرم';
                        }
                        else {
                            document.getElementById('packing-weight').innerHTML = document.getElementById('packing-weight').innerHTML + ' و ' + thevalue.toPersianLetter() + ' گرم';
                        }
                    }
                }
            }
            var e5 = document.getElementById('input_lengthwithpackaging');
            e5.onfocusout  = myHandler5;
            e5.onpropertychange = e5.onfocusout ; // for IE8
            function myHandler5() {
                var thevalue2 = e5.value;
                var intlength5 = parseInt(e5.value / 100);
                var metercount = 0;
                var endmeter = true;
                if (e5.value == '')
                {
                    document.getElementById('length-dimension').innerHTML = '';
                }
                else {
                    if (intlength5 == 0) {
                        document.getElementById('length-dimension').innerHTML = e5.value.toPersianLetter() + ' سانتی متر';
                    }
                    else {
                        while (endmeter) {
                            thevalue2 = thevalue2 - 100;
                            metercount++;
                            if (parseInt(thevalue2 / 100) == 0)
                            {
                                endmeter = false;
                            }
                        }
                        document.getElementById('length-dimension').innerHTML = metercount.toPersianLetter() + ' متر';
                        if (thevalue2 != 0)
                        {
                            document.getElementById('length-dimension').innerHTML = document.getElementById('length-dimension').innerHTML + ' و ' + thevalue2.toPersianLetter() + ' سانتی متر';
                        }
                    }
                }
            }
            var e6 = document.getElementById('input_widthwithpackaging');
            e6.onfocusout  = myHandler6;
            e6.onpropertychange = e6.onfocusout ; // for IE8
            function myHandler6() {
                var thevalue3 = e6.value;
                var intlength6 = parseInt(e6.value / 100);
                var metercount2 = 0;
                var endmeter2 = true;
                if (e6.value == '')
                {
                    document.getElementById('width-dimension').innerHTML = '';
                }
                else {
                    if (intlength6 == 0) {
                        document.getElementById('width-dimension').innerHTML = e6.value.toPersianLetter() + ' سانتی متر';
                    }
                    else {
                        while (endmeter2) {
                            thevalue3 = thevalue3 - 100;
                            metercount2++;
                            if (parseInt(thevalue3 / 100) == 0)
                            {
                                endmeter2 = false;
                            }
                        }
                        document.getElementById('width-dimension').innerHTML = metercount2.toPersianLetter() + ' متر';
                        if (thevalue3 != 0)
                        {
                            document.getElementById('width-dimension').innerHTML = document.getElementById('width-dimension').innerHTML + ' و ' + thevalue3.toPersianLetter() + ' سانتی متر';
                        }
                    }
                }
            }
            var e7 = document.getElementById('input_heightwithpackaging');
            e7.onfocusout  = myHandler7;
            e7.onpropertychange = e7.onfocusout ; // for IE8
            function myHandler7() {
                var thevalue4 = e7.value;
                var intlength7 = parseInt(e7.value / 100);
                var metercount3 = 0;
                var endmeter3 = true;
                if (e7.value == '')
                {
                    document.getElementById('height-dimension').innerHTML = '';
                }
                else {
                    if (intlength7 == 0) {
                        document.getElementById('height-dimension').innerHTML = e7.value.toPersianLetter() + ' سانتی متر';
                    }
                    else {
                        while (endmeter3) {
                            thevalue4 = thevalue4 - 100;
                            metercount3++;
                            if (parseInt(thevalue4 / 100) == 0)
                            {
                                endmeter3 = false;
                            }
                        }
                        document.getElementById('height-dimension').innerHTML = metercount3.toPersianLetter() + ' متر';
                        if (thevalue4 != 0)
                        {
                            document.getElementById('height-dimension').innerHTML = document.getElementById('height-dimension').innerHTML + ' و ' + thevalue4.toPersianLetter() + ' سانتی متر';
                        }
                    }
                }
            }
            if ($("#inputprod_sellprice").val() !== '')
            {
                myHandler();
            }
            // if ($("#inputprod_realprice").val() !== '')
            // {
            //     myHandler2();
            // }
            if ($("#input_netweight").val() !== '')
            {
                myHandler3();
            }
            if ($("#input_packingweight").val() !== '')
            {
                myHandler4();
            }
            if ($("#input_lengthwithpackaging").val() !== '')
            {
                myHandler5();
            }
            if ($("#input_widthwithpackaging").val() !== '')
            {
                myHandler6();
            }
            if ($("#input_heightwithpackaging").val() !== '')
            {
                myHandler7();
            }
            if ($(".inputprod_realprice").val() !== '' && $(".inputprod_sellprice").val() !== '' && (parseInt($(".inputprod_realprice").val()) > parseInt($(".inputprod_sellprice").val())))
            {
                validPrices = true;
            }
            if ($("#input_packingweight").val() !== '' && $("#input_netweight").val() !== '' && (parseInt($("#input_netweight").val()) < parseInt($("#input_packingweight").val())))
            {
                validWeight = true;
            }
            if($('.product-detail-now option:selected ').text() != 'آماده در انبار'){
                $('#detail-num-box').hide();
                var el = $('#detail-now-box');
                el.addClass('col-md-6');
                el.removeClass('col-md-4');
            }
            else{
                $('#detail-num-box').show();
                var el = $('#detail-now-box');
                el.addClass('col-md-4');
                el.removeClass('col-md-6');
            }
            });

checkProductFields = function () {
    //Img
    $("#alert-div-inputproduct-img-empty").hide();

    //Shop
    $("#alert-div-inputproduct-shop-empty").hide();
    $("#inpuShop").removeClass("inputshopempty");

    //Category
    $("#alert-div-inputproduct-category-empty").hide();
    $("#alert-div-inputproduct-category-count-limit").hide();
    $(".category-product-list .chosen-choices").removeClass("inputshopempty_Cat");

    //Product Send Area
    $("#alert-div-inputproduct-send-area-limit").hide();
    $(".send-area-list .chosen-choices").removeClass("inputshopempty_Cat");

    //Product Send Area Exception
    $("#alert-div-inputproduct-send-area-exception-limit").hide();
    $(".send-area-exception-list .chosen-choices").removeClass("inputshopempty_Cat");

    var checks = true;

    //Img
	if ($("#avatar").prop("src") == 'http://localhost:8000/static/images/image_upload.jpg') {
		$("#alert-div-inputproduct-img-empty").show();
		checks = false;
	}
    
    // if ($(".inputprod_img").val() == '')
    // {
    //     $("#alert-div-inputproduct-img-empty").show();
    //     checks = false;
    // }
    
    //Title
    // var checkTitleValidChars = checkValidChars($("#inputprod_title").val());
    if ($("#inputprod_title").val() == '')
    {
        $("#alert-div-inputproduct-title-empty").show();
        $("#inputprod_title").addClass("inputshopempty");
        checks = false;
    }
    // else if (!checkTitleValidChars)
    // {
    //     $("#alert-div-inputproduct-title-valid-chars").show();
    //     $("#inputprod_title").addClass("inputshopempty");
    //     checks = false;
    // }
    else if ($("#inputprod_title").val().length < 2)
    {
        $("#alert-div-inputproduct-title-minlength").hide();
        $("#inputprod_title").addClass("inputshopempty");
        checks = false;
    }
    else if ($("#inputprod_title").val().length > 170)
    {
        $("#alert-div-inputproduct-title-maxlength").show();
        $("#inputprod_title").addClass("inputshopempty");
        checks = false;
    }

    if ($("#inpuShop")[0].selectedIndex === -1)
    {
        $("#alert-div-inputproduct-shop-empty").show();
        $("#inpuShop").addClass("inputshopempty");
        checks = false;
    }

    //Des
    // var checkDesValidChars = checkValidChars($("#inputProdDes").val());
    if ($("#inputProdBio").val() == '')
    {
        $("#alert-div-inputproduct-bio-empty").show();
        $("#inputProdBio").addClass("inputshopempty");
        checks = false;
    }
    // else if (!checkDesValidChars)
    // {
    //     $("#alert-div-inputproduct-about-valid-chars").show();
    //     $("#inputProdDes").addClass("inputshopempty");
    //     checks = false;
    // }

    if($(".category-product :selected").length === 0)
    {
        $("#alert-div-inputproduct-category-empty").show();
        $(".category-product-list .chosen-choices").addClass("inputshopempty_Cat");
        checks = false;
    }
    else if ($(".category-product :selected").length > 10)
    {
        $("#alert-div-inputproduct-category-count-limit").show();
        $(".category-product-list .chosen-choices").addClass("inputshopempty_Cat");
        checks = false;
    }
    if ($("#inputSubMarket")[0].selectedIndex === -1)
    {
        $("#alert-div-inputproduct-submarket-empty").show();
        $("#inputSubMarket").addClass("inputshopempty");
        checks = false;
    }
    //Intro
    if ($("#inputProdBio").val().length > 200)
    {
        $("#alert-div-inputproduct-bio-maxlength").show();
        $("#inputProdBio").addClass("inputshopempty");
        checks = false;   
    }
    // if ($("#inputProdBio").val().length > 0) {
    //     var checkIntroValidChars = checkValidChars($("#inputProdBio").val());
    //     if (!checkIntroValidChars)
    //     {
    //         $("#alert-div-inputproduct-intro-valid-chars").show();
    //         $("#inputProdBio").addClass("inputshopempty");
    //         checks = false;
    //     }
    // }
    //Story
    // if ($("#inputProdStory").val().length > 0) {
    //     var checkStoryValidChars = checkValidChars($("#inputProdStory").val());
    //     if (!checkStoryValidChars)
    //     {
    //         $("#alert-div-inputproduct-story-valid-chars").show();
    //         $("#inputProdStory").addClass("inputshopempty");
    //         checks = false;
    //     }
    // }
    if ($(".inputprod_sellprice").val() == '')
    {
        $("#alert-div-inputproduct-sell-price-empty").show();
        $(".inputprod_sellprice").addClass("inputshopempty");
        checks = false;
    }
    else if ($(".inputprod_sellprice").val().length < 2) {
        $("#alert-div-inputproduct-sell-price-minlength").show();
        $(".inputprod_sellprice").addClass("inputshopempty");
        checks = false;
    }
    if (offornot && $("#inputprod_offamount").val() == '')
    {
        $("#alert-div-inputproduct-off-empty").show();
        $("#inputprod_offamount").addClass("inputshopempty");
        checks = false;
    }
    else if (offornot && $("#inputprod_offamount").val().length < 2)
    {
        $("#alert-div-inputproduct-off-length").show();
        $("#inputprod_offamount").addClass("inputshopempty");
        checks = false;
    }
    // else if ($(".inputprod_realprice").val() != '' && $(".inputprod_realprice").val().length < 5)
    // {
    //     $("#alert-div-inputproduct-real-price-minlength").show();
    //     $(".inputprod_realprice").addClass("inputshopempty");
    //     checks = false;    
    // }
    // else if ($(".inputprod_realprice").val() != '' && $(".inputprod_realprice").val().length >= 5 && $(".inputprod_sellprice").val().length >= 5 && !validPrices) {
    //     $("#alert-div-inputproduct-price-comparison").show();
    //     $(".inputprod_sellprice").addClass("inputshopempty");
    //     $(".inputprod_realprice").addClass("inputshopempty");
    //     checks = false;
    // }
    if ($("#input_netweight").val() == '') {
        $("#alert-div-inputproduct-pure-weight-empty").show();
        $("#input_netweight").addClass("inputshopempty");
        checks = false;
    }
    if ($("#input_packingweight").val() == '') {
        $("#alert-div-inputproduct-packing-weight-empty").show();
        $("#input_packingweight").addClass("inputshopempty");
        checks = false;
    }
    if ($("#input_netweight").val() != '' && $("#input_packingweight").val() != '' && !validWeight) {
        $("#alert-div-inputproduct-weight-comparison").show();
        $("#input_netweight").addClass("inputshopempty");
        $("#input_packingweight").addClass("inputshopempty");
        checks = false;
    }
    if($("#input_lengthwithpackaging").val() == '') {
        $("#alert-div-inputproduct-length-dimension-empty").show();
        $("#input_lengthwithpackaging").addClass("inputshopempty");
        checks = false;
    }
    if($("#input_widthwithpackaging").val() == '') {
        $("#alert-div-inputproduct-width-dimension-empty").show();
        $("#input_widthwithpackaging").addClass("inputshopempty");
        checks = false;
    }
    if($("#input_heightwithpackaging").val() == '') {
        $("#alert-div-inputproduct-height-dimension-empty").show();
        $("#input_heightwithpackaging").addClass("inputshopempty");
        checks = false;
    }
    if($(".send-area-list .chosen-choices").find($(".search-choice")).length > 999)
    {
        $("#alert-div-inputproduct-send-area-limit").show();
        $(".send-area-list .chosen-choices").addClass("inputshopempty_Cat");
        checks = false;
    }
    if($(".send-area-exception-list .chosen-choices").find($(".search-choice")).length > 999)
    {
        $("#alert-div-inputproduct-send-area-exception-limit").show();
        $(".send-area-exception-list .chosen-choices").addClass("inputshopempty_Cat");
        checks = false;
    }
    if($('.product-detail-now option:selected ').text() == 'آماده در انبار') {
        if($("#prod_num_in_store").val() == '')
            {
                $("#alert-div-inputproduct-available-count-empty").show();
                $("#prod_num_in_store").addClass("inputshopempty");
                checks = false;
            }
        else if($("#prod_num_in_store").val() == '0' || $("#prod_num_in_store").val() == '00')
            {
                $("#alert-div-inputproduct-available-count-zero-value").show();
                $("#prod_num_in_store").addClass("inputshopempty");
                checks = false;
            }
        }
    if(!checks) {
        $("html, body").animate({
            scrollTop: 220 
        }, "slow");
    }
    return checks;
}

setSomeFormDataFields = function () {
    //prodCategoryList
    prodCategroyList = '';
    var catlist = [];
    var cats = $("#select_cat_chosen .chosen-choices .search-choice").find('li');
	for (var i = 0; i<$("#select_cat_chosen .chosen-choices .search-choice").length; i++) 
        {
            catlist[i] = cats.prevObject[i].innerText;
		}
    var eachoption = [];
	for (var i = 0; i<$("#select-cat option").length; i++) 
		{
			eachoption = $("#select-cat option")[i].text;
			for (var j = 0; j<$("#select_cat_chosen .chosen-choices .search-choice").length; j++) {
			if (catlist[j] == eachoption ) {
				prodCategroyList += $("#select-cat option")[i].value + '~';
				break;
			}
		}
	}

	if (prodCategroyList.length > 0)
	{
		prodCategroyList = prodCategroyList.substring(0, prodCategroyList.length - 1);
	}
	else {
		for(var i=0; i<$(".category-product :selected").length; i++) {
			prodCategroyList += $(".category-product :selected")[i].value + '~';
		}
		if (prodCategroyList.length > 0)
		{
			prodCategroyList = prodCategroyList.substring(0, prodCategroyList.length - 1);
		}
    }

    //Send Areas
    prodSendAreas = '';    
    for(i=0; i < $($("#inputPostRange_chosen .chosen-choices").find("li.search-choice a")).length; i++)
    {
        prodSendAreas += (parseInt($($("#inputPostRange_chosen .chosen-choices").find("li.search-choice a")[i]).attr('data-option-array-index')) + 1).toString() + '~';
    }
    
	if (prodSendAreas.length > 0)
	{
		prodSendAreas = prodSendAreas.substring(0, prodSendAreas.length - 1);
	}
	else {
		for(var i=0; i<$("#inputPostRange :selected").length; i++) {
            prodSendAreas += $("#inputPostRange :selected")[i].value + '~';
		}
		if (prodSendAreas.length > 0)
		{
			prodSendAreas = prodSendAreas.substring(0, prodSendAreas.length - 1);
		}
    }
    //Send Areas Exception
    prodSendAreasException = '';
    for(i=0; i < $($("#inputPostRangeException_chosen .chosen-choices").find("li.search-choice a")).length; i++)
    {
        prodSendAreasException += (parseInt($($("#inputPostRangeException_chosen .chosen-choices").find("li.search-choice a")[i]).attr('data-option-array-index')) + 1).toString() + '~';
    }

	if (prodSendAreasException.length > 0)
	{
		prodSendAreasException = prodSendAreasException.substring(0, prodSendAreasException.length - 1);
	}
	else {
		for(var i=0; i<$("#inputPostRangeException :selected").length; i++) {
			prodSendAreasException += $("#inputPostRangeException :selected")[i].value + '~';
		}
		if (prodSendAreasException.length > 0)
		{
			prodSendAreasException = prodSendAreasException.substring(0, prodSendAreasException.length - 1);
		}
    }
}
checkValidInputsMakeSomeFields = function () {
            setSomeFormDataFields();
            var checks = checkProductFields();
            if ($("#inputslugProd").val() == '')
            {
                $("#alert-div-inputproduct-slug-empty").show();
                $("#inputslugProd").addClass("inputshopempty");
                checks = false;
            }
            else if (!SlugDup)
            {
                $("#alert-div-inputproduct-slug-dup").show();
                $("#inputslugProd").addClass("inputshopempty");
                checks = false;
            }
            else {
                var slugData = $("#inputslugProd").val();
                for (var i=0; i < slugData.length; i++)
                {
                    var eev = slugData.charCodeAt(i);
                    if (97 <= eev && eev <= 122 || 48 <= eev && eev <= 57) {
        
                    }
                    else if (eev === 45) {
                        
                    }
                    else {
                        $("#alert-div-inputproduct-slug-english").show();
                        $("#inputslugProd").addClass("inputshopempty");
                        checks = false;
                    }
                }
            }
            if(!checks) {
                $("html, body").animate({
                    scrollTop: 220 
                }, "slow");
            }
            return checks;
        }

        checkValidInputsMakeSomeFieldsEdit = function () {
            setSomeFormDataFields();
            var checks = checkProductFields();
            return checks;
        }

    // mark

    $(".product-detail-now" ).change(function() {
        if($('.product-detail-now option:selected ').text() != 'آماده در انبار'){
            $('#detail-num-box').hide();
            var el = $('#detail-now-box');
            el.addClass('col-md-6');
            el.removeClass('col-md-4');
            $("#alert-div-inputproduct-available-count-empty").hide();
            $("#alert-div-inputproduct-available-count-digits").hide();
            $("#alert-div-inputproduct-available-count-zero-value").hide();
        }
        else{
            $('#detail-num-box').show();
            var el = $('#detail-now-box');
            el.addClass('col-md-4');
            el.removeClass('col-md-6');
        }
    });

    $(".product-detail-now_for_opt_attr" ).change(function() {
        if($('.product-detail-now_for_opt_attr option:selected ').text() != 'آماده در انبار') {
            $('#detail-num-box-for-opt-attr').hide();
            var el = $('#detail-now-box-for_opt_attr');
            el.addClass('col-md-12');
            el.removeClass('col-md-8');
            // $("#alert-div-inputproduct-available-count-empty").hide();
            // $("#alert-div-inputproduct-available-count-digits").hide();
            // $("#alert-div-inputproduct-available-count-zero-value").hide();
        }
        else{
            $('#detail-num-box-for-opt-attr').show();
            var el = $('#detail-now-box-for_opt_attr');
            el.addClass('col-md-8');
            el.removeClass('col-md-12');
        }
    });

    $(".input-pic-file").on("change", function () {
        $(".choose-pic-input-name").prop('placeholder', $(this).val());
    })

    $("#product_optattr_extra_weight").on("input", function () {
            if ($(this).val() !== '') {
                $(this).removeClass("inputshopempty");
                
                var data = $("#product_optattr_extra_weight").val();
                var ew = data.charCodeAt(data.length-1);
                if (48 <= ew && ew <= 57) {
                    $("#product_optattr_extra_weight").removeClass("inputshopempty");
                }
                else if (ew === 13) {
                
                }
                else {
                    $("#product_optattr_extra_weight").val($("#product_optattr_extra_weight").val().substr(0, data.length-1));
                    $("#product_optattr_extra_weight").addClass("inputshopempty");
                }
            }
        })
        $("#product_optattr_extra_weight").on("keypress", function () {
            var textLength = $(this).val().length;
            if (textLength >= 4) {
                $(this).val($(this).val().substr(0, 4));
                $(this).prop("maxlength", 4);
                return false;
            }
        })
        $("#product_optattr_extra_weight").on("paste", function () {
            setTimeout(function(){
                var textLength = $("#product_optattr_extra_weight").val().length;
                if (textLength >= 4) {
                    $("#product_optattr_extra_weight").val($("#product_optattr_extra_weight").val().substr(0, 4));
                    $("#product_optattr_extra_weight").prop("maxlength", 4);
                }
                var data = $("#product_optattr_extra_weight").val();
                for(var i=0; i<data.length; i++)
                {
                    var ewt = data.charCodeAt(i);
                    if (48 <= ewt && ewt <= 57) {
                        
                    }
                    else {
                        $("#product_optattr_extra_weight").val('');
                        $("#product_optattr_extra_weight").addClass("inputshopempty");	
                        return false;
                    }
                }
        }, 10)
            setTimeout(function () {
                if($("#product_optattr_extra_weight").val() !== '')
                {
                    $("#product_optattr_extra_weight").removeClass("inputshopempty");
                }
            }, 20)
        })