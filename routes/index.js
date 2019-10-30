var express = require('express');
var router = express.Router();
var spawn = require('child_process').spawn

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', { title: 'graank' });
});

router.post('/runPython', function(req, res){
    //res.render('index', { title: 'graank' });
    console.log("working");
    console.log(req.body.data[1]);
  //function runPythonCode(request){
    const pythonProcess = spawn('python', req.body.data);
    pythonProcess.stdout.on('data', (data) => {
        // Do something with the data returned from python script
        //document.getElementById('text-result').innerHTML = `${data}`
        //showResultContent()
        //closeProgress()
        console.log("finished working");
        res.send(data);
    });
    pythonProcess.stderr.on('data', (data) => {
      console.error("Error: ", data.toString());
      //msgLabel.innerHTML = '<p>sorry, an error occured</p><br><p>check console for more details</p>'
      //closeProgress()
    })
    pythonProcess.on('close', (code) => {
      console.log("Child exited with code ", code);
    })
  //}
});

module.exports = router;
