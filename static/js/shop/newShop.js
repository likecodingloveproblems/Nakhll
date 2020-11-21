//Img
$("#alert-div-inputshop-img-empty").hide();

//Title
$("#alert-div-inputshop-title-empty").hide();
$("#alert-div-inputshop-title-minlength").hide();
$("#alert-div-inputshop-title-maxlength").hide();
// $("#alert-div-inputshop-title-valid-chars").hide();
// $("#alert-div-inputshop-title-persian").hide();

//Slug
$("#alert-div-inputshop-slug-empty").hide();
$("#alert-div-inputshop-slug-english").hide();
$("#alert-div-inputshop-slug-dup").hide();

//About
// $("#alert-div-inputshop-about-valid-chars").hide();

// State
$("#alert-div-inputshop-state-unknown").hide();

//BigCity
$("#alert-div-inputshop-bigcity-unknown").hide();

//City
$("#alert-div-inputshop-city-unknown").hide();

//Submarket
$("#alert-div-inputshop-submarket-unknown").hide();
$("#alert-div-inputshop-submarket-limit-count").hide();

//Bio
$("#alert-div-inputshop-Bio-maxlength").hide();
// $("#alert-div-inputshop-bio-valid-chars").hide();

//Week Holidays
$("#alert-div-inputshop-week-holidays-all").hide();

//Rules
$("#alert-div-inputshop-rules-disagree").hide();

//System Error
$("#alert-div-system-error").hide();


//Img
$("#alert-div-inputshop-img-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
'<i class="far fa-exclamation-circle"></i>' +
'<p>یک عکس برای حجره باید انتخاب شود.</p>' +
'</div></div>');

//Title
$("#alert-div-inputshop-title-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
	'<i class="far fa-exclamation-circle"></i>' +
	'<p>عنوان حجره نمیتواند خالی باشد.</p>' +
	'</div></div>');

// $("#alert-div-inputshop-title-valid-chars").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
// 	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
// 	'<i class="far fa-exclamation-circle"></i>' +
// 	'<p>در عنوان حجره از کاراکترهای غیر مجاز استفاده شده است.</p>' +
// 	'</div></div>');

// $("#alert-div-inputshop-title-persian").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
// 	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
// 	'<i class="far fa-exclamation-circle"></i>' +
// 	'<p>برای عنوان فقط از حروف فارسی و اعداد میتوانید استفاده کنید.</p>' +
// 	'</div></div>');

$("#alert-div-inputshop-title-minlength").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
	'<i class="far fa-exclamation-circle"></i>' +
	'<p>عنوان حجره باید از 2 کارکتر بیشتر باشد.</p>' +
	'</div></div>');

$("#alert-div-inputshop-title-maxlength").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
	'<i class="far fa-exclamation-circle"></i>' +
	'<p>عنوان حجره نباید از 70 کارکتر بیشتر باشد.</p>' +
	'</div></div>');

//Slug
$("#alert-div-inputshop-slug-empty").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
	'<i class="far fa-exclamation-circle"></i>' +
	'<p>وارد کردن شناسه حجره الزامی است.</p>' +
	'</div></div>');

$("#alert-div-inputshop-slug-english").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
	'<i class="far fa-exclamation-circle"></i>' +
	'<p>شناسه حجره باید شامل حروف انگلیسی کوچک، خط تیره ("-") و بدون فاصله باشد.</p>' +
	'</div></div>');

$("#alert-div-inputshop-slug-dup").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
	'<i class="far fa-exclamation-circle"></i>' +
	'<p>این شناسه حجره تکراری میباشد.</p>' +
	'</div></div>');


// About
// $("#alert-div-inputshop-about-valid-chars").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
// 	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
// 	'<i class="far fa-exclamation-circle"></i>' +
// 	'<p>در درباره حجره از کاراکترهای غیر مجاز استفاده شده است.</p>' +
// 	'</div></div>');

// State
$("#alert-div-inputshop-state-unknown").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
	'<i class="far fa-exclamation-circle"></i>' +
	'<p>استان خود را باید مشخص کنید.</p>' +
	'</div></div>');

//BigCity
$("#alert-div-inputshop-bigcity-unknown").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
	'<i class="far fa-exclamation-circle"></i>' +
	'<p>شهرستان خود را باید مشخص کنید.</p>' +
	'</div></div>');

//City
$("#alert-div-inputshop-city-unknown").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
	'<i class="far fa-exclamation-circle"></i>' +
	'<p>شهر خود را باید مشخص کنید.</p>' +
	'</div></div>');

