Dropzone.autoDiscover = false;

const csvFiles = document.getElementById('csv-files')

function setupDropzone(){
    var myDropzone = new Dropzone(csvFiles, {
        url: "/x/runPython",
        acceptedFiles: 'text/csv',
        maxFilesize: 100
    });
}

setupDropzone()
