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


  // Determines On state for "Select All" button in dashboard view
  function downloadCheck() {
    var el = document.getElementsByName("delete");
    if (el.length == 0) {
        document.getElementById("selectAll").setAttribute("disabled", true);
      }
  }


  // Handles behaviour for the "Select All" button in dashboard view
  function selectAll() {
    var el = document.getElementsByName("delete");
    var allChecked = false;
    var counter = 0;
    if (el) {
      for (var i = 0; i < el.length; i++) {
        if (el[i].checked == true){
          counter++;
          if (el.length == counter) {
            allChecked = true;
          }
        }
      }
      if (allChecked == false) {
        for (var i = 0; i < el.length; i++) {
          el[i].checked = true;
        }
      }
      if (allChecked == true) {
        for (var i = 0; i < el.length; i++) {
          el[i].checked = false;
        }
      }
    }
  check();
  }


  // Determines On state for delete/ download buttons in dashboard view and highlights relevant table rows
  function check () {
    var el = document.getElementsByName("delete");
    var disabled = true;
    for (var i = 0; i < el.length; i++) {
      var row = el[i].getAttribute("value");
      if (disabled == true) {
        document.getElementById("deletecheck").setAttribute("disabled", true);
        document.getElementById("download").setAttribute("disabled", true);
      }
      if (el[i].checked) {
        document.getElementById("deletecheck").removeAttribute("disabled");
        document.getElementById("download").removeAttribute("disabled");
        document.getElementById(row).style.backgroundColor = "#844D36";
        disabled = false;
        continue;
      }
      if (el[i].checked == false) {
        document.getElementById(row).style.backgroundColor = "";
        continue;
      }
    }
  }


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


  // Disables submit buttons after being clicked. Prevents submitting form multiple times.
  function disableBtn() {setTimeout(function() {
    var btn = document.getElementsByClassName("btn");
    for (var i = 0; i < btn.length; i++) {
      btn[i].setAttribute("disabled", true);
    }
  },0);
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