var express = require('express');
var router = express.Router();
var spawn = require('child_process').spawn

/* GET crossing csv files */
router.get('/', function(req, res, next) {
  res.render('crossing', { title: 'fuzztx' });
});

router.post('/runPython', function(req, res){
  console.log("working");
  //console.log(req.body.data[0]);
  res.send("ok");
  /*var py_req = req.body.data
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
  })*/

});

module.exports = router;