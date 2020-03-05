Dropzone.autoDiscover = false;

const uploads = document.getElementById('uploads')
const crossFiles = document.getElementById('cross-files')

function setupDropzone(){
    var myDropzone = new Dropzone(uploads, {
        url: "/x/upload",
        acceptedFiles: 'text/csv',
        maxFilesize: 100
    });
}

setupDropzone()


crossFiles.addEventListener('click', (event) => {
    python_path = '../public/python_modules/src/tx_csv.py'
    req = [python_path]
    runPythonCode(req)
});


function runPythonCode(request){
    var payload = JSON.stringify({data: request})
    console.log("sending Python request")
    var x = new XMLHttpRequest();
    x.onreadystatechange = function(){
      if( x.status === 200 && x.readyState === 4) {
        try{
            // Optional callback for when request completes
            var msg = JSON.parse(x.responseText);
            console.log(msg);
    
            if (msg.success == 1){
                //document.getElementById('text-result').innerHTML = `${msg.pyload}`
                //showResultContent()
                console.log(msg.pyload)
            }else if (msg.success == 0){
                //msgLabel.innerHTML = '<p>Sorry, an error occured. Check console for more details</p>'
                console.log(msg.pyload)
                alert(msg.pyload)
            }
            //closeProgress()
        }catch(err){
            var blob = new Blob([x.response], {type: 'text/csv'});
            console.log(blob);
            let a = document.createElement("a");
            a.style = "display: none";
            document.body.appendChild(a);
            let url = window.URL.createObjectURL(blob);
            a.href = url;
            a.download = 'x_data.csv';
            a.click();
            window.URL.revokeObjectURL(url);
        }
      }
    }
    x.open('POST', '/x/runPython', true);
    x.setRequestHeader("Content-Type", "application/json; charset=UTF-8");
    x.send(payload);
}