//Submarket
$("#alert-div-inputshop-submarket-unknown").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
	'<i class="far fa-exclamation-circle"></i>' +
	'<p>مشخص کردن راسته حجره الزامی است.</p>' +
	'</div></div>');

$("#alert-div-inputshop-submarket-limit-count").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
	'<i class="far fa-exclamation-circle"></i>' +
	'<p>تعداد راسته های حجره نمیتواند بیش از 7 مورد باشد.</p>' +
	'</div></div>');

//Bio
$("#alert-div-inputshop-Bio-maxlength").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
	'<i class="far fa-exclamation-circle"></i>' +
	'<p>معرفی حجره دار نباید از 200 کارکتر بیشتر باشد.</p>' +
	'</div></div>');

// $("#alert-div-inputshop-bio-valid-chars").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
// 	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
// 	'<i class="far fa-exclamation-circle"></i>' +
// 	'<p>در فیلد معرفی حجره دار از کاراکترهای غیر مجاز استفاده شده است.</p>' +
// 	'</div></div>');
	

//Week Holidays
$("#alert-div-inputshop-week-holidays-all").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
	'<i class="far fa-exclamation-circle"></i>' +
	'<p>حجره نمیتواند هر روز هفته تعطیل باشد.</p>' +
	'</div></div>');

//Rules
$("#alert-div-inputshop-rules-disagree").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
	'<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
	'<i class="far fa-exclamation-circle"></i>' +
	'<p>برای ساخت حجره موافقت با قوانین قرارداد و ضوابط الزامی میباشد.</p>' +
	'</div></div>');

