var express = require('express');
var router = express.Router();
var spawn = require('child_process').spawn
var path = require('path')

var csvFiles = [];

/* GET crossing csv files */
router.get('/', function(req, res, next) {
  res.render('crossing', { title: 'fuzztx' });
});

router.post('/upload', function(req, res){
  console.log("uploading");
  csvFiles.push(req.files.file)
  console.log("uploaded");
  res.send("finished uploading");
});

router.post('/runPython', function(req, res){
  console.log("working");
  if (csvFiles.length >= 2){

    var temp = {data: [req.body.data[0], csvFiles]}
    //console.log(temp);

    var py_req = temp.data
    var py_path = python_path = path.join(__dirname, py_req[0])
    py_req[0] = py_path
    console.log(py_path)
    /*const pythonProcess = spawn('python', req.body.data);
    pythonProcess.stdout.on('data', (data) => {
        // Do something with the data returned from python script
        console.log("finished working");
        var response = JSON.stringify({success: 1, pyload: data});
        res.send(response);
    });
    pythonProcess.stderr.on('data', (data) => {
      console.error("Error: ", data.toString());
      var response = JSON.stringify({success: 0, pyload: data.toString()});
      res.send(response);
    })
    pythonProcess.on('close', (code) => {
      console.log("Child exited with code ", code);
    })*/
  }else{
    console.error("Error: Upload at least 2 csv files");
    var response = JSON.stringify({success: 0, pyload: "Upload at least 2 csv files"});
    res.send(response);
  }

});

module.exports = router;
