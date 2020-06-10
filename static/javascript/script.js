const toast = document.getElementById("toast");
const toast2 = document.getElementById("toast2");

const cosNotify = document.getElementById("cosNotify");
const nluNotify = document.getElementById("nluNotify");
const scrollClass = document.getElementById("scrollClass");
const clickBtn2 = document.getElementById("clickBtn2");
const refresh2 = document.getElementById("refresh2");
const fileNamefromTable = document.getElementById("fileName");

const table = document.getElementById("table");
const tableRef = table.getElementsByTagName('tbody')[0];
const analyseBtn = document.getElementById('analyseBtn');

const categoryHere = document.getElementById('categoryHere');
const conceptHere = document.getElementById('conceptHere');
const entityHere = document.getElementById('entityHere');
const sentimentsHere = document.getElementById('sentimentsHere');
const positiveSentencesHere = document.getElementById('positiveSentencesHere');
const wordCloudHere = document.getElementById('wordCloudHere');

const uploading2 = document.getElementById("uploading2");
const uploaded2 = document.getElementById("uploaded2");
const optionals = document.getElementById('optionals');
const optional1 = document.getElementById('optional1');
const optional2 = document.getElementById('optional2');
const optional3 = document.getElementById('optional3');
const removeThis = document.getElementById('removeThis');
var file;

$(document).ready(function() {
    toast.style.display = "none";
    toast2.style.display = "none";
    refresh2.style.display = "none";
    table.style.display = "none";
    analyseBtn.style.display = "none";
    uploading2.style.display = "none";
    uploaded2.style.display = "none";
    scrollClass.style.display = "none";
    getCOSCredentials();

    clickBtn2.click();
});

var addSerialNumber = function() {
    $('table tr').each(function(index) {
        $(this).find('td:nth-child(1)').html(index);
    });
};

async function getCOSCredentials() {
    await fetch('/initCOS').then(async(response) => {
        data = await response.json();
        cosNotify.innerHTML = " ";
        cosNotify.innerHTML = data.message;
        toast.style.display = "block";

    });
}
async function getConvertedFiles() {
    tableRef.innerHTML = " ";
    refresh2.style.display = "block";
    await fetch('/getAudioFiles').then(async(response) => {
        data = await response.json();
        data.forEach(element => {
            audioPlayer = '<br/><a><audio controls> <source src="static/' +
                element.audioFile + '" type="audio/flac"> Your browser does not support the audio element. </audio></a>';
            // Insert a row in the table at the last row
            var newRow = tableRef.insertRow();

            // Insert a cell in the row at index 0
            var newCellIndex = newRow.insertCell(0);
            var newCell = newRow.insertCell(1);
            var newCell2 = newRow.insertCell(2);
            var newCell3 = newRow.insertCell(3);
            var newCell4 = newRow.insertCell(4);

            fileFormat = element.audioFile.split('.')[1];
            newCellIndex.innerHTML = "";
            newCell.innerHTML = `<a href="#" onclick="updateOptions('${element.audioFile.split('/')[1]}')"> \
                                    ${element.audioFile.split('/')[1]}</a>`;
            newCell2.innerHTML = element.fileSize;
            newCell3.innerHTML = fileFormat;

            newCell4.innerHTML = "";
            newCell4.innerHTML = `<button class="bx--btn bx--btn--ghost bx--btn--sm" onclick='deleteUploadedFile("${element.audioFile}")' type="button"> \
                            <svg focusable="false" preserveAspectRatio="xMidYMid meet" style="will-change: transform;" \
                                xmlns="http://www.w3.org/2000/svg" class="bx--btn__icon" width="16" height="16" \
                                viewBox="0 0 32 32" aria-hidden="true"> \
                                <path d="M25.7,9.3l-7-7A.91.91,0,0,0,18,2H8A2,2,0,0,0,6,4V28a2,2,0,0,0,2,2H24a2,2,0,0,0,2-2V10A.91.91,0,0,0,25.7,9.3ZM18,4.4,23.6,10H18ZM24,28H8V4h8v6a2,2,0,0,0,2,2h6Z">\
                                </path><path d="M11 19H21V21H11z"></path> </svg> </button>`;

            addSerialNumber();
        });
        table.style.display = "block";
        refresh2.style.display = "none";
    });
    var x = document.getElementById("table").rows.length;
    if (x > 1)
        table.style.display = "block";
    else
        table.style.display = "none";
}

