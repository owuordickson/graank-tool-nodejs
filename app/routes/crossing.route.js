var express = require('express');
var router = express.Router();
var spawn = require('child_process').spawn
var path = require('path');

const csvJson = require('csvtojson')

var csvFiles = [];
var csvPaths = [];

/* GET crossing csv files */
router.get('/', function(req, res, next) {
  csvFiles = [];
  csvPaths = [];
  res.render('crossing', { title: 'fuzztx' });
});

router.post('/upload', async function(req, res){
  console.log("uploading");
  not_uploaded = 1
  new_file = req.files.file;
  for(i=0; i<csvFiles.length; i++){
    if (new_file.name == csvPaths[i]){
      not_uploaded = 0
      console.log("already uploaded");
      break;
    }
  }

  if(not_uploaded == 1){
    var csv_str = new_file.data.toString();
    const jsonArray = await getJson(csv_str)
    var count = csvFiles.length
    var json_str = {file: count, data: jsonArray}

    csvFiles.push(json_str);
    csvPaths.push(new_file.name)
    console.log("uploaded");
  }
  res.send("finished uploading");
});

router.post('/runPython', function(req, res){
  console.log("working");
  if (csvFiles.length >= 2){

    //var temp = {data: [req.body.data[0], csvFiles]};
    //console.log(temp);
    var json_str = JSON.stringify(csvFiles)

    var py_req = req.body.data;
    var py_path = python_path = path.join(__dirname, py_req[0]);
    py_req = {data: [py_path, json_str]};
    //console.log(py_req);
    const pythonProcess = spawn('python3', py_req.data);//req.body.data);
    pythonProcess.stdout.on('data', async(data) => {
      try{
          // Do something with the data returned from python script
          console.log("finished working");

          var ok = 0;
          try{
            test_data = JSON.stringify(data.toString());
            ok = 1;
          }catch(err){
            ok = 0;
          }

          if (ok == 0){
            var response = JSON.stringify({success: 0, pyload: "unable to cross data"});
            res.set("Content-Type", "application/json; charset=UTF-8");
            res.send(response);
          }else if(ok == 1){
            var response = data.toString();
            res.set("Content-Type", "text/csv; charset=UTF-8");
            res.send(response);
          }
      }catch(err){
        console.log(err);
      }
    });
    pythonProcess.stderr.on('data', async(data) => {
      try{
        console.error("Error: ", data.toString());
        var response = JSON.stringify({success: 0, pyload: data.toString()});
        res.set("Content-Type", "application/json; charset=UTF-8");
        res.send(response);
      }catch(err){
        console.log(err);
      }
    })
    pythonProcess.on('close', async(code) => {
      try{
        console.log("Child exited with code ", code);
      }catch(err){
        console.log(err);
      }
    })
  }else{
    console.error("Error: Upload at least 2 different csv files");
    res.set("Content-Type", "application/json; charset=UTF-8");
    var response = JSON.stringify({success: 0, pyload: "Upload at least 2 DIFFERENT csv files"});
    res.send(response);
  }

});

function getJson(csvString){
  return csvJson({delimiter: [";",",",' ',"\t"]}).fromString(csvString)
}

module.exports = router;
