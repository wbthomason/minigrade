function changeBar(done, total) {
    var width = ((done/total)*100).toString() + "%";
    $("#progressbar").width(width);
    $("#progamt").text(width);
}

function grade(assignment, repo) {
    var elems = '<h2> Grading ' + assignment.toString() + ' from ' + repo.toString() +' </h2>\n' + 
    '<h3 id="pbar"> Progress: </h3>\n' + '<div id="progress">\n' + '<div id="progressbar"><span id="progamt">0%</span></div>\n' +
    '</div>\n' + '<input type="button" onclick="changeBar(45, 278)" value="More progress!"/>\n' +
    '<h3> Raw output: </h3>\n' + '<pre id="rout"> <code id="routc"></code></pre>\n' +
    '<h3> Test Results: </h3>\n' + '<table id="tresults" style="width:100%">\n' +
    '<tr style="text-align:center">\n' + '<td><h4>Test:</h4></td>\n' + '<td><h4>Result:</h4></td>\n' +
    '</tr>\n' + '</table>\n';
    $("#grade-results").append(elems);
    var source = new EventSource('/grade/?assign='+assignment+'&repo='+repo);
    var namepat = /tn: ([\S\s]+) ([\d]+)/;
    source.onmessage = function(event) { 
        if (event.data == 'done') { source.close(); } 
        else { 
            var name = event.data.match(namepat);
            if (name != null) {
                $("#tresults").append('<tr style="text-align: center" id="'+assignment+'-test-'+name[2]+'"><td>'+name[1]+'</td><td>Not yet run</td></tr>\n');
            }
         } 
    };
    $(window).bind("beforeunload", function() { source.close(); });
}