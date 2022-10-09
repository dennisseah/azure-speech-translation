let audioChunks = [];
let rec = undefined;
const recordBtn = document.getElementById("record");
const stopBtn = document.getElementById("stopRecord");
const ecordedAudio = document.getElementById("recordedAudio");

const handlerFunction = (stream) => {
    rec = new MediaRecorder(stream);
    rec.ondataavailable = e => {
        audioChunks.push(e.data);
        if (rec.state === "inactive") {
            const blob = new Blob(audioChunks, { type: 'audio/wav' });
            sendData(blob);
        }
    }
}

const sendData = (data) => {
    const form_data = new FormData();
    form_data.append('file', data, 'recording.wav');
    const lang = document.getElementById("language").value;

    const xhr = new XMLHttpRequest()
    xhr.open('POST', "/translate?lang=" + lang, true);
    xhr.responseType = "blob";

    xhr.onload = function () {
        if (xhr.status === 200) {
            const blob = new Blob([xhr.response], { type: 'audio/wav' });
            const objectUrl = URL.createObjectURL(blob);
            ecordedAudio.src = objectUrl;
            recordedAudio.play();
        }
    }
    xhr.send(form_data);
}

navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => { handlerFunction(stream) })

recordBtn.onclick = () => {
    recordBtn.disabled = true;
    stopBtn.disabled = false;
    audioChunks = [];
    rec.start();
}
stopBtn.onclick = () => {
    recordBtn.disabled = false;
    stopBtn.disabled = true;
    rec.stop();
}