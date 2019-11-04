//To be ignored because Browserify creates the bundle.js

const fileDialog = require('file-dialog')
//const tooltip = require('electron-tooltip')
const csvJson = require('csvtojson')

const selectPattern = document.querySelector('.dropdown-menu')
const selectDirBtn = document.getElementById('select-directory')
const uploadFile = document.getElementById('upload-file')
const runPattern1 = document.getElementById('run-algorithm1')
const runPattern2 = document.getElementById('run-algorithm2')

const msgLabel = document.getElementById('show-message')

let gradualEP = false
let file1 = ''
let file2 = ''
var csv_data = ''

/*tooltip({
    //
})*/
// ----------------------- Show main content -----------------------------

function showMainContent(){
  document.querySelector('.grid-content-right').classList.add('is-shown')
  resultView = document.querySelector('.grid-content-left.is-shown')
  if (resultView) resultView.classList.remove('is-shown')
  console.log("display landing page")
}

showMainContent()

//-------------------------- get file path -------------------------------------


selectDirBtn.addEventListener('click', (event) => {
  //ipcRenderer.send('open-file-dialog')
  uploadFile.disabled = true
  fileDialog({ accept: '.csv' })
    .then(file => {
      selectDirBtn.value = file[0].name

        var reader = new FileReader()
        reader.onload = function(){
          csv_data = reader.result
          uploadFile.disabled = false
          //console.log(csv_data)

          if (!gradualEP){
            msgLabel.innerHTML = ''
            closeResultContent()
            closeProgress()
            closeSpecifications()
          }
        }
        reader.readAsBinaryString(file[0])
    })
})

/*ipcRenderer.on('selected-directory', (event, path) => {
  selectDirBtn.value = `${path}`
  if (!gradualEP){
    msgLabel.innerHTML = ''
    closeResultContent()
    closeProgress()
    closeSpecifications()
  }
})*/


//----------------------------------------------------------------------------


selectPattern.addEventListener('click', (event) => {
    if(event.target.dataset.value){
      document.getElementById('pattern-type').innerHTML = `${event.target.dataset.value} Patterns`
      //if (!gradualEP){
      gradualEP = false
      msgLabel.innerHTML = ''
      closeResultContent()
      closeProgress()
      closeSpecifications()
      //}
      //var txt = `${event.target.dataset.value} Patterns`
      //console.log(txt)
    }
  })

uploadFile.addEventListener('click', (event) => {
  msgLabel.innerHTML = ''
  if (gradualEP){
    showProgress()
    file2 = csv_data
    msgLabel.innerHTML = '<p style="color: green;">csv file verified &#128077</p>'
    closeProgress()
  }else{
    closeResultContent()
    showSpecifications(csv_data)
  }
})

runPattern2.addEventListener('click', (event) => {
  file = csv_data//selectDirBtn.value
  ref_col = document.getElementById('input-ref2').value
  min_sup = document.getElementById('input-sup2').value
  min_rep = document.getElementById('input-rep2').value

  patternType = document.getElementById('pattern-type').innerHTML
  if(patternType === 'Emerging Patterns'){
    type = 12
  }else{
    type = 2
  }
  showProgress()
  //python_path = path.join(__dirname, '../python_modules/src/border_tgraank.py')
  python_path = '../public/python_modules/src/border_tgraank.py'
  python_file = 'border_tgraank.py'
  req = [python_path, type, file, (ref_col-1), min_sup, min_rep]
  //console.log(req)
  runPythonCode(req)
})

runPattern1.addEventListener('click', (event) => {

  file = csv_data//selectDirBtn.value
  min_sup = document.getElementById('input-sup1').value

  patternType = document.getElementById('pattern-type').innerHTML
  if(patternType === 'Emerging Patterns'){
    type = 11
    if (file1 != ''){
      if (file2 != '' && file1 != file2){
        showProgress()
        validateTimeColumn(file2)
        .then((hasTime) => {
          if (hasTime == 404){
            msgLabel.innerHTML = '<p>sorry, an error occured</p>'
            closeProgress()
            closeSpecifications()
          }
          else if (hasTime){
            file2 = ''
            msg = 'columns in csv file not matching previous file...<br>upload another file'
            requestFile(msg)
          }else {
            //python_path = path.join(__dirname, '../python_modules/src/graank.py')
            python_path = '../public/python_modules/src/graank.py'
            python_file = 'graank.py'
            req = [python_path, type, file1, file2, min_sup]
            runPythonCode(req)
            file1 = ''
            file2 = ''
            gradualEP = false
          }
        })
        .catch((err) => {
          file2 = ''
          msg = 'sorry system error...upload another file'
          requestFile(msg)
        })
      }else {
        file2 = ''
        msg = 'file is blank or may be similar to previous file...<br>upload another file'
        requestFile(msg)
      }
    }else{
      file1 = file
      file2 = ''
      msg = 'Please upload 2nd file'
      requestFile(msg)
      gradualEP = true
    }
  }else{
    type = 1
    showProgress()
    //python_path = path.join(__dirname, '../python_modules/src/graank.py')
    python_path = '../public/python_modules/src/graank.py'
    python_file = 'graank.py'
    req = [python_path, type, file, min_sup]
    runPythonCode(req)
  }
})

// --------------------- Views ----------------------------------


function showResultContent(){
  mainView = document.querySelector('.grid-content-right.is-shown')
  resultView = document.querySelector('.grid-content-left')
  if (mainView){
    mainView.classList.remove('is-shown')
    mainView.classList.add('adjust')
    resultView.classList.add('is-shown')
  }
}