//System Error
$("#alert-div-system-error").html('<div class="col-xl-12 xol-lg-12 col-md-12 col-sm-12 col-12">' +
    '<div class="alert alert-warning alert-dismissible fade show custom-alart alert-width limit-alert" role="alert">' +
    '<i class="far fa-exclamation-circle"></i>' +
    '<p>خطا! صفحه را رفرش کرده مجددا سعی کنید.</p>' +
    '</div></div>');


	//Img Events

	//Title Events
			
		$("#inputshop_title").on("focusout", function () {
			var inputshopTitleLength = $(this).val().length;

			if ($(this).val() === '') {
				$(this).addClass("inputshopempty");
				$("#alert-div-inputshop-title-empty").show();
				$("#alert-div-inputshop-title-minlength").hide();
			}
			else if (inputshopTitleLength < 2) {
				$(this).addClass("inputshopempty");
				$("#alert-div-inputshop-title-minlength").show();
				$("#alert-div-inputshop-title-empty").hide();
				$(this).prop("minLength", 2);
				$("html, body").animate({ 
					scrollTop: 220 
				}, "slow");
			}
			else {
				$("#alert-div-inputshop-title-minlength").hide();
				$("#alert-div-inputshop-title-empty").hide();
			}
		})
		$("#inputshop_title").on("input", function () {
			var InpShopTitleLength = $(this).val().length;
			if ($(this).val() !== '') {
				$(this).removeClass("inputshopempty");
				$("#alert-div-inputshop-title-empty").hide();
				// $("#alert-div-inputshop-title-valid-chars").hide();
			}
			if (InpShopTitleLength >= 2) {
				$(this).removeClass("inputshopempty");
				$("#alert-div-inputshop-title-minlength").hide();
			}
		})
		$("#inputshop_title").on("keypress", function () {
			var textLength = $(this).val().length;
			if (textLength >= 70) {
				$(this).val($(this).val().substr(0, 70));
				$(this).prop("maxlength", 70);
				return false;
			}
		})
		$("#inputshop_title").on("paste", function () {
            setTimeout(function () {
                var textLength = $("#inputshop_title").val().length;
                if (textLength >= 70) {
                    $("#inputshop_title").val($("#inputshop_title").val().substr(0, 70));
                    $("#inputshop_title").prop("maxlength", 70);
				}
			})
		})
		
	// Slug Events
		$("#inputslugshop").on("focusout", function () {
			if ($(this).val() === '') {
				$(this).addClass("inputshopempty");
				$("#alert-div-inputshop-slug-empty").show();
			}
			else {
				$("#alert-div-inputshop-slug-empty").hide();
				$("#alert-div-inputproduct-slug-english").hide();
			}
		})
		$("#inputslugshop").on("input", function () {
			if ($(this).val() !== '') {
				$(this).removeClass("inputshopempty");
				$("#alert-div-inputshop-slug-empty").hide();

				var data = $("#inputslugshop").val();
                var ews = data.charCodeAt(data.length-1);
                if (97 <= ews && ews <= 122 || 48 <= ews && ews <= 57) {
                    $("#alert-div-inputshop-slug-english").hide();
                    $("#inputslugshop").removeClass("inputshopempty");
                }
                else if (ews === 45) {
                    $("#alert-div-inputshop-slug-english").hide();
                    $("#inputslugshop").removeClass("inputshopempty");
                }
                else {
                    $("#inputslugshop").val($("#inputslugshop").val().substr(0, data.length-1));
                    $("#alert-div-inputshop-slug-english").show();
                    $("#inputslugshop").addClass("inputshopempty");
                    $("html, body").animate({ 
                        scrollTop: 220 
                    }, "slow");
                }
			}
		})
		$("#inputslugshop").on("keypress", function(event) {
			var es = event.which;
			if (97 <= es && es <= 122 || 48 <= es && es <= 57)
			{
				$("#alert-div-inputshop-slug-english").hide();
				return true;
			}
			else if (es === 45)
			{
				$("#alert-div-inputshop-slug-english").hide();
				return true;
			}
			else if (es === 13) {
        
			}
			else {
				$(this).addClass("inputshopempty");
				$("#alert-div-inputshop-slug-english").show();
				$("html, body").animate({ 
					scrollTop: 220 
				}, "slow");
				return false;
			}
		})
		$("#inputslugshop").on("paste drop", function () {
			setTimeout(function(){
				var data = $("#inputslugshop").val();
				for(var i=0; i<data.length; i++)
				{
					var ews = data.charCodeAt(i);
					if (97 <= ews && ews <= 122 || 48 <= ews && ews <= 57) {
						
					}
					else if (ews === 45) {
						
					}
					else {
						$("#inputslugshop").val('');
						$("#alert-div-inputshop-slug-english").show();
						$(this).addClass("inputshopempty");	
						$("html, body").animate({ 
							scrollTop: 220 
						}, "slow");
						return false;
					}
				}
		}, 10)
			setTimeout(function () {
				if($("#inputslugshop").val() !== '')
				{
					$("#alert-div-inputshop-slug-empty").hide();
					$("#alert-div-inputshop-slug-english").hide();
					$("#inputslugshop").removeClass("inputshopempty");	
				}
			}, 20)
		})

	//About Shop
	$("#inputshopdes").on("input", function() {
		// $("#alert-div-inputshop-about-valid-chars").hide();
		$(this).removeClass('inputshopempty');
	})

	// State, BigCity, City Events

		var stateValid = false;
		var bigcityValid = false;
		var cityValid = false;
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
			stateValid = checkDestination($("#inputshopState"));
			bigcityValid = checkDestination($("#inputshopBigCity"));
			cityValid = checkDestination($("#inputshopCity"));

			$("#inputshopState").chosen().change(function() {
				stateValid = checkDestination($(this));
				if (stateValid == false)
				{
					bigcityValid = false;
					cityValid = false;
				}
				else {
					$("#alert-div-inputshop-state-unknown").hide();
					$("#inputshopState_chosen .chosen-single").removeClass("inputshopempty_Cat");
				}
			})
			$("#inputshopBigCity").chosen().change(function() {
				bigcityValid = checkDestination($(this));
				if (bigcityValid == false)
				{
					cityValid = false;
				}
				else {
					$("#alert-div-inputshop-bigcity-unknown").hide();
					$("#inputshopBigCity_chosen .chosen-single").removeClass("inputshopempty_Cat");
				}
			})
			$("#inputshopCity").chosen().change(function() {
				cityValid = checkDestination($(this));
				if (cityValid) {
					$("#alert-div-inputshop-city-unknown").hide();
					$("#inputshopCity_chosen .chosen-single").removeClass("inputshopempty_Cat");
				}
			})
		})
		
	// Submarket Events
	$(document).ready(function () {
		$("#select-cat").chosen({max_selected_options: 10, rtl: true});
		$("#select-cat").chosen().change(function (){
			if ($(".submarket-shop :selected").length > 0) {
				$("#alert-div-inputshop-submarket-unknown").hide();
				$(".submarket-shop-list .chosen-choices").removeClass("inputshopempty_Cat");
			}
		})
	})
	// Shopper Bio
	$("#inputshopBio").on("input", function () {
		// $("#alert-div-inputshop-bio-valid-chars").hide();
		$(this).removeClass('inputshopempty');
	})
	$("#inputshopBio").on("keypress", function () {
		var textLength = $(this).val().length;
		if (textLength >= 200) {
			$(this).val($(this).val().substr(0, 200));
			$(this).prop("maxlength", 200);
			return false;
		}
	})
	$("#inputshopBio").on("paste", function () {
		setTimeout(function () {
			var textLength = $("#inputshopBio").val().length;
			if (textLength >= 200) {
				$("#inputshopBio").val($("#inputshopBio").val().substr(0, 200));
				$("#inputshopBio").prop("maxlength", 200);
			}
		})
	})
	// Rules Events
	
