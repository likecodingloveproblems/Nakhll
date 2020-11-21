$.fn.digits = function(){ 
    return this.each(function(){ 
        $(this).text( $(this).text().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,") ); 
    })
}
$(".numbersprice").digits();



$.fn.longtitle = function(){ 
    if($(".longtitle").text().length >= 36){
        return this.each(function(){ 
            $(this).text( $(this).text().slice(0, 36)+' ... '); 
        })
    }
}
$(".longtitle").longtitle();



$.fn.longdes = function(){ 
    if($(".longdes").text().length >= 110){
        return this.each(function(){ 
            $(this).text( $(this).text().slice(0, 110)+' ... '); 
        })
    }
}
$(".longdes").longdes();


function separateNum(value, input) {
    /* seprate number input 3 number */
    var nStr = value + '';
    nStr = nStr.replace(/\,/g, "");
    x = nStr.split('.');
    x1 = x[0];
    x2 = x.length > 1 ? '.' + x[1] : '';
    var rgx = /(\d+)(\d{3})/;
    while (rgx.test(x1)) {
        x1 = x1.replace(rgx, '$1' + ',' + '$2');
    }
    if (input !== undefined) {

        input.value = x1 + x2;
    } else {
        return x1 + x2;
    }
}



$(document).ready(function(){

    $('#new-ticket-profile').click(function(){
        $(".form-ticket").css("display", "block");
        $(".ticket-messages").css("display", "none");
    });

    var rBtnVal = 'yes';
    $('#readonlyswitchbtn').click(function(){
      if(rBtnVal == "yes"){
          $("#profile-sec input").prop("readonly", false);
          $('.selcetoption').prop("disabled", false)
          $('#readonlyswitchbtn').text("لغو");
          $("#edit-profile").css("display", "inline");
          $("#pic-profile-add").css("display", "block");
          $("#helpinputNationalCode").css("display", "block");
          $("#helpinputMobileNumber").css("display", "block");
          $("#inputprofState").attr('disabled', false).trigger("chosen:updated");
          $("#inputprofBigCity").attr('disabled', false).trigger("chosen:updated");
          $("#inputprofCity").attr('disabled', false).trigger("chosen:updated");
          rBtnVal = "no"; 
        }
        else{ 
            $("#profile-sec input").prop("readonly", true); 
            $('.selcetoption').prop("disabled", true)
            $('#readonlyswitchbtn').text("ویرایش");
            $("#edit-profile").css("display", "none");
            $("#helpinputNationalCode").css("display", "none");
            $("#helpinputMobileNumber").css("display", "none");
            $("#pic-profile-add").css("display", "none");
            $("#inputprofState").attr('disabled', true).trigger("chosen:updated");
            $("#inputprofBigCity").attr('disabled', true).trigger("chosen:updated");
            $("#inputprofCity").attr('disabled', true).trigger("chosen:updated");
          rBtnVal = "yes";
      }
    });

    $('.attr-item-price').click(function(){
        alert('با تغییر این ویژگی قیمت آن در سبد خرید شما تغییر می کند ...');
    });

 });



 $(document).ready(function(){
    var next = 1;
    var nexto = 1;

    $(".add-more").click(function(e){
        e.preventDefault();
        var addto = "#field" + next;
        var addRemove = "#field" + (next);
        next = next + 1;
        var newIn = '<input autocomplete="off" class="input form-control col-md-10 mg10" id="field' + next + '" name="field-up" type="text">';
        var newInput = $(newIn);
        var removeBtn = '<button id="remove' + (next - 1) + '" class="btn btn-danger remove-me col-md-2 mg10" >-</button></div><div id="field">';
        var removeButton = $(removeBtn);
        $(addto).after(newInput);
        $(addRemove).after(removeButton);
        $("#field" + next).attr('data-source',$(addto).attr('data-source'));
        $("#count").val(next);  
        
            $('.remove-me').click(function(e){
                e.preventDefault();
                var fieldNum = this.id.charAt(this.id.length-1);
                var fieldID = "#field" + fieldNum;
                $(this).remove();
                $(fieldID).remove();
            });
    });

    $(".add-moreo").click(function(e){
        e.preventDefault();
        var addtoo = "#fieldo" + nexto;
        var addRemoveo = "#fieldo" + (nexto);
        nexto = nexto + 1;
        var newIno = '<input autocomplete="off" class="input form-control col-md-10 mg10" id="fieldo' + nexto + '" name="field-down" type="text">';
        var newInputo = $(newIno);
        var removeBtno = '<button id="removeo' + (nexto - 1) + '" class="btn btn-danger remove-meo col-md-2 mg10" >-</button></div><div id="fieldo">';
        var removeButtono = $(removeBtno);
        $(addtoo).after(newInputo);
        $(addRemoveo).after(removeButtono);
        $("#fieldo" + nexto).attr('data-source',$(addtoo).attr('data-source'));
        $("#counto").val(nexto);  
        
            $('.remove-meo').click(function(e){
                e.preventDefault();
                var fieldNumo = this.id.charAt(this.id.length-1);
                var fieldIDo = "#fieldo" + fieldNumo;
                $(this).remove();
                $(fieldIDo).remove();
            });
    });  
    
});


$(document).on("click", ".browse", function() {
    var file = $(this).parents().find(".file");
    file.trigger("click");
  });
  $('input[type="file"]').change(function(e) {
    var fileName = e.target.files[0].name;
    $("#file").val(fileName);
  
    var reader = new FileReader();
    reader.onload = function(e) {
      // get loaded data and render thumbnail.
    //   document.getElementById("preview").src = e.target.result;
    };
    // read the image file as a data URL.
    reader.readAsDataURL(this.files[0]);
  });


  //Rating
  $('.rating input').change(function () {
      var $radio = $(this);
      $('.rating .selected').removeClass('selected');
      $radio.closest('label').addClass('selected');
  });

  checkValidChars = function (inputEL) {
      console.log(inputEL);
    var data = inputEL;
    var charcheck;
    var check = true;
    for (var i = 0; i < data.length; i++)
	{
        charcheck = data.charCodeAt(i);
		if (32 <= charcheck && charcheck <= 126) {
            // console.log(data[i] + ': ' + charcheck + ' doroste');
        }
        else if (145 <= charcheck && charcheck <= 152) {
            
        }
        else if ((1578 <= charcheck && charcheck <= 1594) || (1604 <= charcheck && charcheck <= 1608)) {
            // console.log(data[i] + ': ' + charcheck + ' doroste');
        }
        else if (1610 <= charcheck && charcheck <= 1617){

        }
        else if (1632 <= charcheck && charcheck <= 1641) {
            // console.log(data[i] + ': ' + charcheck + ' doroste');
        }
        else if (1569 <= charcheck && charcheck <= 1577) {

        }
        else if (charcheck == 10 || charcheck == 171 || charcheck == 187 || charcheck == 1548 || charcheck == 1563 || charcheck == 1567 || charcheck == 1600 || charcheck == 1601 || charcheck == 1602 || charcheck == 1662 || charcheck == 1670 || charcheck == 1688 || charcheck == 1705 || charcheck == 1711 || charcheck == 1728 || charcheck == 1740 || charcheck == 8204 || charcheck == 8221) {
            // console.log(data[i] + ': ' + charcheck + ' doroste');
        }
		else {
            check = false;
            console.log(data[i] + ': ' + charcheck + ' not valid char!');
            // break;
		}
    }
    return check;
  }

  $("input[type=number]").on("keydown", function (event) {
    if (event.which == 69)
    {
        return false;
    }
  })
//   $("input[type=number]").on("input", function () {
//     // vartextboxText = textboxText.replace(/^0+/, '');
//   })
//   $("input[type=number]").on('paste drop', function () {
//       setTimeout(function(){
//         console.log($(this));
//         var data = $(this).val();
//         console.log(data);
//         for(var i=0; i<data.length; i++)
//         {
//             var ews = data.charCodeAt(i);
//             if (ews >= 48 && ews <= 57 || ews >= 1632 && ews <= 1641) {
                
//             }
//             else {
//                 $(this).val('');
//                 return false;
//             }
//         }
//     }, 10)
//   });
  $("input[type=number]").prop('min', 0);