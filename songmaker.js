$(document).ready(function() {
    console.log("document ready");
    $("#songForm").submit(function(e){ return false; });
    $("#schemeHelp").popover({
        placement: "right",
        html: true,
        trigger: "focus",
    });
    $("#schemeText").tooltip({
        html: true,
    });
    $(".min").addClass("btn-info");
    $(".max").addClass("btn-warning");
    $(".syllable").addClass("btn-primary");
    $(".rhyme").addClass("btn-info");
    $("#minSyllableSlider").change(function() {
        $("#minSyllableCounter").text($(this).val());
    });
    $("#maxSyllableSlider").change(function() {
        $("#maxSyllableCounter").text($(this).val());
    });
});


function showSong(song) {
    $("#songDiv").text("");
    $.each(song.songlines, function(i, line) {
        $("#songDiv").append(line);
        $("#songDiv").append("<br />");
    });
    window.scrollTo(0, $("#songDiv").offset().top);
}

function getMinSyllables() {
    return String.trim($("#minSyllableButtonGroup > .btn.active").text());
}

function getMaxSyllables() {
    return String.trim($("#maxSyllableButtonGroup > .btn.active").text());
}

function getSong() {
    minSyllables = getMinSyllables(); 
    maxSyllables = getMaxSyllables();
    scheme = $("#schemeText").val();
    $.ajax({
        type: "GET",
        url: "http://176.227.202.176:5000/song", 
        data: {
            "minSyllables": minSyllables,
            "maxSyllables": maxSyllables,
            "scheme": scheme,
        },
        success: showSong
  });
}

function createLimerick() {
    $("#schemeText").val("8a,8a,5b,5b,8a");
}

function createSonnet() {
    $("#schemeText").val("10a,10b,10b,10a,10a,10b,10b,10a,10c,10d,10e,10c,10d,10e");
}

var scheme = '';    

function addSyllable(num) {
    console.log('adding num: ' + num);
    scheme += num;
    $(".rhyme").attr("disabled", false);
    $(".syllable").attr("disabled", true);
}

function addRhyme(rhyme) {
    console.log('adding rhyme: ' + rhyme);
    scheme += rhyme;
    updateSchemeText();
    $(".syllable").attr("disabled", false);
    $(".rhyme").attr("disabled", true);
}

function updateSchemeText() {
    scheme += ',';
    $("#schemeText").val(scheme);
}

function clearScheme() {
    scheme = '';
    $("#schemeText").val("");
}