checkFormEmptiesForEditShop = function () {
	var checks = true;

	//Img
	if ($("#avatar").prop("src") == 'http://uupload.ir/files/3t7w_upload.jpg') {
		$("#alert-div-inputshop-img-empty").show();
		checks = false;
	}

	//Title
	var InpShop_TitleLength = $("#inputshop_title").val().length;
	// var checkTitleValidChars = checkValidChars($("#inputshop_title").val());
	if ($("#inputshop_title").val() === '') {
		$("#alert-div-inputshop-title-empty").show();
		$("#inputshop_title").addClass("inputshopempty");
		checks = false;
	}
	// else if (!checkTitleValidChars)
	// {
	// 	$("#alert-div-inputshop-title-valid-chars").show();
	// 	$("#inputshop_title").addClass("inputshopempty");
	// 	checks = false;
	// }
	else if (InpShop_TitleLength < 2) {
		$("#alert-div-inputshop-title-minlength").show();
		$("#inputshop_title").addClass("inputshopempty");
		checks = false;
	}
	else if (InpShop_TitleLength > 70) {
		$("#alert-div-inputshop-title-maxlength").show();
		$("#inputshop_title").addClass("inputshopempty");
		checks = false;
	}
	// if ($("#inputshopdes").val().length !== 0) {
	// 	var checkAboutValidChars = checkValidChars($("#inputshopdes").val());
	// 	if (!checkAboutValidChars) {
	// 		$("#alert-div-inputshop-about-valid-chars").show();
	// 		$("#inputshopdes").addClass("inputshopempty");
	// 		checks = false;
	// 	}
	// }
	stateValid = checkDestination($("#inputshopState"));
	bigcityValid = checkDestination($("#inputshopBigCity"));
	cityValid = checkDestination($("#inputshopCity"));
	if(stateValid == false)
	{
		$("#alert-div-inputshop-state-unknown").show();
		$("#inputshopState_chosen .chosen-single").addClass("inputshopempty_Cat");
		checks = false;
	}
	if(bigcityValid == false)
	{
		$("#alert-div-inputshop-bigcity-unknown").show();
		$("#inputshopBigCity_chosen .chosen-single").addClass("inputshopempty_Cat");
		checks = false;
	}
	if(cityValid == false)
	{
		$("#alert-div-inputshop-city-unknown").show();
		$("#inputshopCity_chosen .chosen-single").addClass("inputshopempty_Cat");
		checks = false;
	}
	if($(".submarket-shop :selected").length === 0)
	{
		$("#alert-div-inputshop-submarket-unknown").show();
		$(".submarket-shop-list .chosen-choices").addClass("inputshopempty_Cat");
		checks = false;
	}
	else if ($(".submarket-shop :selected").length > 10) {
		$(".submarket-shop-list .chosen-choices").addClass("inputshopempty_Cat");
		$("#alert-div-inputshop-submarket-limit-count").show();
		checks = false;
	}

	var inputBioLength = $("#inputshopBio").val().length;
	if (inputBioLength > 200) {
		$("#alert-div-inputshop-Bio-maxlength").show();
		$("#inputshopBio").addClass("inputshopempty");
		checks = false;
	}
	// if (inputBioLength > 0) {
	// 	var checkBioValidChars = checkValidChars($("#inputshopBio").val());
	// 	if (!checkBioValidChars)
	// 	{
	// 		$("#alert-div-inputshop-bio-valid-chars").show();
	// 		$("#inputshopBio").addClass("inputshopempty");
	// 		checks = false;
	// 	}
	// }
	if ($("#SATCheck").is(":checked") && $("#SUNCheck").is(":checked") && $("#MONCheck").is(":checked") && $("#TUECheck").is(":checked") && $("#WEDCheck").is(":checked") && $("#THUCheck").is(":checked") && $("#FRICheck").is(":checked")) {
		$("#alert-div-inputshop-week-holidays-all").show();
		checks = false;
	}
	return checks;
}

