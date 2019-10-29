//const path = require('path')
//const {ipcRenderer} = require('electron')
//const tooltip = require('electron-tooltip')
//const mime = require('mime')
//const csvJson = require('csvtojson')


const selectPattern = document.querySelector('.dropdown-menu')
const selectDirBtn = document.getElementById('select-directory')
const uploadFile = document.getElementById('upload-file')
const runPattern = document.getElementById('run-algorithm')
const runPattern1 = document.getElementById('run-algorithm1')

const msgLabel = document.getElementById('show-message')

let gradualEP = false
let file1 = ''
let file2 = ''

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

//----------------------------------------------------------------------------


selectPattern.addEventListener('click', (event) => {
    if(event.target.dataset.value){
      document.getElementById('pattern-type').innerHTML = `${event.target.dataset.value} Patterns`
      //if (!gradualEP){
      /*gradualEP = false
      msgLabel.innerHTML = ''
      closeResultContent()
      closeProgress()
      closeSpecifications()*/
      //}
      var txt = `${event.target.dataset.value} Patterns`
      console.log(txt)
    }
  })

runPattern1.addEventListener('click', function() {
    console.log("added click event")
});

/*runPattern1.onclick = function(){
    console.log("another added click event")
}*/