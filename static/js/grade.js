var tests = 0;
var successes = 0;
var failures = 0;

var persona_in = document.getElementById('persona_in');
if (persona_in) {
  persona_in.onclick = function() { navigator.id.request(); };
}
var currentUser = null;

$.ajax({
  type: 'GET',
  url: '/auth/login',
  async: false,
  success: function(res, status, xhr) {
    currentUser = res;
  },
  error: function(xhr, status, err) {
    alert("Could not reach server!");
  }
});

navigator.id.watch({
  loggedInUser: currentUser,
  onlogin: function(assertion) {
    $.ajax({ 
      type: 'POST',
      url: '/auth/login', // This is a URL on your website.
      data: {assertion: assertion},
      success: function(res, status, xhr) {
        $("#persona_in").click(function() { navigator.id.logout(); });
        $("#persona_in").val("Log out");
        $("#persona_email").text(res);
      },
      error: function(xhr, status, err) {
        navigator.id.logout();
        alert("Login failure: " + err);
      }
    });
  },
  onlogout: function() {
    $.ajax({
      type: 'POST',
      url: '/auth/logout', // This is a URL on your website.
      success: function(res, status, xhr) { 
          $("#persona_in").click(function() { navigator.id.request(); });
          $("#persona_in").val("Log in");
          $("#persona_email").text("Not logged in");
        },
      error: function(xhr, status, err) { alert("Logout failure: " + err); }
    });
  }
});

function changeBar(done, total) {
    var width = ((done/total)*100);
    width = (width < 100) ? width.toString() + "%" : "100%";
    $("#progressbar").width(width);
    $("#progamt").text(width);
}

function grade(assignment, repo) {
    $("#grade-results").empty();
    tests = 0;
    successes = 0;
    failures = 0;
    old_tests = 1;
    var elems = '<h2 id="subj"> Grading ' + assignment.toString() + ' from ' + repo.toString() +' </h2>\n' + 
    '<h3 id="pbar"> Progress: </h3>\n' + '<div id="progress">\n' + '<div id="progressbar"><span id="progamt">0%</span></div>\n' +
    '</div>\n' + '<h3> Raw output: </h3>\n' + '<pre> <code id="routc"></code></pre>\n' +
    '<h3> Test Results: </h3>\n' + '<table id="tresults" style="width:100%">\n' +
    '<tr style="text-align:center">\n' + '<td><h4>Test:</h4></td>\n' + '<td><h4>Result:</h4></td>\n' +
    '</tr>\n' + '</table>\n';
    $("#grade-results").append(elems);
    var source = new EventSource('/grade/?assign='+assignment+'&repo='+repo);
    var nampat = /tn: ([\S\s]+) ([\d]+)/;
    var respat = /tr: (Pass|Fail) ([\d]+)/;
    var invpat = /inv: ([\S\s]+)/
    source.onmessage = function(event) { 
        var chunks = event.data.split(" ");
        if (chunks[0] == 'done') { 
            source.close(); 
            $("#pbar").text("Overall Tests Passed:");
            changeBar(successes, tests);
        } 
        else if (chunks[0] == 'tn:') { 
            var name = event.data.match(nampat);
            if (name != null) {
                $("#tresults").append('<tr style="text-align: center" id="'+assignment+'-test-'+name[2]+'"><td>'+name[1]+'</td><td>Not yet run</td></tr>\n');
                tests += 1;
            }
            else {
                $("#tresults").append('<tr style="text-align: center"><td>Error: Malformed Data</td><td>Please contact admin.</td></tr>\n');
            }
         }
         else if (chunks[0] == 'tr:') {
            var result = event.data.match(respat);
            if (result != null) {
                $('#'+assignment+'-test-'+result[2]).children().eq(1).text(result[1]);
                if (result[1] == "Pass") {
                    successes += 1;
                }
                else {
                    failures += 1;
                }
                changeBar(successes+failures, tests);
            }
         }
         else if (chunks[0] == 'raw:') {
            $("#routc").append(chunks.slice(1).join(" ") + "\n");
         }
         else if (chunks[0] == 'inv:') {
            var err = event.data.match(invpat);
            if (err != null) {
                $("#subj").text(err[1]);
            }
            source.close();
         }
         else if(chunks[0] == 'nextpast') {
            $("#past-results").append('<h3> Previous Test: ' + old_tests + '</h3>\n');
            old_tests += 1;
         }
         else if(chunks[0] == 'past:') {
            $("#past-results").append('<p>' + chunks.slice(1).join(" ") + '</p>\n');
         }
         else {
            alert("I don't know what this is: " + event.data);

         } 
    };
    //$(window).bind("beforeunload", function() { source.close(); });
}
