document.getElementById('downloadButton').addEventListener('click', function() {
    const url = document.getElementById('urlInput').value;
    const downloadType = document.getElementById('typeSelect').value;
    const quality = document.getElementById('qualitySelect').value;

    if (url.trim() === '') {
        alert('Please enter a valid URL');
        return;
    }

    document.getElementById('progressContainer').classList.remove('hidden');
    document.getElementById('resultContainer').classList.add('hidden');

    fetch('/download', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url, downloadType, quality }),
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('progressText').innerText = 'Download complete!';
        document.getElementById('downloadProgress').value = 100;
        document.getElementById('downloadLink').href = data.filePath;
        document.getElementById('resultContainer').classList.remove('hidden');
    })
    .catch(error => {
        alert('Error downloading file');
        console.error('Error:', error);
    });
});
