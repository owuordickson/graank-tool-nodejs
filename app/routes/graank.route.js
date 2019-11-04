var express = require('express');
var router = express.Router();
var spawn = require('child_process').spawn
var path = require('path')

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('graank', { title: 'graank' });
});

router.post('/runPython', function(req, res){
    console.log("working");
    console.log(req.body.data[2]);

    var py_req = req.body.data
    var py_path = python_path = path.join(__dirname, py_req[0])
    py_req[0] = py_path
    const pythonProcess = spawn('python', req.body.data);
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
    })

});

module.exports = router;
