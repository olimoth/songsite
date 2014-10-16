$(document).ready(function() {
    console.log("document ready");
    $("#songForm").submit(function(e){ return false; });
    $("#schemeHelp").popover({
        placement: "auto left",
        html: true,
        trigger: "focus",
    });
    $(".syllable").addClass("btn-primary");
    $(".rhyme").addClass("btn-info");
});

function showSong(song) {
    $("#songDiv").text("");
    $.each(song.songlines, function(i, line) {
        $("#songDiv").append(line);
        $("#songDiv").append("<br />");
    });
}

function getSong() {
    maxSyllables = $("#maxSyllables").val();
    minSyllables = $("#minSyllables").val();
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
