
(function ($) {
    "use strict";


    /*==================================================================
    [ Focus Contact2 ]*/
    $('.input100').each(function(){
        $(this).on('blur', function(){
            if($(this).val().trim() != "") {
                $(this).addClass('has-val');
            }
            else {
                $(this).removeClass('has-val');
            }
        })    
    })
  
  
    /*==================================================================
    [ Validate ]*/
    var input = $('.validate-input .input100');

    $('.validate-form').on('submit',function(){
        var check = true;

        for(var i=0; i<input.length; i++) {
            if(validate(input[i]) == false){
                showValidate(input[i]);
                check=false;
            }
        }

        return check;
    });


    $('.validate-form .input100').each(function(){
        $(this).focus(function(){
           hideValidate(this);
        });
    });

    function validate (input) {
        if($(input).attr('type') == 'email' || $(input).attr('name') == 'email') {
            if($(input).val().trim().match(/^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{1,5}|[0-9]{1,3})(\]?)$/) == null) {
                return false;
            }
        }
        else {
            if($(input).val().trim() == ''){
                return false;
            }
        }
    }

    function showValidate(input) {
        var thisAlert = $(input).parent();

        $(thisAlert).addClass('alert-validate');
    }

    function hideValidate(input) {
        var thisAlert = $(input).parent();

        $(thisAlert).removeClass('alert-validate');
    }
    

})(jQuery);


document.querySelectorAll('.teacher, .manage').forEach(search => {
    search.addEventListener('mouseenter', function() {
        this.style.transform = 'scale(1.2)';
        this.style.boxShadow = '0px 4px 10px rgba(0, 0, 0, 0.5)';
    });
    search.addEventListener('mouseleave', function() {
        this.style.transform = 'scale(1)';
        this.style.boxShadow = '0px 4px 10px rgba(0, 0, 0, 0.5)';
    });
});

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".a-text").forEach((openButton) => {
        const popupId = openButton.id.replace("openPopup", "popup");
        const popup = document.getElementById(popupId);
        
        if (!popup) return;

        const closeButton = popup.querySelector(".close");

        openButton.addEventListener("click", () => {
            console.log("Opening:", popupId);
            popup.classList.add("show");
        });

        closeButton.addEventListener("click", () => {
            console.log("Closing:", popupId);
            popup.classList.remove("show");
        });

        window.addEventListener("click", (event) => {
            if (event.target === popup) {
                popup.classList.remove("show");
            }
        });
    });
});

// ตั้งค่า popups ทั้งหมด
// for (let i = 1; i <= 5; i++) {
//     setupPopup(`popup${i}`, `openPopup${i}`);
// }


function handleSubmit(event) {
    event.preventDefault();
    alert('Appointment Submitted Successfully!');
}
