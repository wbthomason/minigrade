var tests = 0;
var successes = 0;
var failures = 0;

function changeBar(done, total) {
    var width = ((done/total)*100).toString() + "%";
    $("#progressbar").width(width);
    $("#progamt").text(width);
}

function grade(assignment, repo) {
    var elems = '<h2> Grading ' + assignment.toString() + ' from ' + repo.toString() +' </h2>\n' + 
    '<h3 id="pbar"> Progress: </h3>\n' + '<div id="progress">\n' + '<div id="progressbar"><span id="progamt">0%</span></div>\n' +
    '</div>\n' + '<h3> Raw output: </h3>\n' + '<pre> <code id="routc"></code></pre>\n' +
    '<h3> Test Results: </h3>\n' + '<table id="tresults" style="width:100%">\n' +
    '<tr style="text-align:center">\n' + '<td><h4>Test:</h4></td>\n' + '<td><h4>Result:</h4></td>\n' +
    '</tr>\n' + '</table>\n';
    $("#grade-results").append(elems);
    var source = new EventSource('/grade/?assign='+assignment+'&repo='+repo);
    var namepat = /tn: ([\S\s]+) ([\d]+)/;
    var respat  = /tr: (Pass|Fail) ([\d]+)/;
    source.onmessage = function(event) { 
        var chunks = event.data.split(" ");
        if (chunks[0] == 'done') { 
            source.close(); 
            $("#pbar").text("Overall Tests Passed:");
            changeBar(successes, tests);
        } 
        else if (chunks[0] == 'tn:') { 
            var name = event.data.match(namepat);
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
         else {
            alert("I don't know what this is: " + event.data);
         } 
    };
    $(window).bind("beforeunload", function() { source.close(); });
}