async function analyseText() {
    uploaded2.style.display = "none";
    uploading2.style.display = "block";
    var category = document.getElementById('category');
    var concepts = document.getElementById('concepts');
    var entity = document.getElementById('entity');
    var categoryBool, conceptsBool, entityBool;
    var mydata;
    if (category.checked == true) {
        categoryBool = "True";
    } else {
        categoryBool = "False";
    }

    if (concepts.checked == true) {
        conceptsBool = "True";
    } else {
        conceptsBool = "False";
    }

    if (entity.checked == true) {
        entityBool = "True";
    } else {
        entityBool = "False";
    }

    file = fileNamefromTable.innerHTML.split('>')[1].split('<')[0];

    let options = {
        file: file,
        category: categoryBool,
        concepts: conceptsBool,
        entity: entityBool,
        sentiments: 'True',
        positiveSentences: 'True'
    };

    let formData = new FormData();
    formData.append("options", JSON.stringify(options));

    $.ajax({
        url: '/analyseText',
        type: 'POST',
        data: formData,
        cache: false,
        contentType: false,
        processData: false,
        success: function(response) {
            scrollClass.style.display = "block";
            uploading2.style.display = "none";
            uploaded2.style.display = "block";
            mydata = response;
            // scrollClass.innerHTML = '<div class="bx--tile">\<button class="bx--btn bx--btn--primary bx--btn--field" type="button" data-modal-target="#modal-pyu0ribosn">\
            //                             Download Report\
            //                             <svg focusable="false" preserveAspectRatio="xMidYMid meet" style="will-change: transform;" xmlns="http://www.w3.org/2000/svg" class="bx--btn__icon" width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">\
            //                             <path d="M7.5 11l4.1-4.4.7.7L7 13 1.6 7.3l.7-.7L6.5 11V0h1v11zM13 15v-2h1v2c0 .6-.4 1-1 1H1c-.6 0-1-.4-1-1v-2h1v2h12z"></path></svg>\
            //                             </button>\
            //                             </div>\
            //                             <br>';
            console.log(mydata);

            if (response.category == undefined && response.concepts == undefined && response.entity == undefined) {
                optional1.style.display = "none";
                optional2.style.display = "none";
                optional3.style.display = "none";
                removeThis.style.display = "none";
            } else if (response.category == undefined) {
                optional1.style.display = "none";
                optional2.style.display = "block";
                optional3.style.display = "block";
                removeThis.style.display = "block";
            } else if (response.concepts == undefined) {
                optional1.style.display = "block";
                optional2.style.display = "block";
                optional3.style.display = "none";
                removeThis.style.display = "block";
            } else if (response.entity == undefined) {
                optional1.style.display = "block";
                optional2.style.display = "none";
                optional3.style.display = "block";
                removeThis.style.display = "block";
            } else if (response.category == undefined && response.concepts == undefined) {
                optional1.style.display = "none";
                optional2.style.display = "block";
                optional3.style.display = "none";
                removeThis.style.display = "block";
            } else if (response.concepts == undefined && response.entity == undefined) {
                optional1.style.display = "block";
                optional2.style.display = "none";
                optional3.style.display = "none";
                removeThis.style.display = "block";
            } else if (response.entity == undefined && response.category == undefined) {
                optional1.style.display = "none";
                optional2.style.display = "none";
                optional3.style.display = "block";
                removeThis.style.display = "block";
            } else {
                optional1.style.display = "block";
                optional2.style.display = "block";
                optional3.style.display = "block";
                removeThis.style.display = "block";
                // optionals.style.display = "block";
                categoryHere.innerHTML = response.category.label;
                categoryHere.innerHTML += `<div class="bx--tag bx--tag--green"><span class="bx--tag__label">${response.category.score}</span> </div>`;

                conceptHere.innerHTML = `<ul>`;
                response.concepts.forEach(element => {
                    conceptHere.innerHTML += `<br>`;
                    conceptHere.innerHTML += `<li><a href='${element.dbpedia_resource}'> ${element.text} </a> <div class="bx--tag bx--tag--green"><span class="bx--tag__label">${element.relevance}</span> </div> </li>`;
                });
                conceptHere.innerHTML += `</ul>`;

                entityHere.innerHTML = `${response.entity.type}, ${response.entity.text} <div class="bx--tag bx--tag--green"><span class="bx--tag__label">${response.entity.relevance}</span> </div>`;

            }

            sentimentsHere.innerHTML = `<ul>`;
            response.sentiments.forEach(element => {
                sentimentsHere.innerHTML += `<br>`;
                if (element.sentiment == 'positive' && element.emotion == 'joy') {
                    sentimentsHere.innerHTML += `<li>${element.keyword} <div class="bx--tag bx--tag--green"><span class="bx--tag__label">${element.sentiment}</span> </div> <div class="bx--tag bx--tag--cyan"><span class="bx--tag__label">${element.emotion}</span> </div></li>`;
                } else {
                    sentimentsHere.innerHTML += `<li>${element.keyword} <div class="bx--tag bx--tag--red"><span class="bx--tag__label">${element.sentiment}</span> </div> <div class="bx--tag bx--tag--gray"><span class="bx--tag__label">${element.emotion}</span> </div></li>`;
                }
            });
            sentimentsHere.innerHTML += `</ul>`;

            positiveSentencesHere.innerHTML = `<ul>`;
            response.positiveSentences.forEach(element => {
                positiveSentencesHere.innerHTML += `<br>`;
                positiveSentencesHere.innerHTML += `<li>${element.text} <div class="bx--tag bx--tag--green"><span class="bx--tag__label">${element.score}</span> </div> </li>`;
            });
            positiveSentencesHere.innerHTML += `</ul>`;

            wordCloudHere.innerHTML = `<div class="bx--col-md-3"><div class="outside"><div class="inside"><h6> Nouns & Adjectives </h6><br> <img class="center" height="256" width="256" src="${response.wordclouds[0]}"> </div></div></div>
                <div class="bx--col-md-4"><div class="outside"><div class="inside"> <h6> Verbs </h6><br><img class="center" height="256" width="256" src="${response.wordclouds[1]}"> </div></div></div>`;
        }

    });
}

function updateOptions(fileName) {
    fileNamefromTable.innerHTML = '';
    fileNamefromTable.innerHTML = 'Selected File: <strong>' + fileName + '</strong>';
    analyseBtn.style.display = "block";
}
async function deleteUploadedFile(fileName, fileType) {
    console.log(fileName, fileType);

    await fetch(`/deleteUploadedFile?fileName=${fileName}&fileType=${fileType}`).then(async(response) => {
        data = await response.json();
        if (data.flag == 0) {
            if (fileType == 'video')
                clickBtn1.click();
            if (fileType == 'audio')
                clickBtn2.click();
        } else if (data.flag == 1) {

        }
    });
}

function printDiv() {
    var printContents = document.getElementById("scrollClass").innerHTML;
    var originalContents = document.body.innerHTML;

    document.body.innerHTML = printContents;

    window.print();

    document.body.innerHTML = originalContents;
}