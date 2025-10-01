const countElem = document.getElementById('count');
const toggleBtn = document.getElementById('toggleVideo');
const videoContainer = document.getElementById('videoContainer');

toggleBtn.onclick = () => {
    if (videoContainer.style.display === "none") {
        videoContainer.style.display = "block";
    } else {
        videoContainer.style.display = "none";
    }
};
// Update count every second
setInterval(() => {
    fetch("/count")
    .then(response => response.json())
    .then(data => {
        countElem.innerText = data.current_count;
    });
}, 1000);