checkFormEmpties = function () {
	checks = true;
	checks = checkFormEmptiesForEditShop();
    if (!($("#ruleCheck").prop('checked'))) {
		$("#alert-div-inputshop-rules-disagree").show();
        checks = false;
	}
	//Slug
	if ($("#inputslugshop").val() === '') {
		$("#alert-div-inputshop-slug-empty").show();
		$("#inputslugshop").addClass("inputshopempty");
		checks = false;
	}
	else if (!SlugDup)
	{
		$("#alert-div-inputshop-slug-dup").show();
		$("#inputslugshop").addClass("inputshopempty");
		checks = false;
	}
	else {
		var slugData = $("#inputslugshop").val();
		for (var i=0; i < slugData.length; i++)
		{
			var eev = slugData.charCodeAt(i);
			if (97 <= eev && eev <= 122 || 48 <= eev && eev <= 57) {

			}
			else if (eev === 45) {
				
			}
			else {
				$("#alert-div-inputshop-slug-english").show();
				$("#inputslugshop").addClass("inputshopempty");
				checks = false;
			}
		}
	}
	return checks;
}

clickOnSubmit = function () {
	$("#alert-div-inputshop-img-empty").hide();
	$("#alert-div-inputshop-rules-disagree").hide();
	$("#alert-div-inputshop-week-holidays-all").hide();
	var comp = checkFormEmpties();
    if (!comp) {
		$("html, body").animate({ 
            scrollTop: 220
		}, "slow");
		$(".submit-shop-btn").removeClass("send-button-disabled disabled");
        return false;
	}
	else {
		return true;
	}
}
clickOnEdit = function () {
	$("#alert-div-inputshop-img-empty").hide();
	$("#alert-div-inputshop-week-holidays-all").hide();
	var comp = checkFormEmptiesForEditShop();
	if (!comp) {
		$("html, body").animate({ 
			scrollTop: 220
		}, "slow");
		$(".edit-shop-btn").removeClass("send-button-disabled disabled");
		return false;
	}
	else {
		return true;
	}
}
setSubmarketAndHolidays = function () {
	submarkets_List= '';
	var sublist = [];
	var submarkets = $("#select_cat_chosen .chosen-choices .search-choice").find('li');
	for (var i = 0; i<$("#select_cat_chosen .chosen-choices .search-choice").length; i++) 
		{
			sublist[i] = submarkets.prevObject[i].innerText;
		}
	var eachoption = [];
	for (var i = 0; i<$("#select-cat option").length; i++) 
		{
			eachoption = $("#select-cat option")[i].text;
			for (var j = 0; j<$("#select_cat_chosen .chosen-choices .search-choice").length; j++) {
			if (sublist[j] == eachoption ) {
				submarkets_List += $("#select-cat option")[i].value + '~';
				break;
			}
		}
	}

	if (submarkets_List.length > 0)
	{
		submarkets_List = submarkets_List.substring(0, submarkets_List.length - 1);
	}
	else {
		for(var i=0; i<$(".submarket-shop :selected").length; i++) {
			submarkets_List += $(".submarket-shop :selected")[i].value + '~';
		}
		if (submarkets_List.length > 0)
		{
			submarkets_List = submarkets_List.substring(0, submarkets_List.length - 1);
		}
	}
	holidaysString = '';
	if ($("#SATCheck").is(":checked")) {
		holidaysString += '0-';
	}
	if ($("#SUNCheck").is(":checked")) {
		holidaysString += '1-';
	}
	if ($("#MONCheck").is(":checked")) {
		holidaysString += '2-';
	}
	if ($("#TUECheck").is(":checked")) {
		holidaysString += '3-';
	}
	if ($("#WEDCheck").is(":checked")) {
		holidaysString += '4-';
	}
	if ($("#THUCheck").is(":checked")) {
		holidaysString += '5-';
	}
	if ($("#FRICheck").is(":checked")) {
		holidaysString += '6-';
	}
	if(holidaysString == '') {
		holidaysString = 'null';
	}
}
$(".submit-shop-btn").on("click", function () {
	$(".submit-shop-btn").addClass("send-button-disabled disabled");
	setSubmarketAndHolidays();
	return checkProfileInfo();
})
$(".edit-shop-btn").on("click", function () {
	$(".edit-shop-btn").addClass("send-button-disabled disabled");
	setSubmarketAndHolidays();
	return checkProfileInfo();
})

$(".scroll-down-btn").click(function () {
	var modalHeight = $(".modal-body").height();
	$(".modal, .modal-dialog").animate({ 
		scrollTop: modalHeight
	}, "slow");
})

$(".modal").scroll(function () {
	var ScrollPosition = $(".modal-open").scrollTop();
	$(".scroll-down-btn").show();
})

$(function () {
	$('[data-toggle="tooltip"]').tooltip();
  })

$(".input-pic-file").on("change", function () {
	$(".choose-pic-input-name").prop('placeholder', $(this).val());
})