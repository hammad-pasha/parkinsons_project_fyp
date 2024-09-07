$(document).ready(function() {

    $(".ap").on('click', function() {
        var arr = [];
        var $row = $(this).closest("tr").find("td").each(function() {
            arr.push($(this).text());
        });

        myVar = arr[1];
        let user = {
            name: arr[0]
        }
        const request = new XMLHttpRequest()
        request.open('POST', `/addappointment/${JSON.stringify(user)}`)

        request.onload = () => {
            const flaskMessage = request.responseText
            console.log(flaskMessage)
        }
        request.send();
        alert("Appointment Added Successfully");
        window.location.reload();
    });



    $(".parpresc").on('click', function() {
        var arr = [];
        var $row = $(this).closest("tr").find("td").each(function() {
            arr.push($(this).text());
        });
         console.log($row)
        console.log(arr[1]);
        console.log(arr);
        myVar = arr[1];
        let user = {
            name: arr[1]
        }

        const request = new XMLHttpRequest()
        request.open('POST', `/makeprescription/${JSON.stringify(user)}`)

        request.onload = () => {
            const flaskMessage = request.responseText
            console.log(flaskMessage)
        }
        request.send();

        location.href = "pres"

    });


    $(".paraccep").on('click', function() {
        var arr = [];
        var $row = $(this).closest("tr").find("td").each(function() {
            arr.push($(this).text());
        });
         console.log($row)
        console.log(arr[1]);
        console.log(arr);
        myVar = arr[1];
        let user = {
            name: arr[1],
            email: arr[2]
        }

        const request = new XMLHttpRequest()
        request.open('POST', `/accept/${JSON.stringify(user)}`)

        request.onload = () => {
            const flaskMessage = request.responseText
            // window.location.reload();
            console.log(flaskMessage)
        }
        request.send();
        window.location.reload();



    });








    $(".subm").on('click', function() {
        var arr = [];
        var $row = $(this).closest("tr").find("td").each(function() {
            console.log("This is the text",$(this).text())
            arr.push($(this).text());
        });
         console.log($row)
        console.log(arr[1]);
        console.log(arr);
        myVar = arr[1];
        let user = {
            mr: arr[1]
        }
        const request = new XMLHttpRequest()
        request.open('POST', `/appointmentdelete/${JSON.stringify(user)}`)

        request.onload = () => {
            const flaskMessage = request.responseText
            console.log(flaskMessage)
        }
        request.send();

    });





    $(".docdel").on('click', function() {
        var arr = [];
        var $row = $(this).closest("tr").find("td").each(function() {
            arr.push($(this).text());
        });
        console.log(arr[1]);
        console.log(arr);
        myVar = arr[1];
        let user = {
            id: arr[0]
        }
        const request = new XMLHttpRequest()
        request.open('POST', `/docdelete/${JSON.stringify(user)}`)

        request.onload = () => {
            const flaskMessage = request.responseText
            window.location.reload();
            console.log(flaskMessage)
        }
        request.send();


    });





    $(".pardel").on('click', function() {
        var arr = [];
        var $row = $(this).closest("tr").find("td").each(function() {
            arr.push($(this).text());
        });
        console.log(arr[1]);
        console.log(arr);
        myVar = arr[1];
        let user = {
            name: arr[1],
            email: arr[2]
        }
        const request = new XMLHttpRequest()
        request.open('POST', `/reject/${JSON.stringify(user)}`)

        request.onload = () => {
            const flaskMessage = request.responseText
            window.location.reload();
            console.log(flaskMessage)
        }
        request.send();


    });






});



let camera_button = document.querySelector("#start-camera");
let video = document.querySelector("#video");
let start_button = document.querySelector("#start-record");
let stop_button = document.querySelector("#stop-record");
let download_link = document.querySelector("#download-video");

let camera_stream = null;
let media_recorder = null;
let blobs_recorded = [];

camera_button.addEventListener('click', async function() {
    camera_stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    video.srcObject = camera_stream;
});

start_button.addEventListener('click', function() {
    // set MIME type of recording as video/webm
    media_recorder = new MediaRecorder(camera_stream, { mimeType: 'video/webm' });

    // event : new recorded video blob available 
    media_recorder.addEventListener('dataavailable', function(e) {
        blobs_recorded.push(e.data);
    });

    // event : recording stopped & all blobs sent
    media_recorder.addEventListener('stop', function() {
        // create local object URL from the recorded video blobs
        let video_local = URL.createObjectURL(new Blob(blobs_recorded, { type: 'video/webm' }));
        download_link.href = video_local;
        let arr = String(download_link.href);
        let video_link = arr.split('blob:')[1]

        console.log(video_link)


        const UR = '/participantvideo'
        const xhr = new XMLHttpRequest();
        sender = JSON.stringify(video_link.toString())
        xhr.open('POST', UR);
        xhr.send(sender);
    });

    // start recording with each recorded blob having 1 second video
    media_recorder.start(1000);

});

stop_button.addEventListener('click', function() {
    media_recorder.stop();
});

function fun() {
    var node = document.getElementById('kk')
    if (node.style.visibility == 'hidden') {
        node.style.visibility = 'visible';
    } else {
        node.style.visibility = 'hidden';
    }
}


function func_2() {
    var node = document.getElementById('ppf')
    if (node.style.visibility == 'hidden') {
        node.style.visibility = 'visible';
    } else {
        node.style.visibility = 'hidden';
    }
}