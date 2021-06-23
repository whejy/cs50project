  document.addEventListener('DOMContentLoaded', function() {
    textgrow();
    toggle();
    selectcheck();
    fontcheck();
  });


  // Font selector which also adds hidden value to be submitted with "add entry" and "update" buttons
  var changeFont = function(font){
      document.getElementById("paper").style.fontFamily = font.value;
      var el = document.getElementById("fontSelector");
      el.setAttribute("value", font.value);
      };


  // Background selector which also adds hidden value to be submitted with "add entry" and "update" buttons
  var changePad = function(pad){
      document.getElementById("paper").style.backgroundImage = pad.value;
      var el = document.getElementById("padSelector");
      el.setAttribute("value", pad.value);
  };


  // Checks current background image and preselects the relevant option in Selection Box
  function selectcheck () {
    var sel = document.getElementById('padCheck');
    var el = document.getElementById('paper');
    if (el) {
      var str = el.getAttribute('style');
      var img2 = str.split("image: ")[1];
      var img = img2.split(";")[0];
      var opts = sel.options;
        for (let j = 0; j < opts.length; j++) {
          if (opts[j].value == img) {
            sel.selectedIndex = j;
            break;
          }
        }
    }
  }


  // Checks current font and preselects the correct option in Selection Box
  function fontcheck () {
    var sel = document.getElementById('fontCheck');
    var el = document.getElementById('paper');
    if (el) {
      var str = el.getAttribute('style');
      var img2 = str.split("family: ")[1];
      var img = img2.split(";")[0];
      var opts = sel.options;
        for (let j = 0; j < opts.length; j++) {
          if (opts[j].value == img) {
            sel.selectedIndex = j;
            break;
          }
        }
    }
  }


  // Grows textbox to fit content
  function textgrow () {
    const growers = document.querySelectorAll(".grow-wrap");
      growers.forEach((grower) => {
        const textarea = grower.querySelector("textarea");
        textarea.addEventListener("input", () => {
        grower.dataset.replicatedValue = textarea.value;
        });
        textarea.addEventListener("focus", () => {
        grower.dataset.replicatedValue = textarea.value;
        });
    });
  }


  // Toggles active state for toggle bar links
  function toggle() {
    $('a.active').removeClass('active');
    $('a[href="' + location.pathname + '"]').closest('a').addClass('active');
  }


  // Auto dismisses flask alert
  function dismiss() {
  $(".alert-dismissible").fadeTo(2000, 500).slideUp(500, function(){
      $(".alert-dismissible").alert('close');
  });
  }