function showProgress(){
  progressView = document.querySelector('.graank-progress.is-shown')
  if (!progressView){
    progressView = document.querySelector('.graank-progress')
    progressView.classList.add('is-shown')

    msgLabel.innerHTML = ''
    responseView = document.querySelector('.graank-response.is-shown')
    if(responseView){
      responseView.classList.remove('is-shown')
    }
  }
}

function showSpecifications(file){
  showProgress()
  
  validateTimeColumn(file)
  .then((isValid) => {

    if (isValid == 404){
      msgLabel.innerHTML = '<p>sorry, an error occured</p>'
      closeSpecifications()
    }
    else if (isValid){
      msgLabel.innerHTML = '<p style="color: green;">csv file verified &#128077</p>'
      showTemporalSpecifications()
    }else {
      msgLabel.innerHTML = '<p style="color: green;">csv file verified &#128077</p>'
      showGradualSpecifications()
    }
    closeProgress()
  })
  .catch((err) => {
    console.error(err)
    msgLabel.innerHTML = '<p>sorry, an error occured</p>'
    closeProgress()
    closeSpecifications()
  })  
}

function showGradualSpecifications(){
  specsGradual = document.querySelector('.grid-specs-gradual-group.is-shown')
  specsTemporal = document.querySelector('.grid-specs-temporal-group.is-shown')
  if(!specsGradual){
    specsGradual = document.querySelector('.grid-specs-gradual-group')
    specsGradual.classList.add('is-shown')
  }
  if(specsTemporal){
    specsTemporal.classList.remove('is-shown')
  }
}

function showTemporalSpecifications(){
  specsGradual = document.querySelector('.grid-specs-gradual-group.is-shown')
  specsTemporal = document.querySelector('.grid-specs-temporal-group.is-shown')
  if(!specsTemporal){
    specsTemporal = document.querySelector('.grid-specs-temporal-group')
    specsTemporal.classList.add('is-shown')
  }
  if(specsGradual){
    specsGradual.classList.remove('is-shown')
  }
}

function closeResultContent(){
  resultView = document.querySelector('.grid-content-left.is-shown')
  if (resultView){
    resultView.classList.remove('is-shown')

    mainView = document.querySelector('.grid-content-right.adjust')
    if(mainView){
      mainView.classList.remove('adjust')
      mainView.classList.add('is-shown')
      }
    }
  }

function closeProgress(){
    progressView = document.querySelector('.graank-progress.is-shown')
    if (progressView){
      progressView.classList.remove('is-shown')

      responseView = document.querySelector('.graank-response')
      if(responseView){
        responseView.classList.add('is-shown')
      }
    }
  }

function closeSpecifications(){

    specsGradual = document.querySelector('.grid-specs-gradual-group.is-shown')
    specsTemporal = document.querySelector('.grid-specs-temporal-group.is-shown')

    if(specsGradual){
      specsGradual.classList.remove('is-shown')
    }
    if(specsTemporal){
      specsTemporal.classList.remove('is-shown')
    }

  }


// ----------------------- upload another file ---------------------------------

function requestFile(msg){
  msgLabel.innerHTML = '<p>' + msg + '</p>'
  selectDirBtn.value = ''
  closeProgress()
}

// ----------------------- main tasks ------------------------------------------

async function validateTimeColumn(csvFile){
    const dateReg = /(0?[1-9]|[12]\d|30|31)[^\w\d\r\n:](0?[1-9]|1[0-2])[^\w\d\r\n:](\d{4}|\d{2})/
    const time12Reg = /^(?:1[0-2]|0?[0-9]):[0-5][0-9]:[0-5][0-9]$/
    const time24Reg = /^(?:2[0-3]|[01]?[0-9]):[0-5][0-9]:[0-5][0-9]$/
    const jsonArray = await getJson(csvFile)
    csv_data = JSON.stringify(jsonArray)
    //console.log(jsonArray[0])

    try {
      for (key in jsonArray[0]){
        if (jsonArray[0][key].match(dateReg) || jsonArray[0][key].match(time12Reg) || jsonArray[0][key].match(time24Reg)){
          //console.log(jsonArray[0][key])
          return true
        }
      }
      //throw new Error("")
      return false
    }catch (err){
      console.error("Error: ", err.toString())
      msgLabel.innerHTML = '<p>sorry, an error occured</p>'
      return 404
    }
  }

function getJson(csvString){
  return csvJson({delimiter: [";",",",' ',"\t"]}).fromString(csvString)
}

function runPythonCode(request){
  var payload = JSON.stringify({data: request})
  console.log("sending Python request")
  var x = new XMLHttpRequest();
  x.onreadystatechange = function(){
    if( x.status === 200 && x.readyState === 4) {
      // Optional callback for when request completes
      var msg = JSON.parse(x.responseText);
      console.log(msg);

      if (msg.success == 1){
        document.getElementById('text-result').innerHTML = `${msg.pyload}`
        showResultContent()
      }else if (msg.success == 0){
        msgLabel.innerHTML = '<p>Sorry, an error occured. Check console for more details</p>'
        console.log(msg.pyload)
      }
      closeProgress()
    }
  }
  x.open('POST', '/runPython', true);
  x.setRequestHeader("Content-Type", "application/json; charset=UTF-8");
  x.send(payload);

  //const func = () => fetch(path.join(__dirname, '/runPython'));
  //console.log(func)
  /*const pythonProcess = spawn('python', request)
  pythonProcess.stdout.on('data', (data) => {
      // Do something with the data returned from python script
      document.getElementById('text-result').innerHTML = `${data}`
      showResultContent()
      closeProgress()
  })
  pythonProcess.stderr.on('data', (data) => {
    console.error("Error: ", data.toString())
    msgLabel.innerHTML = '<p>sorry, an error occured</p><br><p>check console for more details</p>'
    closeProgress()
  })
  pythonProcess.on('close', (code) => {
    console.log("Child exited with code ", code)
  })*/
}